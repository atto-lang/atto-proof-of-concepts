//! Bounded POSIX pattern runner. Structural/host evidence only until a real compiler is supplied.
pub mod sha256;

use std::ffi::OsStr;
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
    let data = fs::read(path)?;
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
        if fs::read(&oracle)? != expected {
            return Err(invalid(format!("{name}: mismatched exact stdout oracle")));
        }
        let body = fs::read_to_string(&source)?;
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
                token.push(next);
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
    thread::spawn(move || {
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
    let mut command = Command::new(OsStr::new(&argv[0]));
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
    let status = loop {
        if cancellation.load(Ordering::SeqCst) != 0 {
            error = Some("cancelled");
            break None;
        }
        if Instant::now() >= deadline {
            error = Some("timeout");
            break None;
        }
        let status = child.try_wait()?;
        if ended == 2 && status.is_some() {
            break status;
        }
        let remaining = deadline.saturating_duration_since(Instant::now());
        match rx.recv_timeout(remaining.min(Duration::from_millis(25))) {
            Ok(PipeEvent::Chunk(index, bytes)) => {
                let available = max_bytes.saturating_sub(output[index].len());
                output[index].extend_from_slice(&bytes[..bytes.len().min(available)]);
                if bytes.len() > available {
                    truncated = true;
                    error = Some("output limit");
                    break None;
                }
            }
            Ok(PipeEvent::End) => ended += 1,
            Ok(PipeEvent::ReadError) => {
                error = Some("pipe read error");
                break None;
            }
            Err(RecvTimeoutError::Timeout) => {}
            Err(RecvTimeoutError::Disconnected) if ended == 2 => {}
            Err(RecvTimeoutError::Disconnected) => {
                error = Some("pipe reader disconnected");
                break None;
            }
        }
    };
    if error.is_some() {
        kill_group(child_pid);
    }
    let final_status = match status {
        Some(status) => status,
        None => child.wait()?,
    };
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
                    result.error = Some(format!("runner I/O error: {}", err.kind()));
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
