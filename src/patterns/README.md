# Design pattern catalog (70)

23 classical GoF, 27 enterprise/application/concurrency, 20 advanced systems patterns. Curated list, not a measured popularity ranking. Each directory holds a concrete implementation specification; planned does not mean implemented.

| # | Pattern | Family | Intent |
|---|---|---|---|
| 1 | [Factory Method](./01-factory-method/) | GoF creational | Factory selects concrete type through interface |
| 2 | [Abstract Factory](./02-abstract-factory/) | GoF creational | Build compatible families of interfaces |
| 3 | [Builder](./03-builder/) | GoF creational | Stepwise construction of complex values |
| 4 | [Prototype](./04-prototype/) | GoF creational | Clone polymorphic object graphs |
| 5 | [Singleton](./05-singleton/) | GoF creational | Publish exactly one lazily initialized instance |
| 6 | [Adapter](./06-adapter/) | GoF structural | Translate one interface to another |
| 7 | [Bridge](./07-bridge/) | GoF structural | Separate abstraction and implementation dimensions |
| 8 | [Composite](./08-composite/) | GoF structural | Use uniform interface for recursive tree nodes |
| 9 | [Decorator](./09-decorator/) | GoF structural | Compose nested wrappers around an interface |
| 10 | [Facade](./10-facade/) | GoF structural | Provide simple API over multiple components |
| 11 | [Flyweight](./11-flyweight/) | GoF structural | Share immutable data among instances |
| 12 | [Proxy](./12-proxy/) | GoF structural | Interpose controlled or lazy access to objects |
| 13 | [Chain of Responsibility](./13-chain-of-responsibility/) | GoF behavioral | Forward requests through linked handlers |
| 14 | [Command](./14-command/) | GoF behavioral | Encapsulate actions and undo in values |
| 15 | [Interpreter](./15-interpreter/) | GoF behavioral | Evaluate recursive syntax and lexical scopes |
| 16 | [Iterator](./16-iterator/) | GoF behavioral | Abstract collection traversal |
| 17 | [Mediator](./17-mediator/) | GoF behavioral | Coordinate collaborating objects centrally |
| 18 | [Memento](./18-memento/) | GoF behavioral | Capture and restore state snapshots |
| 19 | [Observer](./19-observer/) | GoF behavioral | Manage subscriptions and notifications |
| 20 | [State](./20-state/) | GoF behavioral | Model behavior with explicit runtime states |
| 21 | [Strategy](./21-strategy/) | GoF behavioral | Select interchangeable algorithms at runtime |
| 22 | [Template Method](./22-template-method/) | GoF behavioral | Fix algorithm order while customizing steps |
| 23 | [Visitor](./23-visitor/) | GoF behavioral | Traverse heterogeneous object hierarchies |
| 24 | [Dependency Injection](./24-dependency-injection/) | enterprise/application | Bind dependencies by scope and interface |
| 25 | [Null Object](./25-null-object/) | enterprise/application | Use an inert implementation instead of null |
| 26 | [Repository](./26-repository/) | enterprise/application | Abstract domain persistence |
| 27 | [Unit of Work](./27-unit-of-work/) | enterprise/application | Commit grouped changes atomically |
| 28 | [Identity Map](./28-identity-map/) | enterprise/application | Share one logical instance per entity ID |
| 29 | [Data Mapper](./29-data-mapper/) | enterprise/application | Map persistence rows into domain types |
| 30 | [Active Record](./30-active-record/) | enterprise/application | Combine persistence methods and domain object |
| 31 | [Service Layer](./31-service-layer/) | enterprise/application | Expose high-level domain operations |
| 32 | [Model View Controller](./32-model-view-controller/) | enterprise/application | Separate model view and controller |
| 33 | [Model View ViewModel](./33-model-view-viewmodel/) | enterprise/application | Bind presentation to derived state |
| 34 | [CQRS](./34-cqrs/) | enterprise/application | Separate write commands from read projections |
| 35 | [Event Sourcing](./35-event-sourcing/) | enterprise/application | Rebuild state from immutable events |
| 36 | [Publish Subscribe](./36-publish-subscribe/) | concurrency/architecture | Fan out events to independent subscribers |
| 37 | [Reactor](./37-reactor/) | concurrency/architecture | Dispatch I/O readiness through event loop |
| 38 | [Proactor](./38-proactor/) | concurrency/architecture | Dispatch asynchronous completion results |
| 39 | [Actor Model](./39-actor-model/) | concurrency/architecture | Use message passing around isolated state |
| 40 | [Producer Consumer](./40-producer-consumer/) | concurrency/architecture | Coordinate queues and worker stages |
| 41 | [Thread Pool](./41-thread-pool/) | concurrency/architecture | Share reusable execution workers |
| 42 | [Object Pool](./42-object-pool/) | concurrency/architecture | Lease and reset reusable objects |
| 43 | [Future Promise](./43-future-promise/) | concurrency/architecture | Represent eventual success or failure |
| 44 | [Pipeline](./44-pipeline/) | concurrency/architecture | Compose transformations and backpressure |
| 45 | [Middleware](./45-middleware/) | concurrency/architecture | Wrap async request-processing handlers |
| 46 | [Circuit Breaker](./46-circuit-breaker/) | concurrency/architecture | Gate calls by error and recovery state |
| 47 | [Retry with Backoff](./47-retry-with-backoff/) | concurrency/architecture | Repeat safely after recoverable errors |
| 48 | [Bulkhead](./48-bulkhead/) | concurrency/architecture | Isolate independent capacity cohorts |
| 49 | [Saga](./49-saga/) | concurrency/architecture | Apply distributed compensating transactions |
| 50 | [Specification](./50-specification/) | concurrency/architecture | Compose predicate functions and expressions |
| 51 | [Typestate](./51-typestate/) | advanced | Encode legal resource lifecycle in types |
| 52 | [Session Types](./52-session-types/) | advanced | Encode valid protocol message sequences |
| 53 | [Object Capability](./53-object-capability/) | advanced | Authorize via explicit unforgeable object handles |
| 54 | [RAII](./54-raii/) | advanced | Tie owned resources to deterministic scope exit |
| 55 | [Region Based Memory Management](./55-region-based-memory-management/) | advanced | Allocate values with linked region lifetime |
| 56 | [Generational Handles](./56-generational-handles/) | advanced | Use slot plus version to address storage |
| 57 | [Intrusive Linkage](./57-intrusive-linkage/) | advanced | Embed list links within pinned nodes |
| 58 | [Epoch Based Reclamation](./58-epoch-based-reclamation/) | advanced | Delay freeing until active readers exit epochs |
| 59 | [Hazard Pointers](./59-hazard-pointers/) | advanced | Protect concurrently dereferenced nodes |
| 60 | [Read Copy Update](./60-read-copy-update/) | advanced | Publish immutable versions then reclaim later |
| 61 | [Sequence Lock](./61-sequence-lock/) | advanced | Validate lockless optimistic read snapshots |
| 62 | [Flat Combining](./62-flat-combining/) | advanced | Serialize batches of contended updates |
| 63 | [Disruptor Sequenced Ring Buffer](./63-disruptor-sequenced-ring-buffer/) | advanced | Publish work through sequenced ring slots |
| 64 | [Work Stealing](./64-work-stealing/) | advanced | Steal pending work from other worker deques |
| 65 | [Trampoline](./65-trampoline/) | advanced | Replace recursive stack growth with continuation loop |
| 66 | [Zipper](./66-zipper/) | advanced | Navigate and edit immutable recursive trees |
| 67 | [Copy on Write](./67-copy-on-write/) | advanced | Detach shared storage on mutation |
| 68 | [Transactional Outbox](./68-transactional-outbox/) | advanced | Write state and message record in one transaction |
| 69 | [Half Sync Half Async](./69-half-sync-half-async/) | advanced | Bridge sync-facing APIs onto asynchronous machinery |
| 70 | [Supervisor Tree](./70-supervisor-tree/) | advanced | Supervise dependent actors under restart policy |

Native source prototypes have been started for Strategy, Future Promise, Pipeline and Specification; all require actual compiler/runtime verification.
