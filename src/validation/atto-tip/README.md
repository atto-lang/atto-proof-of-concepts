# AttoLang current-tip source contract

This cohort is copied byte-for-byte from **ores-truffle-oreslang/oreslang-source.java** `main` at commit `6d8eb70048eafc9a84c5aebe9c1bb06104f16e76` (observed November 10, 2026). It pins three positive scalar/type/call sources and two intentionally invalid language cases. Existing PoC patterns were not rewritten to infer unsupported syntax from these five files.

Run `python3 -m unittest discover -s src/validation/atto-tip -p 'test_atto_tip_fixtures.py' -v` to verify the five Git blob identities and the absence of legacy sources in this contract. This is **source identity only**, not parser, static semantic, negative-diagnostic, executable, or AOT backend evidence. To claim compatibility, execute every positive case using an independently pinned compiler and require the expected result; execute negative cases and check targeted rejection diagnostics (not merely a process crash). Then run the migrated 90 patterns, 32 library probes and supporting fixtures on Java/GraalVM and supported AOT backends, recording exact-head SHA/tree/runner job/attempt and real executed steps.

The historical 70/70 and 20/20 Java guest results were obtained against different source/runner revisions; they are not comparable to a fresh all-pattern tip pass.
