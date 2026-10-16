# Pattern conformance and evidence matrix

**Java static verification:** 70/70 parser and 70/70 type/ownership passes in [funded exact-source CI #38318787965](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38318787965) using Java source commit `43edad9e31333e1e20c8646a8a22728b586696ea`. **LLVM:** `40b4430c0bba01d4a1980270cb90457d910e4835`, source tests not run. **Java/GraalVM guest execution:** 70/70 samples returned the exact expected stdout and exit 0 in [funded exact-source Java/GraalVM CI #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687); PoC `a162edf`, pinned Java `43edad9`. **LLVM guest execution:** not run. Java runtime PASS asserts sample behavior, not full algorithm safety.

| # | Native .ores source | Nature of exercise | Java status | LLVM status |
|---|---|---|---|---|
| 01 | [factory-method](01-factory-method/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 02 | [abstract-factory](02-abstract-factory/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 03 | [builder](03-builder/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 04 | [prototype](04-prototype/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 05 | [singleton](05-singleton/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 06 | [adapter](06-adapter/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 07 | [bridge](07-bridge/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 08 | [composite](08-composite/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 09 | [decorator](09-decorator/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 10 | [facade](10-facade/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 11 | [flyweight](11-flyweight/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 12 | [proxy](12-proxy/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 13 | [chain-of-responsibility](13-chain-of-responsibility/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 14 | [command](14-command/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 15 | [interpreter](15-interpreter/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 16 | [iterator](16-iterator/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 17 | [mediator](17-mediator/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 18 | [memento](18-memento/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 19 | [observer](19-observer/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 20 | [state](20-state/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 21 | [strategy](21-strategy/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 22 | [template-method](22-template-method/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 23 | [visitor](23-visitor/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 24 | [dependency-injection](24-dependency-injection/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 25 | [null-object](25-null-object/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 26 | [repository](26-repository/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 27 | [unit-of-work](27-unit-of-work/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 28 | [identity-map](28-identity-map/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 29 | [data-mapper](29-data-mapper/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 30 | [active-record](30-active-record/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 31 | [service-layer](31-service-layer/example.ores) | Behavioral prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 32 | [model-view-controller](32-model-view-controller/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 33 | [model-view-viewmodel](33-model-view-viewmodel/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 34 | [cqrs](34-cqrs/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 35 | [event-sourcing](35-event-sourcing/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 36 | [publish-subscribe](36-publish-subscribe/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 37 | [reactor](37-reactor/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 38 | [proactor](38-proactor/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 39 | [actor-model](39-actor-model/example.ores) and [real actor proofs](39-actor-model/runtime/README.md) | Sequential baseline + 2 spawned-actor behaviors | **Baseline PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687); **actor runtime 2/2 PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38342677493) | Not run (feature scope may be unsupported) |
| 40 | [producer-consumer](40-producer-consumer/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 41 | [thread-pool](41-thread-pool/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 42 | [object-pool](42-object-pool/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 43 | [future-promise](43-future-promise/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 44 | [pipeline](44-pipeline/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 45 | [middleware](45-middleware/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 46 | [circuit-breaker](46-circuit-breaker/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 47 | [retry-with-backoff](47-retry-with-backoff/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 48 | [bulkhead](48-bulkhead/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 49 | [saga](49-saga/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 50 | [specification](50-specification/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 51 | [typestate](51-typestate/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 52 | [session-types](52-session-types/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 53 | [object-capability](53-object-capability/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 54 | [raii](54-raii/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 55 | [region-based-memory-management](55-region-based-memory-management/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 56 | [generational-handles](56-generational-handles/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 57 | [intrusive-linkage](57-intrusive-linkage/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 58 | [epoch-based-reclamation](58-epoch-based-reclamation/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 59 | [hazard-pointers](59-hazard-pointers/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 60 | [read-copy-update](60-read-copy-update/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 61 | [sequence-lock](61-sequence-lock/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 62 | [flat-combining](62-flat-combining/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 63 | [disruptor-sequenced-ring-buffer](63-disruptor-sequenced-ring-buffer/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 64 | [work-stealing](64-work-stealing/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 65 | [trampoline](65-trampoline/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 66 | [zipper](66-zipper/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 67 | [copy-on-write](67-copy-on-write/example.ores) | Native prototype | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 68 | [transactional-outbox](68-transactional-outbox/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 69 | [half-sync-half-async](69-half-sync-half-async/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |
| 70 | [supervisor-tree](70-supervisor-tree/example.ores) | Reference model | **Static + Java guest PASS** [CI](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | Not run (feature scope may be unsupported) |

## New additions (71–80): exact-source Java static verification

The historical 70/70 Java guest run remains **limited to 01–70**. Java 25 [CI #38929258766](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) verified exact source blobs and **10/10 Java parser/type/ownership** for 71–80, but did not run their guest runtime; LLVM remains untested.

| # | Native .ores source | Nature of exercise | Java status | LLVM status |
|---|---|---|---|---|
| 71 | [idempotent-consumer](71-idempotent-consumer/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 72 | [token-bucket-rate-limiter](72-token-bucket-rate-limiter/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 73 | [optimistic-concurrency-control](73-optimistic-concurrency-control/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 74 | [fencing-tokens](74-fencing-tokens/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 75 | [rendezvous-hashing](75-rendezvous-hashing/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 76 | [singleflight](76-singleflight/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 77 | [cache-aside](77-cache-aside/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 78 | [dead-letter-queue](78-dead-letter-queue/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 79 | [feature-flags-rollout](79-feature-flags-rollout/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |
| 80 | [vector-clocks](80-vector-clocks/example.ores) | Sequential native reference model | **Java static PASS** [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) (guest not run) | **Not run** |

## New additions (81–90): compiler and runtime pending

| # | Native .ores source | Nature of exercise | Java status | LLVM status |
|---|---|---|---|---|
| 81 | [request-reply-correlation](81-request-reply-correlation/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 82 | [lease-expiration-renewal](82-lease-expiration-renewal/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 83 | [weighted-quorum-voting](83-weighted-quorum-voting/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 84 | [grow-only-counter-crdt](84-grow-only-counter-crdt/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 85 | [last-writer-wins-register](85-last-writer-wins-register/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 86 | [credit-based-flow-control](86-credit-based-flow-control/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 87 | [write-ahead-log-replay](87-write-ahead-log-replay/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 88 | [retry-budget](88-retry-budget/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 89 | [hedged-requests](89-hedged-requests/example.ores) | Sequential native reference model | **Not run** | **Not run** |
| 90 | [deadline-propagation](90-deadline-propagation/example.ores) | Sequential native reference model | **Not run** | **Not run** |

## Evidence rules

- Reference model: verifies only a sequential arithmetic/state-machine oracle, not the named full concurrent/resource/ownership guarantee.
- Native prototype: concrete classes/closures/channels/etc.; lacks actual Java/LLVM test evidence.
- Behavioral prototype: simple behavior test; not a production implementation.
- A Python source-hygiene PASS is not a Java parser/type-checker PASS.
- LLVM's documented narrow source subset does not support most of these programs. Rejecting unsupported code is not a successful cross-backend compatibility result.
- Evidence is for Parser.parse + TypeChecker.check, including ownership and return-cleanup checking. It is not a full linked CLI compilation, guest runtime test, formal verification, or LLVM parity. Retain the actual run permalink and exact source SHA.
