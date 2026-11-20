"""Regression checks for six deterministic Python reference models."""
from pathlib import Path
import json
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_scenarios as subject

def load(name):
    return json.loads((subject.ROOT / name / "scenario.json").read_text())

class ProjectOracleTests(unittest.TestCase):
    def test_six_reference_oracles(self):
        self.assertEqual(subject.main(), 0)
    def test_bank_duplicate_and_insufficient_do_not_debit(self):
        case = load("actor-banking")
        result = subject.banking(case)
        self.assertEqual(result["accounts"], {"alice": 80, "bob": 70})
        self.assertEqual(result["duplicates"], ["t1"])
        self.assertEqual(result["rejected"], ["tX"])
    def test_graph_no_dangling_edges(self):
        case = load("graph-editor")
        case["steps"] = [{"op":"edge", "from":"missing","to":"absent"}]
        with self.assertRaises(AssertionError):
            subject.graph(case)
    def test_http_double_release_refused(self):
        case = load("async-http-server")
        case["steps"] = [case["steps"][0], case["steps"][0]]
        with self.assertRaises(AssertionError):
            subject.http(case)
    def test_uncommitted_writes_discarded_on_recovery(self):
        self.assertEqual(subject.kv(load("embedded-kv-database"))["working"], {"a": 3})
    def test_scheduler_cancelled_task_not_executed(self):
        case = load("actor-scheduler")
        result = subject.scheduler(case)
        self.assertEqual(result["executed"], ["a", "c"])
        self.assertIn("b", result["refused"])
    def test_interpreter_missing_binding_raises(self):
        with self.assertRaisesRegex(ValueError, "^unbound:missing$"):
            subject.eval_expr({"kind":"var","name":"missing"}, {})


    def test_bank_rejects_conflicting_idempotency_payload(self):
        case = load("actor-banking")
        case["steps"].insert(2, {"op":"transfer", "id":"t1",
                                  "from":"bob", "to":"alice", "amount":30})
        with self.assertRaisesRegex(ValueError, "conflicting-idempotency-key"):
            subject.banking(case)
    def test_rejected_transaction_key_does_not_execute_after_funding(self):
        case = load("actor-banking")
        case["initial"] = {"accounts":{"alice":0,"bob":100}}
        case["steps"] = [
            {"op":"transfer","id":"denied","from":"alice","to":"bob","amount":50},
            {"op":"transfer","id":"fund","from":"bob","to":"alice","amount":90},
            {"op":"transfer","id":"denied","from":"alice","to":"bob","amount":50}
        ]
        actual = subject.banking(case)
        self.assertEqual(actual["accounts"], {"alice":90,"bob":10})
        self.assertEqual(actual["rejected"], ["denied"])
        self.assertEqual(actual["duplicates"], ["denied"])
    def test_scheduler_stop_cancels_pending_and_refuses_execution(self):
        case = load("actor-scheduler")
        case["steps"] = [{"op":"submit", "id":"x"}, {"op":"stop"},
                          {"op":"run","id":"x"}, {"op":"submit","id":"y"}]
        actual = subject.scheduler(case)
        self.assertEqual(actual["cancelled"], ["x"])
        self.assertEqual(actual["executed"], [])
        self.assertEqual(actual["refused"], ["x","y"])
    def test_interpreter_rejects_boolean_as_integer(self):
        with self.assertRaisesRegex(ValueError, "non-integer-literal"):
            subject.eval_expr({"kind":"int","value":True}, {})

if __name__ == "__main__":
    unittest.main()
