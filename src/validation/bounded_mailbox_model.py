"""Small exhaustive interleaving explorer for bounded actor DATA + CONTROL.

This checks a finite abstract protocol, not real native concurrency,
scheduler fairness, actor runtime execution, or an unbounded theorem.
"""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    issued: int = 0
    reserved: int = 0
    queued: int = 0
    completed: int = 0
    cancelled: int = 0
    control_pending: bool = False
    control_delivered: bool = False
    stopped: bool = False


def invariant(state, capacity):
    if type(capacity) is not int or capacity < 1 or capacity > 8:
        raise ValueError("capacity outside small model bounds")
    if any(type(x) is not int or x < 0 for x in
           (state.issued, state.reserved, state.queued,
            state.completed, state.cancelled)):
        raise AssertionError("invalid negative message/accounting count")
    if state.reserved + state.queued > capacity:
        raise AssertionError("DATA credit exceeded bounded capacity")
    if state.issued != (state.reserved + state.queued
                        + state.completed + state.cancelled):
        raise AssertionError("lost, leaked or duplicated message credit")
    if state.control_delivered and (
        not state.stopped or state.control_pending or state.queued or state.reserved
    ):
        raise AssertionError("CONTROL finalization left live DATA")


def next_states(state, *, capacity, max_issued):
    """Enumerate all enabled abstract transitions, including control at full DATA."""
    invariant(state, capacity)
    if type(max_issued) is not int or max_issued < 0:
        raise ValueError("max_issued must be nonnegative")
    if state.stopped:
        return ()
    enabled = []
    if state.issued < max_issued and state.reserved + state.queued < capacity:
        enabled.append(("reserve", replace(
            state, issued=state.issued + 1, reserved=state.reserved + 1)))
    if state.reserved:
        enabled.append(("publish", replace(
            state, reserved=state.reserved - 1, queued=state.queued + 1)))
        enabled.append(("cancel_reserved", replace(
            state, reserved=state.reserved - 1, cancelled=state.cancelled + 1)))
    if state.queued:
        enabled.append(("deliver", replace(
            state, queued=state.queued - 1, completed=state.completed + 1)))
    if not state.control_pending and not state.control_delivered:
        # CONTROL is a dedicated trusted lane, never charged to DATA credits.
        enabled.append(("control_arrival", replace(state, control_pending=True)))
    if state.control_pending:
        enabled.append(("control_finalize", replace(
            state, stopped=True, control_pending=False, control_delivered=True,
            cancelled=state.cancelled + state.reserved + state.queued,
            reserved=0, queued=0)))
    for _, next_state in enabled:
        invariant(next_state, capacity)
    return tuple(enabled)


def explore(*, capacity=2, max_issued=3):
    """Breadth-first enumerate the complete bounded reachable state graph."""
    if type(max_issued) is not int or not 0 <= max_issued <= 8:
        raise ValueError("state-space request exceeds bounded model limit")
    initial = State()
    pending = deque([initial])
    visited = {initial}
    transitions = []
    while pending:
        state = pending.popleft()
        for action, successor in next_states(
            state, capacity=capacity, max_issued=max_issued
        ):
            transitions.append((state, action, successor))
            if successor not in visited:
                visited.add(successor)
                pending.append(successor)
    return frozenset(visited), tuple(transitions)
