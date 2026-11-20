# Actor and reader/writer-lock obligations

- Actor stateful execution: in any trace, `active_stateful_turns(actor) <= 1` even after suspend/resume, panic, cancellation, supervision or racing wakeups.
- Actor-private state is inaccessible outside `handle_state` (or a separately approved compiler-recognized scope).
- `critical-read`/ `critical-write` scopes only allow access according to their permissions; escaped guards/borrows rejected.
- Shared RW locks allow simultaneous readers, but exclude writer-reader and writer-writer overlap.
- **Do not conflate actor serialization with parallel readers:** multiple readers inside a strictly single-turn actor are still serialized unless state is published separately.
- Await while holding a mutable/exclusive state loan requires explicitly defined semantics; otherwise reject.
- Panic routes directly to supervisor CONTROL path; actor never intercepts its own panic.
- `tear_down()` closes actor resources once under defined shutdown ordering.
- Model check per-actor entry/exit, mailbox admission, cancellation and lock fairness; record model bounds.
