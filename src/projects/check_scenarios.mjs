#!/usr/bin/env node
// Independent reference-model cross-check. Not Oreslang execution or a runtime proof.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));
const clone = value => JSON.parse(JSON.stringify(value));
const load = name => {
  const file = JSON.parse(readFileSync(join(root, name, "scenario.json"), "utf8"));
  assert.equal(file.version, 1);
  assert.equal(file.project, name);
  return file;
};
function banking(f) {
  const accounts = { ...f.initial.accounts };
  const total = Object.values(accounts).reduce((a, b) => a + b, 0);
  const accepted = [], duplicates = [], rejected = [], seen = new Map();
  for (const s of f.steps) {
    assert.equal(s.op, "transfer");
    assert.ok(Number.isSafeInteger(s.amount) && s.amount > 0 && s.from !== s.to);
    assert.ok(Object.hasOwn(accounts, s.from) && Object.hasOwn(accounts, s.to));
    const fingerprint = JSON.stringify([s.from, s.to, s.amount]);
    if (seen.has(s.id)) {
      assert.equal(seen.get(s.id), fingerprint, "conflicting idempotency key");
      duplicates.push(s.id);
    } else if (accounts[s.from] < s.amount) {
      seen.set(s.id, fingerprint);
      rejected.push(s.id);
    } else {
      accounts[s.from] -= s.amount;
      accounts[s.to] += s.amount;
      seen.set(s.id, fingerprint);
      accepted.push(s.id);
    }
    assert.equal(Object.values(accounts).reduce((a, b) => a + b, 0), total);
    assert.ok(Object.values(accounts).every(x => x >= 0));
  }
  return { accounts, accepted, duplicates, rejected, total };
}
function scheduler(f) {
  const states = new Map();
  const executed = [], cancelled = [], refused = [];
  let stopped = false;
  for (const s of f.steps) {
    if (s.op === "submit") {
      if (stopped) refused.push(s.id);
      else {
        assert.ok(!states.has(s.id), "duplicate task ID");
        states.set(s.id, "queued");
      }
    } else if (s.op === "run") {
      if (stopped || states.get(s.id) !== "queued") refused.push(s.id);
      else { states.set(s.id, "done"); executed.push(s.id); }
    } else if (s.op === "cancel") {
      assert.equal(states.get(s.id), "queued");
      states.set(s.id, "cancelled");
      cancelled.push(s.id);
    } else if (s.op === "stop") {
      assert.ok(!stopped, "repeated STOP");
      stopped = true;
      for (const [id, status] of states) {
        if (status === "queued") { states.set(id, "cancelled"); cancelled.push(id); }
      }
    } else throw new Error("unsupported scheduler step: " + s.op);
  }
  assert.equal(new Set(executed).size, executed.length);
  return { executed, cancelled, refused, stopped };
}
function http(f) {
  const released = new Set(), cancelled = new Set(), responses = [];
  for (const s of f.steps) {
    if (s.op === "cancel") {
      assert.ok(!released.has(s.id), "double release");
      released.add(s.id); cancelled.add(s.id);
    } else if (s.op === "request") {
      if (cancelled.has(s.id)) continue;
      assert.ok(!released.has(s.id), "duplicate completion");
      if (s.method === "GET" && s.path === "/health") responses.push([s.id, 200, "ok"]);
      else if (s.method === "POST" && s.path === "/echo") responses.push([s.id, 200, s.body]);
      else responses.push([s.id, 404, "not found"]);
      released.add(s.id);
    } else throw new Error("unsupported HTTP step: " + s.op);
  }
  return { responses, released: [...released].sort() };
}
function kv(f) {
  let committed = { ...f.initial.committed }, working = { ...committed };
  let commit_count = 0, crashed = false;
  for (const s of f.steps) {
    if (s.op === "put") {
      assert.ok(!crashed);
      working[s.key] = s.value;
    } else if (s.op === "commit") {
      assert.ok(!crashed); committed = { ...working }; commit_count++;
    } else if (s.op === "crash") {
      working = {}; crashed = true;
    } else if (s.op === "recover") {
      assert.ok(crashed); working = { ...committed }; crashed = false;
    } else throw new Error("unsupported KV step: " + s.op);
  }
  assert.ok(!crashed);
  return { committed, working, commit_count };
}
function graph(f) {
  let state = clone(f.initial);
  const undo = [], redo = [];
  for (const s of f.steps) {
    if (s.op === "node" || s.op === "edge") {
      undo.push(clone(state)); redo.length = 0;
      if (s.op === "node") {
        assert.ok(!state.nodes.includes(s.id));
        state.nodes.push(s.id);
      } else {
        assert.ok(state.nodes.includes(s.from) && state.nodes.includes(s.to));
        assert.ok(!state.edges.some(e => e[0] === s.from && e[1] === s.to));
        state.edges.push([s.from, s.to]);
      }
    } else if (s.op === "undo") {
      assert.ok(undo.length);
      redo.push(clone(state)); state = undo.pop();
    } else if (s.op === "redo") {
      assert.ok(redo.length);
      undo.push(clone(state)); state = redo.pop();
    } else throw new Error("unsupported graph operation: " + s.op);
    for (const [from, to] of state.edges)
      assert.ok(state.nodes.includes(from) && state.nodes.includes(to));
  }
  return { ...state, undo_depth: undo.length, redo_depth: redo.length };
}
function evaluate(node, env) {
  if (node.kind === "int") {
    if (!Number.isSafeInteger(node.value)) throw new Error("non-integer-literal");
    return node.value;
  }
  if (node.kind === "var") {
    if (!Object.hasOwn(env, node.name)) throw new Error("unbound:" + node.name);
    return env[node.name];
  }
  if (node.kind === "let")
    return evaluate(node.body, { ...env, [node.name]: evaluate(node.value, env) });
  if (node.kind === "add") return evaluate(node.left, env) + evaluate(node.right, env);
  if (node.kind === "mul") return evaluate(node.left, env) * evaluate(node.right, env);
  throw new Error("unknown-expression:" + node.kind);
}
function interpreter(f) {
  for (const test of f.programs) {
    let result, error;
    try { result = evaluate(test.expr, {}); }
    catch (err) { error = err; }
    if (Object.hasOwn(test, "expected_error")) {
      assert.ok(error, "expected interpreter failure");
      assert.equal(error.message, test.expected_error);
    } else {
      if (error) throw error;
      assert.equal(result, test.expected);
    }
  }
}

