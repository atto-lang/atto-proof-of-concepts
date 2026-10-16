# Oreslang proof of concepts

[Source catalog](src/README.md): 60 library briefs and **80 pattern source prototypes (70 historically Java-verified; 10 new unverified)** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 real guest executions on the historical 70-example set**, which test sample outputs rather than the named patterns' full safety properties.

The new patterns numbered 71–80 have not yet been compiled or executed on Java/GraalVM or LLVM. The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the Oreslang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.
