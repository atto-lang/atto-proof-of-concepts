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
    let metadata = fs::symlink_metadata(path)
        .map_err(|error| failure(format!("missing catalog file {}: {error}", path.display())))?;
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
        failure(format!(
            "missing catalog directory {}: {error}",
            path.display()
        ))
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
    if bytes.len() < 4
        || !bytes[0].is_ascii_digit()
        || !bytes[1].is_ascii_digit()
        || bytes[2] != b'-'
    {
        return None;
    }
    Some(usize::from(bytes[0] - b'0') * 10 + usize::from(bytes[1] - b'0'))
}

fn catalog_directories(root: &Path, patterns: bool) -> io::Result<Vec<(String, PathBuf)>> {
    real_directory(root)?;
    let mut found = Vec::new();
    for entry in fs::read_dir(root)? {
        let entry = entry?;
        let name = entry
            .file_name()
            .into_string()
            .map_err(|_| failure(format!("non-UTF-8 catalog entry under {}", root.display())))?;
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
        if fixture_exists(&directory.join("example.ores"))? {
            return Err(failure("legacy .ores source forbidden"));
        }
        let source = directory.join("example.atto");
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
        if fixture_exists(&directory.join("example.ores"))? {
            return Err(failure("legacy .ores source forbidden"));
        }
        nonempty_source(&directory.join("example.atto"))?;
        exact_oracle(
            &directory.join("expected.stdout"),
            &format!("PASS:{number}\n"),
        )?;
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};

    static NEXT: AtomicU64 = AtomicU64::new(0);
    const SMALL: Expected = Expected {
        libraries: 2,
        patterns: 2,
        library_probes: 2,
    };

    struct Fixture(PathBuf);

    impl Fixture {
        fn new() -> Self {
            let id = NEXT.fetch_add(1, Ordering::Relaxed);
            let root = std::env::temp_dir()
                .join(format!("oreslang-poc-catalog-{}-{id}", std::process::id()));
            fs::create_dir(&root).expect("fresh test directory");
            for area in ["libraries", "patterns", "validation"] {
                fs::create_dir(root.join(area)).unwrap();
                fs::write(root.join(area).join("README.md"), "# Catalog\n").unwrap();
            }
            fs::write(root.join("README.md"), "# Catalog\n").unwrap();
            for name in ["oreslang-a", "oreslang-b"] {
                let dir = root.join("libraries").join(name);
                fs::create_dir(&dir).unwrap();
                fs::write(dir.join("README.md"), "## Status: planned\n").unwrap();
                fs::write(dir.join("example.atto"), "pub routine main(): void {}\n").unwrap();
                fs::write(dir.join("expected.stdout"), format!("PASS:{name}\n")).unwrap();
            }
            for name in ["01-alpha", "02-beta"] {
                let dir = root.join("patterns").join(name);
                fs::create_dir(&dir).unwrap();
                fs::write(dir.join("README.md"), "## Status: prototype\n").unwrap();
                fs::write(dir.join("example.atto"), "pub routine main(): void {}\n").unwrap();
                fs::write(
                    dir.join("expected.stdout"),
                    format!("PASS:{}\n", pattern_number(name).unwrap()),
                )
                .unwrap();
            }
            Self(root)
        }

        fn path(&self, relative: &str) -> PathBuf {
            self.0.join(relative)
        }

        fn check(&self) -> io::Result<Counts> {
            validate(&self.0, SMALL)
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn exact_small_catalog_passes() {
        let fixture = Fixture::new();
        assert_eq!(
            fixture.check().unwrap(),
            Counts {
                libraries: 2,
                patterns: 2,
                library_probes: 2,
            }
        );
    }

    #[test]
    fn missing_pattern_fixture_rejected() {
        for name in ["example.atto", "expected.stdout"] {
            let fixture = Fixture::new();
            fs::remove_file(fixture.path(&format!("patterns/01-alpha/{name}"))).unwrap();
            assert!(fixture.check().is_err());
        }
    }

    #[test]
    fn legacy_ores_sources_rejected_even_with_valid_atto_files() {
        for relative in [
            "patterns/01-alpha/example.ores",
            "libraries/oreslang-a/example.ores",
        ] {
            let fixture = Fixture::new();
            fs::write(fixture.path(relative), "pub routine main(): void {}\n").unwrap();
            let error = fixture.check().expect_err("legacy source should fail closed");
            assert!(error.to_string().contains("legacy .ores"));
        }
    }

    #[cfg(unix)]
    #[test]
    fn dangling_legacy_ores_symlink_rejected() {
        use std::os::unix::fs::symlink;
        let fixture = Fixture::new();
        symlink(
            fixture.path("absent-legacy-target"),
            fixture.path("patterns/01-alpha/example.ores"),
        )
        .unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn wrong_oracle_rejected() {
        let fixture = Fixture::new();
        fs::write(fixture.path("patterns/02-beta/expected.stdout"), "PASS:1\n").unwrap();
        assert!(fixture.check().is_err());
        let fixture = Fixture::new();
        fs::write(
            fixture.path("libraries/oreslang-b/expected.stdout"),
            "PASS:x\n",
        )
        .unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn pattern_number_gap_rejected() {
        let fixture = Fixture::new();
        fs::rename(
            fixture.path("patterns/02-beta"),
            fixture.path("patterns/03-beta"),
        )
        .unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn missing_and_extra_catalog_entries_rejected() {
        let fixture = Fixture::new();
        fs::remove_dir_all(fixture.path("libraries/oreslang-b")).unwrap();
        assert!(fixture.check().is_err());
        let fixture = Fixture::new();
        fs::create_dir(fixture.path("patterns/03-extra")).unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn incomplete_library_pair_rejected() {
        for name in ["example.atto", "expected.stdout"] {
            let fixture = Fixture::new();
            fs::remove_file(fixture.path(&format!("libraries/oreslang-a/{name}"))).unwrap();
            assert!(fixture.check().is_err());
        }
    }

    #[test]
    fn missing_library_probe_count_rejected() {
        let fixture = Fixture::new();
        fs::remove_file(fixture.path("libraries/oreslang-a/example.atto")).unwrap();
        fs::remove_file(fixture.path("libraries/oreslang-a/expected.stdout")).unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn empty_source_rejected() {
        let fixture = Fixture::new();
        fs::write(fixture.path("patterns/01-alpha/example.atto"), " \n").unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn missing_required_index_rejected() {
        let fixture = Fixture::new();
        fs::remove_file(fixture.path("validation/README.md")).unwrap();
        assert!(fixture.check().is_err());
    }

    #[test]
    fn broken_readme_contract_rejected() {
        let fixture = Fixture::new();
        fs::write(fixture.path("patterns/01-alpha/README.md"), "# No status\n").unwrap();
        assert!(fixture.check().is_err());
    }

    #[cfg(unix)]
    #[test]
    fn symlinked_source_and_oracle_rejected() {
        use std::os::unix::fs::symlink;
        for name in ["example.atto", "expected.stdout"] {
            let fixture = Fixture::new();
            let path = fixture.path(&format!("patterns/01-alpha/{name}"));
            let other = fixture.path("original-file");
            fs::rename(&path, &other).unwrap();
            symlink(&other, &path).unwrap();
            assert!(fixture.check().is_err());
        }
    }

    #[cfg(unix)]
    #[test]
    fn symlinked_library_directory_rejected() {
        use std::os::unix::fs::symlink;
        let fixture = Fixture::new();
        let original = fixture.path("libraries/oreslang-a");
        let real = fixture.path("moved-directory");
        fs::rename(&original, &real).unwrap();
        symlink(&real, &original).unwrap();
        assert!(fixture.check().is_err());
    }
}
