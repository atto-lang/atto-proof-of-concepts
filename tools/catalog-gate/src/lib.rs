//! Strict, dependency-free structural catalog admission; NOT Oreslang guest CI.
use std::fs;
use std::io;
use std::path::{Path, PathBuf};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Expected {
    pub libraries: usize,
    pub patterns: usize,
    pub library_probes: usize,
}

pub const RELEASE_CATALOG: Expected = Expected {
    libraries: 60,
    patterns: 90,
    library_probes: 32,
};

#[derive(Debug, Eq, PartialEq)]
pub struct Counts {
    pub libraries: usize,
    pub patterns: usize,
    pub library_probes: usize,
}

fn failure(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}

fn regular_file(path: &Path) -> io::Result<()> {
    let metadata = fs::symlink_metadata(path).map_err(|error| {
        failure(format!("missing catalog file {}: {error}", path.display()))
    })?;
    if !metadata.file_type().is_file() {
        return Err(failure(format!(
            "symlinked or non-regular catalog file: {}",
            path.display()
        )));
    }
    Ok(())
}

fn real_directory(path: &Path) -> io::Result<()> {
    let metadata = fs::symlink_metadata(path).map_err(|error| {
        failure(format!("missing catalog directory {}: {error}", path.display()))
    })?;
    if !metadata.file_type().is_dir() {
        return Err(failure(format!(
            "symlinked or non-directory catalog entry: {}",
            path.display()
        )));
    }
    Ok(())
}

fn nonempty_source(path: &Path) -> io::Result<()> {
    regular_file(path)?;
    if fs::read_to_string(path)?.trim().is_empty() {
        return Err(failure(format!("empty catalog source: {}", path.display())));
    }
    Ok(())
}

fn exact_oracle(path: &Path, expected: &str) -> io::Result<()> {
    regular_file(path)?;
    if fs::read(path)? != expected.as_bytes() {
        return Err(failure(format!(
            "invalid exact catalog oracle: {}",
            path.display()
        )));
    }
    Ok(())
}

fn readme(path: &Path) -> io::Result<()> {
    regular_file(path)?;
    let body = fs::read_to_string(path)?;
    if !body.contains("Status:") || !body.contains("##") {
        return Err(failure(format!(
            "missing catalog status/heading: {}",
            path.display()
        )));
    }
    Ok(())
}

fn pattern_number(name: &str) -> Option<usize> {
    let bytes = name.as_bytes();
    if bytes.len() < 4 || !bytes[0].is_ascii_digit() || !bytes[1].is_ascii_digit() || bytes[2] != b'-' {
        return None;
    }
    Some(usize::from(bytes[0] - b'0') * 10 + usize::from(bytes[1] - b'0'))
}

fn catalog_directories(root: &Path, patterns: bool) -> io::Result<Vec<(String, PathBuf)>> {
    real_directory(root)?;
    let mut found = Vec::new();
    for entry in fs::read_dir(root)? {
        let entry = entry?;
        let name = entry.file_name().into_string().map_err(|_| {
            failure(format!("non-UTF-8 catalog entry under {}", root.display()))
        })?;
        let selected = if patterns {
            pattern_number(&name).is_some()
        } else {
            name.starts_with("oreslang-")
        };
        if selected {
            let path = entry.path();
            real_directory(&path)?;
            found.push((name, path));
        }
    }
    found.sort_unstable_by(|a, b| a.0.cmp(&b.0));
    Ok(found)
}

fn fixture_exists(path: &Path) -> io::Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(_) => Ok(true),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error),
    }
}

/// Validate structural layout and exact bytes, without executing any compiler.
/// Catalog root is the repository's `src/` directory.
pub fn validate(root: &Path, expected: Expected) -> io::Result<Counts> {
    real_directory(root)?;
    let libraries = catalog_directories(&root.join("libraries"), false)?;
    let patterns = catalog_directories(&root.join("patterns"), true)?;
    if libraries.len() != expected.libraries {
        return Err(failure(format!(
            "expected {} libraries; found {}",
            expected.libraries,
            libraries.len()
        )));
    }
    if patterns.len() != expected.patterns {
        return Err(failure(format!(
            "expected {} patterns; found {}",
            expected.patterns,
            patterns.len()
        )));
    }
    let mut numbers = patterns
        .iter()
        .map(|(name, _)| pattern_number(name).expect("filtered numeric pattern name"))
        .collect::<Vec<_>>();
    numbers.sort_unstable();
    if numbers != (1..=expected.patterns).collect::<Vec<_>>() {
        return Err(failure(format!(
            "missing, duplicate or out-of-order pattern numbers: {numbers:?}"
        )));
    }
    for (_, directory) in libraries.iter().chain(patterns.iter()) {
        readme(&directory.join("README.md"))?;
    }
    let mut library_probes = 0;
    for (name, directory) in &libraries {
        let source = directory.join("example.ores");
        let oracle = directory.join("expected.stdout");
        if fixture_exists(&source)? || fixture_exists(&oracle)? {
            nonempty_source(&source)?;
            exact_oracle(&oracle, &format!("PASS:{name}\n"))?;
            library_probes += 1;
        }
    }
    if library_probes != expected.library_probes {
        return Err(failure(format!(
            "expected {} library probes; found {library_probes}",
            expected.library_probes
        )));
    }
    for (name, directory) in &patterns {
        let number = pattern_number(name).expect("filtered pattern name");
        nonempty_source(&directory.join("example.ores"))?;
        exact_oracle(&directory.join("expected.stdout"), &format!("PASS:{number}\n"))?;
    }
    for relative in [
        "README.md",
        "libraries/README.md",
        "patterns/README.md",
        "validation/README.md",
    ] {
        regular_file(&root.join(relative))?;
    }
    Ok(Counts {
        libraries: libraries.len(),
        patterns: patterns.len(),
        library_probes,
    })
}
