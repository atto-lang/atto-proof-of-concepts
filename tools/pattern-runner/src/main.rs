use oreslang_poc_pattern_runner::{
    discover, execute, protect_report_path, publish_report, Mode, Options, MAX_OUTPUT_BYTES,
};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicI32, Ordering};
use std::time::Duration;

static INTERRUPTED: AtomicI32 = AtomicI32::new(0);

extern "C" fn mark_interrupted(signal: i32) {
    INTERRUPTED.store(signal, Ordering::SeqCst);
}

extern "C" {
    fn signal(signum: i32, handler: extern "C" fn(i32)) -> usize;
}

fn usage() {
    println!(
        "Structural inventory: oreslang-poc-pattern-runner [--root REPO] [--filter-prefix PREFIX] --list\n\
         Execution: oreslang-poc-pattern-runner [--root REPO] --runner-command 'oreslang run {{source}}' \\\n\
         [--filter-prefix PREFIX] [--mode run|compile] [--backend NAME] \\\n\
         [--compiler-revision SHA] [--require-revision] [--timeout SECONDS] \\\n\
         [--max-output-bytes LIMIT] [--allow-stderr] [--report FILE]\n\
         No compiler execution without --runner-command. No shell is implicitly invoked.\n\
         --filter regex is intentionally not implemented; use literal --filter-prefix.\n\
         Reports are caller-labeled, not authenticated native evidence."
    );
}

fn need_value(args: &mut impl Iterator<Item = String>, key: &str) -> Result<String, String> {
    args.next()
        .ok_or_else(|| format!("missing value for {key}"))
}

fn launch() -> Result<i32, String> {
    let mut root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let mut list = false;
    let mut runner_command: Option<String> = None;
    let mut filter_prefix = None;
    let mut report = None;
    let mut backend = String::from("unspecified");
    let mut mode = Mode::Run;
    let mut revision = String::from("unknown");
    let mut require_revision = false;
    let mut timeout = Duration::from_secs(40);
    let mut max_output = 65_536_usize;
    let mut allow_stderr = false;
    let mut args = std::env::args().skip(1);

    while let Some(key) = args.next() {
        match key.as_str() {
            "--help" | "-h" => {
                usage();
                return Ok(0);
            }
            "--root" => root = PathBuf::from(need_value(&mut args, "--root")?),
            "--list" => list = true,
            "--runner-command" => runner_command = Some(need_value(&mut args, "--runner-command")?),
            "--filter-prefix" => filter_prefix = Some(need_value(&mut args, "--filter-prefix")?),
            "--report" => report = Some(PathBuf::from(need_value(&mut args, "--report")?)),
            "--backend" => backend = need_value(&mut args, "--backend")?,
            "--compiler-revision" => revision = need_value(&mut args, "--compiler-revision")?,
            "--require-revision" => require_revision = true,
            "--allow-stderr" => allow_stderr = true,
            "--mode" => {
                mode = match need_value(&mut args, "--mode")?.as_str() {
                    "run" => Mode::Run,
                    "compile" => Mode::Compile,
                    _ => return Err("--mode must be run or compile".into()),
                };
            }
            "--timeout" => {
                let text = need_value(&mut args, "--timeout")?;
                let secs: f64 = text.parse().map_err(|_| "--timeout must be a number")?;
                if !secs.is_finite() || !(0.0..=86_400.0).contains(&secs) || secs == 0.0 {
                    return Err("--timeout must be finite and in (0,86400] seconds".into());
                }
                timeout = Duration::from_secs_f64(secs);
            }
            "--max-output-bytes" => {
                max_output = need_value(&mut args, "--max-output-bytes")?
                    .parse()
                    .map_err(|_| "invalid --max-output-bytes")?;
                if !(1..=MAX_OUTPUT_BYTES).contains(&max_output) {
                    return Err("max output bytes must be 1..16777216".into());
                }
            }
            "--filter" => return Err(
                "regex --filter not supported; use literal --filter-prefix (not parity-complete)"
                    .into(),
            ),
            _ => return Err(format!("unsupported argument: {key}")),
        }
    }
    let root = std::fs::canonicalize(&root)
        .map_err(|error| format!("cannot open repository root: {error}"))?;
    let cases = discover(&root.join("src/patterns"), 90)
        .map_err(|error| format!("STRUCTURAL FAILURE: {error}"))?;
    let selected = cases
        .iter()
        .filter(|case| {
            filter_prefix
                .as_ref()
                .is_none_or(|p: &String| case.name.starts_with(p))
        })
        .collect::<Vec<_>>();
    if selected.is_empty() {
        return Err("no examples match --filter-prefix".into());
    }
    if list {
        if runner_command.is_some() || report.is_some() {
            return Err("--list cannot be combined with --runner-command or --report".into());
        }
        for case in &selected {
            println!("UNVERIFIED {:02} {}", case.number, case.name);
        }
        println!(
            "Inventory: {} of {} examples. NO Oreslang compiler/runtime execution.",
            selected.len(),
            cases.len()
        );
        return Ok(0);
    }
    let command_template = runner_command
        .ok_or("Missing --runner-command; use --list for structural inventory".to_owned())?;
    if let Some(report) = &report {
        protect_report_path(report, &cases)
            .map_err(|error| format!("report alias admission failed: {error}"))?;
    }
    // SAFETY: the handler only stores an integer to a lock-free atomic.
    unsafe {
        let _ = signal(2, mark_interrupted);
        let _ = signal(15, mark_interrupted);
    }
    let options = Options {
        backend,
        mode,
        revision,
        require_revision,
        command_template,
        timeout,
        max_output,
        allow_stderr,
        filter_prefix,
    };
    let evidence = execute(&root, &cases, &options, &INTERRUPTED)
        .map_err(|error| format!("execution admission failed: {error}"))?;
    if let Some(path) = report {
        protect_report_path(&path, &cases)
            .map_err(|error| format!("report aliases a fixture: {error}"))?;
        publish_report(&path, &evidence.to_json())
            .map_err(|error| format!("cannot publish report: {error}"))?;
    }
    for result in &evidence.results {
        println!(
            "{} {}",
            if result.success { "PASS" } else { "FAIL" },
            result.pattern
        );
    }
    println!(
        "Executed {}; passed {}; failed {}; catalog_inputs_unchanged={}; NO_COMPILER_ATTESTATION",
        evidence.results.len(),
        evidence.passed(),
        evidence.selected - evidence.passed(),
        evidence.catalog_unchanged
    );
    match INTERRUPTED.load(Ordering::SeqCst) {
        2 => Ok(130),
        15 => Ok(143),
        _ if evidence.passed_all() => Ok(0),
        _ => Ok(1),
    }
}

fn main() {
    match launch() {
        Ok(exit) => std::process::exit(exit),
        Err(error) => {
            eprintln!("FAIL pattern runner: {error}");
            std::process::exit(2);
        }
    }
}
