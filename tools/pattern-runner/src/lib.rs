//! Bounded POSIX pattern runner. Structural/host evidence only until a real compiler is supplied.
pub mod sha256;

use std::fs::{self, Metadata, OpenOptions};
use std::io::{self, Read, Write};
use std::os::unix::fs::MetadataExt;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::mpsc::{self, RecvTimeoutError, SyncSender};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

pub const MAX_FIXTURE_BYTES: u64 = 4 * 1024 * 1024;
pub const MAX_OUTPUT_BYTES: usize = 16 * 1024 * 1024;

fn invalid(text: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, text.into())
}

fn real_dir(path: &Path) -> io::Result<()> {
    if !fs::symlink_metadata(path)?.file_type().is_dir() {
        return Err(invalid(format!("symlinked/non-directory path: {}", path.display())));
    }
    Ok(())
}

fn regular(path: &Path) -> io::Result<Metadata> {
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_file() {
        return Err(invalid(format!("symlinked/non-regular fixture: {}", path.display())));
    }
    if metadata.len() > MAX_FIXTURE_BYTES {
        return Err(invalid(format!("oversized fixture: {}", path.display())));
    }
    Ok(metadata)
}

fn read_fixture(path: &Path) -> io::Result<Vec<u8>> {
    // Check both the directory entry and the *opened descriptor*. This makes
    // an inode replacement during open fail rather than trusting only lstat.
    let before = regular(path)?;
    let mut file = fs::File::open(path)?;
    let opened = file.metadata()?;
    if !opened.file_type().is_file()
        || opened.dev() != before.dev()
        || opened.ino() != before.ino()
        || opened.mode() != before.mode()
        || opened.len() != before.len()
    {
        return Err(invalid(format!("fixture replaced during open: {}", path.display())));
    }
    let mut data = Vec::new();
    file.by_ref().take(MAX_FIXTURE_BYTES + 1).read_to_end(&mut data)?;
    if data.len() as u64 > MAX_FIXTURE_BYTES {
        return Err(invalid(format!("oversized fixture: {}", path.display())));
    }
    let after_open = file.metadata()?;
    let after_path = regular(path)?;
    if after_open.dev() != before.dev()
        || after_open.ino() != before.ino()
        || after_open.mode() != before.mode()
        || after_open.len() != before.len()
        || after_path.dev() != before.dev()
        || after_path.ino() != before.ino()
        || after_path.mode() != before.mode()
        || after_path.len() != before.len()
        || data.len() as u64 != before.len()
    {
        return Err(invalid(format!("fixture mutated during read: {}", path.display())));
    }
    Ok(data)
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Fingerprint {
    pub digest: String,
    dev: u64,
    ino: u64,
    mode: u32,
    len: u64,
}

pub fn fingerprint(path: &Path) -> io::Result<Fingerprint> {
    let metadata = regular(path)?;
    let data = read_fixture(path)?;
    let after = regular(path)?;
    if metadata.dev() != after.dev()
        || metadata.ino() != after.ino()
        || metadata.mode() != after.mode()
        || metadata.len() != after.len()
        || data.len() as u64 != metadata.len()
    {
        return Err(invalid("fixture mutated while being fingerprinted"));
    }
    Ok(Fingerprint {
        digest: sha256::hex(&data),
        dev: metadata.dev(),
        ino: metadata.ino(),
        mode: metadata.mode(),
        len: metadata.len(),
    })
}

pub fn unchanged(path: &Path, pinned: &Fingerprint) -> bool {
    fingerprint(path).is_ok_and(|now| &now == pinned)
}

#[derive(Clone)]
pub struct Case {
    pub number: usize,
    pub name: String,
    pub source: PathBuf,
    pub oracle: PathBuf,
    pub expected: Vec<u8>,
    pub source_fp: Fingerprint,
    pub oracle_fp: Fingerprint,
}

fn numbered(name: &str) -> Option<usize> {
    let b = name.as_bytes();
    if b.len() < 4 || !b[0].is_ascii_digit() || !b[1].is_ascii_digit() || b[2] != b'-' {
        return None;
    }
    Some(usize::from(b[0] - b'0') * 10 + usize::from(b[1] - b'0'))
}

pub fn discover(patterns: &Path, expected_count: usize) -> io::Result<Vec<Case>> {
    real_dir(patterns)?;
    let mut cases = Vec::new();
    for entry in fs::read_dir(patterns)? {
        let entry = entry?;
        let name = entry
            .file_name()
            .into_string()
            .map_err(|_| invalid("non-UTF-8 pattern directory name"))?;
        let Some(number) = numbered(&name) else { continue };
        real_dir(&entry.path())?;
        let source = entry.path().join("example.ores");
        let oracle = entry.path().join("expected.stdout");
        let source_fp = fingerprint(&source)?;
        let oracle_fp = fingerprint(&oracle)?;
        let expected = format!("PASS:{number}\n").into_bytes();
        if read_fixture(&oracle)? != expected {
            return Err(invalid(format!("{name}: mismatched exact stdout oracle")));
        }
        let body = String::from_utf8(read_fixture(&source)?)
            .map_err(|_| invalid(format!("{name}: non-UTF-8 pattern source")))?;
        if body.matches('{').count() != body.matches('}').count()
            || body.matches("pub routine main(").count()
                + body.matches("pub async routine main(").count() != 1
            || !body.contains(&format!("PASS:{number}"))
            || !body.contains(&format!("FAIL:{number}:"))
        {
            return Err(invalid(format!("{name}: structural entrypoint/marker mismatch")));
        }
        cases.push(Case {
            number, name, source, oracle, expected, source_fp, oracle_fp,
        });
    }
    cases.sort_by_key(|item| item.number);
    if cases.len() != expected_count
        || cases.iter().enumerate().any(|(index, case)| case.number != index + 1)
    {
        return Err(invalid(format!(
            "expected {expected_count} contiguous numbered patterns starting at 01"
        )));
    }
    Ok(cases)
}

pub fn protect_report_path(path: &Path, cases: &[Case]) -> io::Result<()> {
    let resolved = if path.exists() || fs::symlink_metadata(path).is_ok() {
        fs::canonicalize(path)?
    } else {
        let parent = path.parent().filter(|p| !p.as_os_str().is_empty()).unwrap_or(Path::new("."));
        fs::canonicalize(parent)?.join(
            path.file_name().ok_or_else(|| invalid("invalid report file name"))?,
        )
    };
    // The report must never replace another catalog entry (including READMEs),
    // not merely avoid the two executable fixtures.
    let destination_parent = path.parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    let destination = fs::canonicalize(destination_parent)?.join(
        path.file_name().ok_or_else(|| invalid("missing report filename"))?,
    );
    let patterns_root = fs::canonicalize(
        cases.first().ok_or_else(|| invalid("empty catalog"))?
            .source.parent().ok_or_else(|| invalid("missing pattern parent"))?
            .parent().ok_or_else(|| invalid("missing catalog root"))?,
    )?;
    if destination.starts_with(&patterns_root) {
        return Err(invalid("reports may not be written inside the pattern catalog"));
    }
    let existing = fs::metadata(path).ok();
    for case in cases {
        for fixture in [&case.source, &case.oracle] {
            if resolved == fs::canonicalize(fixture)? {
                return Err(invalid("report path aliases source/oracle"));
            }
            if let Some(existing) = &existing {
                let protected = fs::metadata(fixture)?;
                if existing.dev() == protected.dev() && existing.ino() == protected.ino() {
                    return Err(invalid("report hardlink aliases source/oracle"));
                }
            }
        }
    }
    Ok(())
}

/// Minimal POSIX-style argument tokenization (quotes and escapes, NO implicit shell).
pub fn parse_argv(input: &str) -> io::Result<Vec<String>> {
    let mut tokens = Vec::new();
    let mut token = String::new();
    let mut active = false;
    let mut quote: Option<char> = None;
    let mut iter = input.chars();
    while let Some(c) = iter.next() {
        match (quote, c) {
            (Some('\''), '\'') => quote = None,
            (Some('\''), _) => token.push(c),
            (Some('"'), '"') => quote = None,
            (Some('"'), '\\') => {
                let next = iter.next().ok_or_else(|| invalid("trailing command escape"))?;
                // POSIX double-quoted backslashes only escape $, backtick,
                // a double quote, a backslash, or a line continuation.
                if matches!(next, '$' | '`' | '"' | '\\') {
                    token.push(next);
                } else if next != '\n' {
                    token.push('\\');
                    token.push(next);
                }
            }
            (Some('"'), _) => token.push(c),
            (None, '\'') => { quote = Some('\''); active = true; }
            (None, '"') => { quote = Some('"'); active = true; }
            (None, '\\') => {
                token.push(iter.next().ok_or_else(|| invalid("trailing command escape"))?);
                active = true;
            }
            (None, c) if c.is_whitespace() => {
                if active {
                    tokens.push(std::mem::take(&mut token));
                    active = false;
                }
            }
            (None, c) => { token.push(c); active = true; }
        }
    }
    if quote.is_some() {
        return Err(invalid("unterminated runner command quote"));
    }
    if active {
        tokens.push(token);
    }
    if tokens.is_empty()
        || tokens.iter().map(|t| t.matches("{source}").count()).sum::<usize>() != 1
    {
        return Err(invalid("runner argv must contain exactly one {source} placeholder"));
    }
    Ok(tokens)
}

#[derive(Debug)]
pub struct BoundedOutcome {
    pub exit_code: Option<i32>,
    pub stdout: Vec<u8>,
    pub stderr: Vec<u8>,
    pub truncated: bool,
    pub error: Option<&'static str>,
}

enum PipeEvent {
    Chunk(usize, Vec<u8>),
    End,
    ReadError,
}

fn read_pipe(mut reader: impl Read + Send + 'static, stream: usize, tx: SyncSender<PipeEvent>) {
    // Deliberately detach reader threads: joining could hang if a malicious
    // detached grandchild keeps an inherited pipe open after group teardown.
    // Dropping the receiver at return wakes blocked channel senders.
    let _ = thread::spawn(move || {
        let mut buffer = [0_u8; 4096];
        loop {
            match reader.read(&mut buffer) {
                Ok(0) => { let _ = tx.send(PipeEvent::End); return; }
                Ok(n) => {
                    if tx.send(PipeEvent::Chunk(stream, buffer[..n].to_vec())).is_err() {
                        return;
                    }
                }
                Err(_) => { let _ = tx.send(PipeEvent::ReadError); return; }
            }
        }
    });
}

extern "C" {
    fn kill(pid: i32, signal: i32) -> i32;
}

/// Linux waitid(WNOWAIT) observes child exit without reaping its PID.
/// Keeping the leader unreaped until after killpg avoids signaling a recycled
/// process group ID. This implementation intentionally fails closed elsewhere.
/// siginfo_t is a 128-byte Linux ABI object, aligned at least as strictly as
/// the platform siginfo_t (8 bytes on common supported 64-bit Linux ABIs).
#[cfg(target_os = "linux")]
fn exited_but_unreaped(pid: u32) -> io::Result<bool> {
    #[repr(C, align(16))]
    struct SigInfo([u8; 128]);
    extern "C" {
        fn waitid(idtype: i32, id: u32, info: *mut std::ffi::c_void, options: i32) -> i32;
    }
    const P_PID: i32 = 1;
    const WNOHANG: i32 = 1;
    const WEXITED: i32 = 4;
    const WNOWAIT: i32 = 0x0100_0000;
    let mut info = SigInfo([0; 128]);
    // SAFETY: waitid writes a siginfo_t to a 128-byte, 16-byte-aligned buffer.
    // P_PID is restricted to the child PID owned by this Child handle.
    let outcome = unsafe {
        waitid(
            P_PID,
            pid,
            &mut info as *mut _ as *mut std::ffi::c_void,
            WEXITED | WNOHANG | WNOWAIT,
        )
    };
    if outcome != 0 {
        return Err(io::Error::last_os_error());
    }
    // si_signo is the first C int in Linux siginfo_t. Zero means WNOHANG
    // found no exited child. The buffer is zero-initialized for old kernels.
    let signo = i32::from_ne_bytes(info.0[..4].try_into().expect("four signal bytes"));
    Ok(signo != 0)
}

#[cfg(not(target_os = "linux"))]
fn exited_but_unreaped(_pid: u32) -> io::Result<bool> {
    Err(invalid("non-reaping group-safe child wait is supported on Linux only"))
}

/// Group-wide termination. POSIX group leader was established with process_group(0).
fn kill_group(pid: u32) {
    // SAFETY: negative PID addresses only the new child process group.
    unsafe { let _ = kill(-(pid as i32), 9); }
}

/// Child stdout/stderr are drained concurrently through a capacity-4 channel.
/// This bounds queued data even if a guest floods a pipe. Detached descendants
/// that create a new session are NOT sandboxed or guaranteed to be terminated.
pub fn bounded_run(
    argv: &[String],
    cwd: &Path,
    timeout: Duration,
    max_bytes: usize,
    cancellation: &AtomicI32,
) -> io::Result<BoundedOutcome> {
    if argv.is_empty() || max_bytes == 0 || max_bytes > MAX_OUTPUT_BYTES || timeout.is_zero() {
        return Err(invalid("invalid bounded runner arguments"));
    }
    if cancellation.load(Ordering::SeqCst) != 0 {
        return Ok(BoundedOutcome {
            exit_code: None, stdout: vec![], stderr: vec![],
            truncated: false, error: Some("cancelled"),
        });
    }
    let mut command = Command::new(&argv[0]);
    command.args(&argv[1..])
        .current_dir(cwd)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .process_group(0);
    let mut child = command.spawn()?;
    let child_pid = child.id();
    let (tx, rx) = mpsc::sync_channel(4);
    read_pipe(child.stdout.take().ok_or_else(|| invalid("stdout pipe missing"))?, 0, tx.clone());
    read_pipe(child.stderr.take().ok_or_else(|| invalid("stderr pipe missing"))?, 1, tx);
    let deadline = Instant::now() + timeout;
    let mut output: [Vec<u8>; 2] = [Vec::new(), Vec::new()];
    let mut ended = 0_usize;
    let mut truncated = false;
    let mut error = None;
    loop {
        if cancellation.load(Ordering::SeqCst) != 0 {
            error = Some("cancelled");
            break;
        }
        if Instant::now() >= deadline {
            error = Some("timeout");
            break;
        }
        let exited = match exited_but_unreaped(child_pid) {
            Ok(exited) => exited,
            Err(_) => {
                error = Some("non-reaping child status poll error");
                break;
            }
        };
        if ended == 2 && exited {
            break;
        }
        let remaining = deadline.saturating_duration_since(Instant::now());
        match rx.recv_timeout(remaining.min(Duration::from_millis(25))) {
            Ok(PipeEvent::Chunk(index, bytes)) => {
                let available = max_bytes.saturating_sub(output[index].len());
                output[index].extend_from_slice(&bytes[..bytes.len().min(available)]);
                if bytes.len() > available {
                    truncated = true;
                    error = Some("output limit");
                    break;
                }
            }
            Ok(PipeEvent::End) => ended += 1,
            Ok(PipeEvent::ReadError) => {
                error = Some("pipe read error");
                break;
            }
            Err(RecvTimeoutError::Timeout) => {}
            Err(RecvTimeoutError::Disconnected) if ended == 2 => {}
            Err(RecvTimeoutError::Disconnected) => {
                error = Some("pipe reader disconnected");
                break;
            }
        }
    };
    // Always retire the entire process group, including after a zero-exit
    // guest. A runner may fork a background grandchild that closes its pipe
    // handles, allowing EOF and a false "clean shutdown" while it survives.
    // This is best-effort process-group containment, NOT an OS sandbox:
    // a malicious guest can still setsid()/detach outside the group.
    kill_group(child_pid);
    if error.is_some() {
        // A failed or raced group signal must not leave the direct child
        // running while wait() blocks indefinitely.
        let _ = child.kill();
    }
    // The leader has intentionally NOT been reaped at this point. Therefore
    // child_pid cannot be recycled into an unrelated process group before
    // the group signal above. Reap only after that signal is sent.
    let final_status = child.wait()?;
    Ok(BoundedOutcome {
        exit_code: if error.is_none() { final_status.code() } else { None },
        stdout: std::mem::take(&mut output[0]),
        stderr: std::mem::take(&mut output[1]),
        truncated,
        error,
    })
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Run,
    Compile,
}

impl Mode {
    pub fn label(self) -> &'static str {
        match self { Self::Run => "run", Self::Compile => "compile" }
    }
}

