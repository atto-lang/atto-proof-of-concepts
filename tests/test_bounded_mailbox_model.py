"""Bounded actor concurrency model explorer regression tests."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "validation"))
from bounded_mailbox_model import State, explore, invariant, next_states


class ModelTests(unittest.TestCase):
    def test_enumeration_covers_multiple_message_interleavings(self):
        states, edges = explore(capacity=2, max_issued=3)
        self.assertGreater(len(states), 15)
        self.assertGreater(len(edges), len(states))
        for state in states:
            invariant(state, 2)
        self.assertTrue(any(action == "cancel_reserved" for _, action, _ in edges))
        self.assertTrue(any(action == "deliver" for _, action, _ in edges))

    def test_full_data_mailbox_cannot_starve_control_admission(self):
        states, _ = explore(capacity=2, max_issued=3)
        full = [s for s in states if not s.stopped and s.queued + s.reserved == 2
                and not s.control_pending]
        self.assertTrue(full)
        for state in full:
            actions = dict(next_states(state, capacity=2, max_issued=3))
            self.assertIn("control_arrival", actions)
            control_actions = dict(next_states(actions["control_arrival"],
                                               capacity=2, max_issued=3))
            self.assertIn("control_finalize", control_actions)
            finalized = control_actions["control_finalize"]
            self.assertEqual(finalized.issued,
                             finalized.cancelled + finalized.completed)
            self.assertTrue(finalized.control_delivered)
            self.assertFalse(finalized.queued or finalized.reserved)

    def test_duplicate_credit_and_lost_refund_fail_conservation(self):
        with self.assertRaisesRegex(AssertionError, "lost, leaked or duplicated"):
            invariant(State(issued=1, reserved=0, queued=0), 2)
        with self.assertRaisesRegex(AssertionError, "credit exceeded"):
            invariant(State(issued=3, queued=3), 2)

    def test_control_finalization_is_terminal_not_another_data_turn(self):
        pending = State(issued=1, reserved=1, control_pending=True)
        final = dict(next_states(pending, capacity=2, max_issued=3))["control_finalize"]
        self.assertEqual(next_states(final, capacity=2, max_issued=3), ())
        self.assertEqual(final.cancelled, 1)

    def test_invalid_model_bounds_are_rejected(self):
        for bad in (0, -1, True, 9):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                explore(capacity=bad)
        for bad in (-1, 9, True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                explore(max_issued=bad)


if __name__ == "__main__":
    unittest.main()
