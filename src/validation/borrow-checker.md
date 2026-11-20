# Borrow and lifetime checker: minimum test suite

| Program | Expected |
|---|---|
| Multiple simultaneously live immutable borrows | Accept |
| Single exclusive mutable borrow | Accept |
| Two overlapping exclusive borrows to the same location | Reject |
| Concurrent incompatible shared/mutable borrow | Reject |
| Distinct independently borrowable fields | Accept |
| Borrow escapes dead stack owner | Reject |
| Move while conflicting reference is live | Reject |
| Reborrow with valid nested scope | Accept |
| Return owned recursive tree | Accept |
| Closure captures by owned move | Accept |
| Closure captures dangling lexical borrow | Reject |
| Invalid borrow held across suspend | Reject |
| Address stable when pin guarantees it | Accept |
| Actor private state directly accessed outside authorized callback | Reject |

Compile-fail checks must assert diagnostic code/class and origin; parser failure is not valid proof of borrow checking.