pub struct Options {
    pub backend: String,
    pub mode: Mode,
    pub revision: String,
    pub require_revision: bool,
    pub command_template: String,
    pub timeout: Duration,
    pub max_output: usize,
    pub allow_stderr: bool,
    pub filter_prefix: Option<String>,
}

pub struct CaseResult {
    pub pattern: String,
    pub source_sha256: String,
    pub oracle_sha256: String,
    pub inputs_unchanged: bool,
    pub success: bool,
    pub exit_code: Option<i32>,
    pub stdout: Vec<u8>,
    pub stderr: Vec<u8>,
    pub error: Option<String>,
    pub output_truncated: bool,
}

pub struct Report {
    pub backend: String,
    pub mode: &'static str,
    pub revision: String,
    pub require_revision: bool,
    pub command_digest: String,
    pub selected: usize,
    pub total: usize,
    pub catalog_unchanged: bool,
    pub allow_stderr: bool,
    pub max_output: usize,
    pub results: Vec<CaseResult>,
}

impl Report {
    pub fn passed(&self) -> usize {
        self.results.iter().filter(|r| r.success).count()
    }

    pub fn passed_all(&self) -> bool {
        self.catalog_unchanged && self.passed() == self.selected && self.selected > 0
    }
}

pub fn execute(
    root: &Path,
    cases: &[Case],
    options: &Options,
    cancellation: &AtomicI32,
) -> io::Result<Report> {
    if options.timeout.is_zero() || options.max_output == 0 || options.max_output > MAX_OUTPUT_BYTES {
        return Err(invalid("timeout/output limit out of range"));
    }
    if options.require_revision && !is_sha(&options.revision) {
        return Err(invalid("compiler revision must be 40 hexadecimal digits"));
    }
    let template = parse_argv(&options.command_template)?;
    let selected = cases.iter().filter(|case| {
        options.filter_prefix.as_ref().is_none_or(|prefix| case.name.starts_with(prefix))
    }).collect::<Vec<_>>();
    if selected.is_empty() {
        return Err(invalid("pattern selection contains no cases"));
    }
    let mut report = Report {
        backend: options.backend.clone(),
        mode: options.mode.label(),
        revision: options.revision.clone(),
        require_revision: options.require_revision,
        command_digest: sha256::hex(options.command_template.as_bytes()),
        selected: selected.len(),
        total: cases.len(),
        catalog_unchanged: true,
        allow_stderr: options.allow_stderr,
        max_output: options.max_output,
        results: Vec::with_capacity(selected.len()),
    };
    for case in selected {
        let stable_before = unchanged(&case.source, &case.source_fp)
            && unchanged(&case.oracle, &case.oracle_fp);
        let mut result = CaseResult {
            pattern: case.name.clone(),
            source_sha256: case.source_fp.digest.clone(),
            oracle_sha256: case.oracle_fp.digest.clone(),
            inputs_unchanged: stable_before,
            success: false,
            exit_code: None,
            stdout: vec![], stderr: vec![], error: None, output_truncated: false,
        };
        if !stable_before {
            result.error = Some("fixture changed before invocation".to_owned());
        } else {
            let source = fs::canonicalize(&case.source)?;
            let argv = template.iter().map(|part| {
                part.replace("{source}", &source.to_string_lossy())
            }).collect::<Vec<_>>();
            match bounded_run(&argv, root, options.timeout, options.max_output, cancellation) {
                Ok(outcome) => {
                    result.exit_code = outcome.exit_code;
                    result.stdout = outcome.stdout;
                    result.stderr = outcome.stderr;
                    result.output_truncated = outcome.truncated;
                    result.error = outcome.error.map(str::to_owned);
                    result.inputs_unchanged = unchanged(&case.source, &case.source_fp)
                        && unchanged(&case.oracle, &case.oracle_fp);
                    result.success = result.error.is_none()
                        && result.exit_code == Some(0)
                        && result.inputs_unchanged
                        && !result.output_truncated
                        && (options.mode == Mode::Compile
                            || options.allow_stderr
                            || result.stderr.is_empty())
                        && (options.mode == Mode::Compile || result.stdout == case.expected);
                }
                Err(err) => {
                    result.error = Some(format!("runner I/O error: {:?}", err.kind()));
                    result.inputs_unchanged = unchanged(&case.source, &case.source_fp)
                        && unchanged(&case.oracle, &case.oracle_fp);
                }
            }
        }
        let stop = result.error.as_deref() == Some("cancelled");
        report.results.push(result);
        if stop {
            break;
        }
    }
    report.catalog_unchanged = cases.iter().all(|case| {
        unchanged(&case.source, &case.source_fp) && unchanged(&case.oracle, &case.oracle_fp)
    });
    if !report.catalog_unchanged {
        for item in &mut report.results {
            let Some(case) = cases.iter().find(|c| c.name == item.pattern) else { continue };
            if !unchanged(&case.source, &case.source_fp)
                || !unchanged(&case.oracle, &case.oracle_fp)
            {
                item.inputs_unchanged = false;
                item.success = false;
            }
        }
    }
    Ok(report)
}

