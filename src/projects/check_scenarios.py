#!/usr/bin/env python3
"""Execute six bounded Python reference oracles; never claim Oreslang execution."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if sys.flags.optimize:
    raise RuntimeError("optimized Python disables reference-oracle assertions")
EXPECTED = {"actor-banking", "graph-editor", "async-http-server",
            "embedded-kv-database", "actor-scheduler", "self-hosted-interpreter"}

def banking(v):
    balances = dict(v["initial"]["accounts"])
    initial_total = sum(balances.values())
    accepted, duplicates, rejected = [], [], []
    seen = {}
    for s in v["steps"]:
        assert s["op"] == "transfer"
        tx, a, b, amount = s["id"], s["from"], s["to"], s["amount"]
        assert type(amount) is int and amount > 0 and a != b
        fingerprint = (a, b, amount)
        if tx in seen:
            if seen[tx] != fingerprint:
                raise ValueError("conflicting-idempotency-key:" + tx)
            duplicates.append(tx)
        elif balances[a] < amount:
            seen[tx] = fingerprint
            rejected.append(tx)
        else:
            balances[a] -= amount
            balances[b] += amount
            seen[tx] = fingerprint
            accepted.append(tx)
        assert sum(balances.values()) == initial_total
        assert all(x >= 0 for x in balances.values())
    return dict(accounts=balances, accepted=accepted, duplicates=duplicates,
                rejected=rejected, total=sum(balances.values()))

def graph(v):
    state = copy.deepcopy(v["initial"])
    undo, redo = [], []
    for s in v["steps"]:
        op = s["op"]
        if op in ("node", "edge"):
            old = copy.deepcopy(state)
            if op == "node":
                assert s["id"] not in state["nodes"]
                state["nodes"].append(s["id"])
            else:
                assert s["from"] in state["nodes"] and s["to"] in state["nodes"]
                assert [s["from"], s["to"]] not in state["edges"]
                state["edges"].append([s["from"], s["to"]])
            undo.append(old)
            redo.clear()
        elif op == "undo":
            assert undo
            redo.append(copy.deepcopy(state))
            state = undo.pop()
        elif op == "redo":
            assert redo
            undo.append(copy.deepcopy(state))
            state = redo.pop()
        else:
            raise ValueError(op)
        assert all(a in state["nodes"] and b in state["nodes"] for a,b in state["edges"])
    return dict(**state, undo_depth=len(undo), redo_depth=len(redo))

def http(v):
    cancelled, released = set(), set()
    responses = []
    for s in v["steps"]:
        identity = s["id"]
        if s["op"] == "cancel":
            assert identity not in released
            cancelled.add(identity)
            released.add(identity)
        elif s["op"] == "request":
            if identity in cancelled:
                continue
            assert identity not in released
            path, method = s["path"], s["method"]
            if method == "GET" and path == "/health":
                response = [identity, 200, "ok"]
            elif method == "POST" and path == "/echo":
                response = [identity, 200, s["body"]]
            else:
                response = [identity, 404, "not found"]
            responses.append(response)
            released.add(identity)
        else:
            raise ValueError(s["op"])
    return dict(responses=responses, released=sorted(released))

def kv(v):
    committed = dict(v["initial"]["committed"])
    working = dict(committed)
    count = 0
    crashed = False
    for s in v["steps"]:
        op = s["op"]
        if op == "put":
            assert not crashed
            working[s["key"]] = s["value"]
        elif op == "commit":
            assert not crashed
            committed = dict(working)
            count += 1
        elif op == "crash":
            working = {}
            crashed = True
        elif op == "recover":
            assert crashed
            working = dict(committed)
            crashed = False
        else:
            raise ValueError(op)
    assert not crashed
    return dict(committed=committed, working=working, commit_count=count)

def scheduler(v):
    state, executed, cancelled, refused = {}, [], [], []
    stopped = False
    for s in v["steps"]:
        op = s["op"]
        identity = s.get("id")
        if op == "submit":
            if stopped:
                refused.append(identity)
            else:
                assert identity not in state
                state[identity] = "queued"
        elif op == "run":
            if stopped or state.get(identity) != "queued":
                refused.append(identity)
            else:
                state[identity] = "done"
                executed.append(identity)
        elif op == "cancel":
            assert state.get(identity) == "queued"
            state[identity] = "cancelled"
            cancelled.append(identity)
        elif op == "stop":
            if stopped:
                raise ValueError("repeated-stop")
            stopped = True
            for pending_id, status in state.items():
                if status == "queued":
                    state[pending_id] = "cancelled"
                    cancelled.append(pending_id)
        else:
            raise ValueError(op)
    assert len(executed) == len(set(executed))
    return dict(executed=executed, cancelled=cancelled, refused=refused, stopped=stopped)

def eval_expr(node, env):
    kind = node["kind"]
    if kind == "int":
        if type(node["value"]) is not int:
            raise ValueError("non-integer-literal")
        return node["value"]
    if kind == "var":
        if node["name"] not in env:
            raise ValueError("unbound:" + node["name"])
        return env[node["name"]]
    if kind == "let":
        value = eval_expr(node["value"], env)
        child = dict(env)
        child[node["name"]] = value
        return eval_expr(node["body"], child)
    if kind == "add":
        return eval_expr(node["left"], env) + eval_expr(node["right"], env)
    if kind == "mul":
        return eval_expr(node["left"], env) * eval_expr(node["right"], env)
    raise ValueError("unknown-expression:" + kind)

def interpreter(v):
    for i, case in enumerate(v["programs"]):
        try:
            result = eval_expr(case["expr"], {})
            assert "expected_error" not in case, f"case {i}: missing expected error"
            assert result == case["expected"], f"case {i}: {result} != {case['expected']}"
        except ValueError as exc:
            assert "expected_error" in case, f"case {i}: unexpected {exc}"
            assert str(exc) == case["expected_error"], f"case {i}: {exc}"
    return "all programs matched"

RUNNERS = {"actor-banking": banking, "graph-editor": graph, "async-http-server": http,
           "embedded-kv-database": kv, "actor-scheduler": scheduler,
           "self-hosted-interpreter": interpreter}

def main():
    seen = set()
    for name in sorted(EXPECTED):
        filename = ROOT / name / "scenario.json"
        v = json.loads(filename.read_text(encoding="utf8"))
        assert v["version"] == 1 and v["project"] == name
        if name == "self-hosted-interpreter":
            actual = interpreter(v)
            assert actual == "all programs matched"
        else:
            actual = RUNNERS[name](v)
            assert actual == v["expected"], f"{name}: actual={actual} expected={v['expected']}"
        print("PASS reference model:", name)
        seen.add(name)
    assert seen == EXPECTED
    print("All six reference-oracle scenarios passed; NO native Oreslang execution.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ValueError, KeyError) as exc:
        print("FAIL reference model:", exc, file=sys.stderr)
        raise SystemExit(1)
