# Oreslang proof of concepts

[Source catalog](src/README.md): 60 library briefs and **78 pattern source prototypes** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 historical real guest executions** for patterns 01–70; patterns 71–78 remain unverified by a compiler. These executions test sample outputs rather than the named patterns' full safety properties.

The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the Oreslang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.