pub fn is_sha(s: &str) -> bool {
    s.len() == 40 && s.bytes().all(|ch| ch.is_ascii_hexdigit())
}

fn json_quote(s: &str) -> String {
    let mut result = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c < ' ' => result.push_str(&format!("\\u{:04x}", c as u32)),
            c => result.push(c),
        }
    }
    result.push('"');
    result
}

impl Report {
    /// JSON is escaped manually to keep the harness dependency-free.
    /// Compiler/source revision labels are still caller-supplied, not attested.
    pub fn to_json(&self) -> String {
        use std::fmt::Write as _;
        let mut output = String::new();
        let _ = writeln!(output, "{{");
        let _ = writeln!(output, "  \"backend\": {},", json_quote(&self.backend));
        let _ = writeln!(output, "  \"mode\": {},", json_quote(self.mode));
        let _ = writeln!(output, "  \"compiler_revision\": {},", json_quote(&self.revision));
        let _ = writeln!(output, "  \"provenance\": \"caller-supplied labels; verify independently\",");
        let _ = writeln!(output, "  \"runner_command_sha256\": {},", json_quote(&self.command_digest));
        let _ = writeln!(output, "  \"revision_format_verified\": {},", self.require_revision);
        let _ = writeln!(output, "  \"selected\": {},", self.selected);
        let _ = writeln!(output, "  \"inventory_total\": {},", self.total);
        let _ = writeln!(output, "  \"complete_catalog\": {},", self.selected == self.total);
        let _ = writeln!(output, "  \"catalog_inputs_unchanged\": {},", self.catalog_unchanged);
        let _ = writeln!(output, "  \"output_oracle_matched\": {},", self.mode == "run" && self.passed_all());
        let _ = writeln!(output, "  \"allow_stderr\": {},", self.allow_stderr);
        let _ = writeln!(output, "  \"max_output_bytes\": {},", self.max_output);
        let _ = writeln!(output, "  \"passed\": {},", self.passed());
        let _ = writeln!(output, "  \"failed\": {},", self.selected - self.passed());
        let _ = writeln!(output, "  \"results\": [");
        for (index, result) in self.results.iter().enumerate() {
            let _ = writeln!(output, "    {{");
            let _ = writeln!(output, "      \"pattern\": {},", json_quote(&result.pattern));
            let _ = writeln!(output, "      \"source_sha256\": {},", json_quote(&result.source_sha256));
            let _ = writeln!(output, "      \"oracle_sha256\": {},", json_quote(&result.oracle_sha256));
            let _ = writeln!(output, "      \"inputs_unchanged\": {},", result.inputs_unchanged);
            let _ = writeln!(output, "      \"success\": {},", result.success);
            match result.exit_code {
                Some(code) => { let _ = writeln!(output, "      \"exit_code\": {code},"); }
                None => { let _ = writeln!(output, "      \"exit_code\": null,"); }
            }
            let _ = writeln!(output, "      \"output_truncated\": {},", result.output_truncated);
            let _ = writeln!(output, "      \"stdout_bytes\": {},", result.stdout.len());
            let _ = writeln!(output, "      \"stderr_bytes\": {},", result.stderr.len());
            // Never persist raw subprocess output in portable JSON receipts:
            // a compiler/runner may echo argv, credentials, environment,
            // customer input or source bytes into stdout/stderr.
            // Lengths and hashes preserve comparison handles without
            // accidentally placing plaintext diagnostics in CI artifacts.
            let _ = writeln!(output, "      \"stdout_sha256\": {},", json_quote(&sha256::hex(&result.stdout)));
            let _ = writeln!(output, "      \"stderr_sha256\": {},", json_quote(&sha256::hex(&result.stderr)));
            let _ = writeln!(output, "      \"stdout_redacted\": true,");
            let _ = writeln!(output, "      \"stderr_redacted\": true,");
            match &result.error {
                Some(error) => { let _ = writeln!(output, "      \"error\": {}", json_quote(error)); }
                None => { let _ = writeln!(output, "      \"error\": null"); }
            }
            let _ = writeln!(output, "    }}{}", if index + 1 == self.results.len() { "" } else { "," });
        }
        let _ = writeln!(output, "  ]");
        let _ = writeln!(output, "}}");
        output
    }
}

