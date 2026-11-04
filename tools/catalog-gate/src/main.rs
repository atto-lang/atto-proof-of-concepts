use oreslang_poc_catalog_gate::{validate, RELEASE_CATALOG};
use std::path::PathBuf;

fn main() {
    let mut args = std::env::args_os().skip(1);
    let root = match (args.next(), args.next(), args.next()) {
        (None, None, None) => PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../src"),
        (Some(flag), Some(root), None) if flag == "--root" => PathBuf::from(root),
        (Some(flag), None, None) if flag == "--help" => {
            println!("Usage: oreslang-poc-catalog-gate [--root <catalog src directory>]");
            return;
        }
        _ => {
            eprintln!("Invalid arguments: use --root <catalog src directory>");
            std::process::exit(2);
        }
    };
    match validate(&root, RELEASE_CATALOG) {
        Ok(counts) => println!(
            "STRUCTURAL_ONLY libraries={} patterns={} library_probes={} NO_GUEST_EXECUTION",
            counts.libraries, counts.patterns, counts.library_probes
        ),
        Err(error) => {
            eprintln!("FAIL structural catalog validation: {error}");
            std::process::exit(1);
        }
    }
}