const runners = {
  "actor-banking": banking,
  "actor-scheduler": scheduler,
  "async-http-server": http,
  "embedded-kv-database": kv,
  "graph-editor": graph,
  "self-hosted-interpreter": interpreter
};
for (const [name, run] of Object.entries(runners).sort(([a], [b]) => a.localeCompare(b))) {
  const f = load(name);
  const outcome = run(f);
  if (name !== "self-hosted-interpreter") assert.deepEqual(outcome, f.expected);
  console.log("PASS independent JS reference:", name);
}
console.log("Six JavaScript reference scenarios passed; NO native Oreslang execution.");
// Adversarial checks prevent the positive fixtures from masking broken guards.
{
  const invalid = load("actor-banking");
  invalid.steps.splice(1, 0, { op:"transfer", id:"t1", from:"bob", to:"alice", amount:1 });
  assert.throws(() => banking(invalid), /conflicting idempotency key/);
}
{
  const invalid = load("graph-editor");
  invalid.steps = [{ op:"edge", from:"missing", to:"missing" }];
  assert.throws(() => graph(invalid));
}
{
  const invalid = load("async-http-server");
  invalid.steps = [invalid.steps[0], invalid.steps[0]];
  assert.throws(() => http(invalid), /duplicate completion/);
}
{
  const invalid = load("embedded-kv-database");
  invalid.steps = [{ op:"crash" }, { op:"put", key:"k", value:1 }];
  assert.throws(() => kv(invalid));
}
{
  const invalid = load("actor-scheduler");
  invalid.steps = [{ op:"submit", id:"x" }, { op:"stop" }, { op:"run", id:"x" }];
  assert.deepEqual(scheduler(invalid), { executed:[], cancelled:["x"], refused:["x"], stopped:true });
}
assert.throws(
  () => evaluate({ kind:"int", value:true }, {}),
  /non-integer-literal/
);
console.log("Six additional adversarial JavaScript checks passed; NO native Oreslang execution.");