/// Atomically publish evidence in the same directory. Renaming a temporary
/// file never follows a late symlink in the destination itself.
pub fn publish_report(path: &Path, json: &str) -> io::Result<()> {
    use std::os::unix::fs::OpenOptionsExt;
    let parent = path.parent().filter(|p| !p.as_os_str().is_empty()).unwrap_or(Path::new("."));
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH)
        .map_err(|_| invalid("system clock before epoch"))?
        .as_nanos();
    for attempt in 0..16 {
        let temporary = parent.join(format!(
            ".oreslang-pattern-report-{}-{nanos}-{attempt}.tmp",
            std::process::id()
        ));
        match OpenOptions::new().write(true).create_new(true).mode(0o600).open(&temporary) {
            Ok(mut file) => {
                let result = (|| {
                    file.write_all(json.as_bytes())?;
                    file.sync_all()?;
                    fs::rename(&temporary, path)?;
                    Ok(())
                })();
                if result.is_err() {
                    let _ = fs::remove_file(&temporary);
                }
                return result;
            }
            Err(error) if error.kind() == io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error),
        }
    }
    Err(invalid("unable to allocate unique evidence report file"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicI32;

    static NEXT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

    struct Temp(PathBuf);
    impl Temp {
        fn new() -> Self {
            let id = NEXT.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir().join(format!(
                "oreslang-pattern-rust-test-{}-{id}", std::process::id()
            ));
            fs::create_dir(&path).unwrap();
            Self(path)
        }
        fn root(&self) -> &Path { &self.0 }
        fn cases(&self) -> Vec<Case> {
            discover(&self.0, 2).unwrap()
        }
        fn setup_cases(&self) {
            for n in 1..=2 {
                let case = self.0.join(format!("{n:02}-fixture"));
                fs::create_dir(&case).unwrap();
                fs::write(
                    case.join("example.ores"),
                    format!("pub routine main() {{ \"PASS:{n}\"; \"FAIL:{n}:x\"; }}"),
                ).unwrap();
                fs::write(case.join("expected.stdout"), format!("PASS:{n}\n")).unwrap();
            }
        }
    }
    impl Drop for Temp {
        fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); }
    }

    fn options(command_template: &str) -> Options {
        Options {
            backend: "synthetic-host".into(),
            mode: Mode::Run,
            revision: "unknown".into(),
            require_revision: false,
            command_template: command_template.into(),
            timeout: Duration::from_millis(500),
            max_output: 64,
            allow_stderr: false,
            filter_prefix: Some("01-".into()),
        }
    }

    #[test]
    fn inventory_and_exact_oracles() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        assert_eq!(cases.len(), 2);
        assert_eq!(cases[0].expected, b"PASS:1\n");
        assert_eq!(cases[0].source_fp.digest.len(), 64);
    }

    #[test]
    fn missing_oracle_and_symlinked_source_fail() {
        let dir = Temp::new();
        dir.setup_cases();
        fs::remove_file(dir.root().join("01-fixture/expected.stdout")).unwrap();
        assert!(discover(dir.root(), 2).is_err());
        let dir = Temp::new();
        dir.setup_cases();
        let source = dir.root().join("01-fixture/example.ores");
        let real = dir.root().join("real.ores");
        fs::rename(&source, &real).unwrap();
        std::os::unix::fs::symlink(&real, &source).unwrap();
        assert!(discover(dir.root(), 2).is_err());
    }

    #[test]
    fn reject_missing_cases_and_wrong_stdout() {
        let dir = Temp::new();
        dir.setup_cases();
        assert!(discover(dir.root(), 90).is_err());
        fs::write(dir.root().join("02-fixture/expected.stdout"), b"PASS:1\n").unwrap();
        assert!(discover(dir.root(), 2).is_err());
    }

    #[test]
    fn quoted_argv_parsing_never_invokes_a_shell_implicitly() {
        let parsed = parse_argv("runner --flag 'arg with spaces' \"another arg\" {source}").unwrap();
        assert_eq!(parsed, vec!["runner", "--flag", "arg with spaces", "another arg", "{source}"]);
        assert!(parse_argv("runner 'oops {source}").is_err());
        assert!(parse_argv("runner --foo").is_err());
        assert!(parse_argv("runner {source} {source}").is_err());
    }

    #[test]
    fn quoted_argv_preserves_literal_backslash_sequences() {
        let argv = parse_argv(r#"sh -c "printf 'PASS:1\n'" {source}"#).unwrap();
        assert_eq!(argv, vec!["sh", "-c", "printf 'PASS:1\\n'", "{source}"]);
        let escaped_quote = parse_argv(r#"compiler --opt "quoted\"value" {source}"#).unwrap();
        assert_eq!(escaped_quote[2], "quoted\"value");
    }

    #[test]
    fn fingerprints_detect_in_place_and_inode_mutation() {
        let dir = Temp::new();
        dir.setup_cases();
        let case = dir.cases().remove(0);
        assert!(unchanged(&case.source, &case.source_fp));
        fs::write(&case.source, "changed").unwrap();
        assert!(!unchanged(&case.source, &case.source_fp));
    }

    #[test]
    fn same_bytes_different_inode_is_not_original_fixture() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let pinned = &cases[0].source_fp;
        let source = &cases[0].source;
        let clone = dir.root().join("replacement.ores");
        fs::write(&clone, fs::read(source).unwrap()).unwrap();
        fs::rename(&clone, source).unwrap();
        assert!(!unchanged(source, pinned));
    }

    #[test]
    fn report_hardlink_alias_rejected() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        // Deliberately place the alias OUTSIDE the pattern root to exercise
        // inode hardlink detection instead of the catalog-path rejection.
        let report = dir.root().parent().unwrap().join(format!(
            "oreslang-pattern-hardlink-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::hard_link(&cases[0].oracle, &report).unwrap();
        assert_eq!(
            fs::metadata(&report).unwrap().ino(),
            fs::metadata(&cases[0].oracle).unwrap().ino()
        );
        assert!(protect_report_path(&report, &cases).is_err());
        assert_eq!(fs::read(&cases[0].oracle).unwrap(), b"PASS:1\\n");
        fs::remove_file(report).unwrap();
    }

    #[test]
    fn generated_json_does_not_contain_command_secret() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let command = "sh -c 'printf PASS:1' --secret=PRIVATE_SENTINEL {source}";
        let mut opts = options(command);
        opts.mode = Mode::Compile;
        let report = execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap();
        let json = report.to_json();
        assert!(!json.contains("PRIVATE_SENTINEL"));
        assert_eq!(report.command_digest.len(), 64);
        assert!(json.contains("runner_command_sha256"));
        assert!(json.contains("caller-supplied"));
    }

    #[test]
    fn raw_subprocess_credentials_never_enter_json_receipts() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let mut opts = options("sh -c 'printf SENSITIVE_STDOUT; printf SENSITIVE_STDERR >&2' {source}");
        opts.mode = Mode::Compile;
        let report = execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap();
        let json = report.to_json();
        assert!(json.contains("\"stdout_sha256\""));
        assert!(json.contains("\"stderr_sha256\""));
        assert!(json.contains("\"stdout_redacted\": true"));
        assert!(!json.contains("SENSITIVE_STDOUT"));
        assert!(!json.contains("SENSITIVE_STDERR"));
        assert_eq!(report.results[0].stdout, b"SENSITIVE_STDOUT");
        assert_eq!(report.results[0].stderr, b"SENSITIVE_STDERR");
    }

    #[test]
    fn invalid_revision_and_zero_max_output_fail_closed() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let mut opts = options("sh -c 'exit 0' {source}");
        opts.require_revision = true;
        assert!(execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).is_err());
        opts.revision = "a".repeat(40);
        opts.max_output = 0;
        assert!(execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).is_err());
    }

    #[test]
    fn exact_stdout_and_stderr_default() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let opts = options("sh -c 'printf \"PASS:1\\n\"' {source}");
        let report = execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap();
        assert!(report.passed_all());
        let opts = options("sh -c 'printf \"PASS:2\\n\"' {source}");
        assert!(!execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
        let opts = options("sh -c 'printf \"PASS:1\\n\"; echo diagnostic >&2' {source}");
        assert!(!execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
    }

    #[test]
    fn compile_only_does_not_pretend_to_match_stdout() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let mut opts = options("sh -c 'exit 0' {source}");
        opts.mode = Mode::Compile;
        assert!(execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
        assert!(!execute(dir.root(), &cases, &options("sh -c 'exit 0' {source}"), &AtomicI32::new(0))
            .unwrap().passed_all());
    }

    #[test]
    fn live_output_cap_terminates_producer() {
        let argv = vec!["sh".into(), "-c".into(), "while :; do printf 1234567890; done".into()];
        let out = bounded_run(&argv, Path::new("."), Duration::from_secs(1), 32, &AtomicI32::new(0)).unwrap();
        assert_eq!(out.error, Some("output limit"));
        assert!(out.truncated);
        assert!(out.stdout.len() <= 32);
    }

    #[test]
    fn successful_leader_exit_does_not_leave_background_group_child() {
        let dir = Temp::new();
        let marker = dir.root().join("escaped-descendant");
        // A background process closes the stdout/stderr pipes, so a naive
        // runner sees clean EOF and a zero exit while the child still runs.
        // The marker is written only if the process survives group retirement.
        let script = format!(
            "(sleep 0.35; printf leaked > {}) >/dev/null 2>&1 & printf 'PASS:1\\n'",
            marker.display()
        );
        let argv = vec!["sh".into(), "-c".into(), script];
        let result = bounded_run(
            &argv, dir.root(), Duration::from_secs(2), 64, &AtomicI32::new(0)
        ).unwrap();
        assert_eq!(result.exit_code, Some(0));
        assert_eq!(result.stdout, b"PASS:1\\n");
        thread::sleep(Duration::from_millis(550));
        assert!(!marker.exists(), "background process escaped after successful leader exit");
    }

    #[cfg(target_os = "linux")]
    #[test]
    fn non_reaping_exit_poll_keeps_leader_waitable() {
        let mut child = Command::new("sh")
            .args(["-c", "exit 0"])
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .process_group(0)
            .spawn()
            .unwrap();
        let pid = child.id();
        let start = Instant::now();
        loop {
            if exited_but_unreaped(pid).unwrap() {
                break;
            }
            assert!(
                start.elapsed() < Duration::from_secs(2),
                "waitid(WNOWAIT) never observed child exit"
            );
            thread::sleep(Duration::from_millis(5));
        }
        // A non-reaping poll must leave the child reapable, otherwise the
        // numeric process-group ID might be recycled before teardown.
        kill_group(pid);
        assert_eq!(child.wait().unwrap().code(), Some(0));
    }

    #[test]
    fn deadline_kills_slow_child() {
        let argv = vec!["sh".into(), "-c".into(), "sleep 3".into()];
        let started = Instant::now();
        let out = bounded_run(&argv, Path::new("."), Duration::from_millis(70), 64, &AtomicI32::new(0)).unwrap();
        assert_eq!(out.error, Some("timeout"));
        assert!(started.elapsed() < Duration::from_secs(2));
    }

    #[test]
    fn explicit_cancellation_stops_running_child() {
        let argv = vec!["sh".into(), "-c".into(), "sleep 3".into()];
        let cancelled = AtomicI32::new(0);
        thread::scope(|scope| {
            scope.spawn(|| {
                thread::sleep(Duration::from_millis(40));
                cancelled.store(15, Ordering::SeqCst);
            });
            let out = bounded_run(&argv, Path::new("."), Duration::from_secs(2), 64, &cancelled).unwrap();
            assert_eq!(out.error, Some("cancelled"));
        });
    }

    #[test]
    fn unselected_mutation_fails_global_run() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let path = dir.root().join("02-fixture/example.ores");
        let command = format!(
            "sh -c 'printf tampered > {}; printf \"PASS:1\\n\"' {{source}}",
            path.display()
        );
        let report = execute(dir.root(), &cases, &options(&command), &AtomicI32::new(0)).unwrap();
        assert!(!report.catalog_unchanged);
        assert!(!report.passed_all());
    }

    #[test]
    fn report_cannot_overwrite_pattern_readme_or_create_inside_catalog() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let readme = dir.root().join("01-fixture/README.md");
        fs::write(&readme, "Do not overwrite").unwrap();
        assert!(protect_report_path(&readme, &cases).is_err());
        assert!(protect_report_path(&dir.root().join("02-fixture/new-report.json"), &cases).is_err());
        assert_eq!(fs::read(&readme).unwrap(), b"Do not overwrite");
    }

    #[test]
    fn nonzero_exit_and_stderr_waiver_are_distinct() {
        let dir = Temp::new();
        dir.setup_cases();
        let cases = dir.cases();
        let mut opts = options("sh -c 'printf \"PASS:1\\n\"; exit 7' {source}");
        assert!(!execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
        opts.command_template = "sh -c 'printf \"PASS:1\\n\"; echo diagnostic >&2' {source}".into();
        assert!(!execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
        opts.allow_stderr = true;
        assert!(execute(dir.root(), &cases, &opts, &AtomicI32::new(0)).unwrap().passed_all());
    }

    #[test]
    fn atomic_report_does_not_follow_final_symlink() {
        let dir = Temp::new();
        let protected = dir.root().join("protected");
        fs::write(&protected, b"original").unwrap();
        let link = dir.root().join("evidence.json");
        std::os::unix::fs::symlink(&protected, &link).unwrap();
        publish_report(&link, "{\"test\":true}\n").unwrap();
        assert_eq!(fs::read(&protected).unwrap(), b"original");
        assert_eq!(fs::read_to_string(link).unwrap(), "{\"test\":true}\n");
    }
}
