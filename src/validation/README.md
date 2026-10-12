# Conformance and proof obligations

Use four separate evidence levels: (1) compiler acceptance/rejection, (2) randomized and targeted runtime testing, (3) bounded model checking with explicit bounds, (4) formal soundness proofs with stated assumptions. **Tests alone are not proofs.**

Every fixture records required features, backend, expected outcome, diagnostic (if negative), provenance and run command. Unsupported features are neither silently passed nor silently skipped.

Coverage areas: `borrow-checker.md`, `gc.md`, `actors-and-locks.md`, `backend-parity.md`.
