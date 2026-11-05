"""Finite bounded mailbox model checks; not native actor execution or fairness proof."""
import sys
import unittest
from pathlib import Path
from dataclasses import replace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "validation"))
from bounded_mailbox_model import State, explore, invariant, next_states


class ControlLaneInterleavings(unittest.TestCase):
    def test_all_reachable_states_conserve_message_credit(self):
        for capacity in (1, 2, 3):
            for max_issued in (0, 1, 2, 3):
                with self.subTest(capacity=capacity, max_issued=max_issued):
                    states, edges = explore(capacity=capacity, max_issued=max_issued)
                    self.assertGreaterEqual(len(states), 3)
                    for state in states:
                        invariant(state, capacity)
                        self.assertLessEqual(state.queued + state.reserved, capacity)
                        if state.stopped:
                            self.assertEqual(next_states(
                                state, capacity=capacity, max_issued=max_issued), ())
                    for before, action, after in edges:
                        self.assertIn(before, states)
                        self.assertIn(after, states)
                        invariant(after, capacity)

    def test_control_admission_remains_available_at_full_data_capacity(self):
        for capacity in (1, 2, 3):
            state = State(issued=capacity, queued=capacity)
            before = dict(next_states(
                state, capacity=capacity, max_issued=capacity))
            self.assertIn("control_arrival", before)
            pending = before["control_arrival"]
            after = dict(next_states(
                pending, capacity=capacity, max_issued=capacity))
            self.assertIn("control_finalize", after)
            final = after["control_finalize"]
            self.assertTrue(final.control_delivered)
            self.assertTrue(final.stopped)
            self.assertEqual(final.cancelled, capacity)
            self.assertEqual(final.completed, 0)
            self.assertEqual(final.queued + final.reserved, 0)

    def test_reserved_and_queued_data_are_both_refunded_by_control(self):
        state = State(issued=3, reserved=2, queued=1, control_pending=True)
        final = dict(next_states(
            state, capacity=3, max_issued=3))["control_finalize"]
        self.assertEqual(final.cancelled, 3)
        self.assertEqual(final.issued, 3)
        self.assertEqual(final.reserved, 0)
        self.assertEqual(final.queued, 0)
        self.assertEqual(next_states(final, capacity=3, max_issued=3), ())

    def test_inconsistent_terminal_or_boolean_credit_is_rejected(self):
        invalid = (
            State(control_delivered=True, stopped=False),
            State(issued=1, queued=1, control_delivered=True, stopped=True),
            State(issued=True, completed=1),
            State(issued=2, completed=1),
            State(issued=1, reserved=-1, completed=2),
        )
        for state in invalid:
            with self.subTest(state=state), self.assertRaises(AssertionError):
                invariant(state, 3)

    def test_false_bounded_arguments_cannot_be_accepted_as_integers(self):
        for name, kwargs in (
            ("bool_capacity", {"capacity": True}),
            ("zero_capacity", {"capacity": 0}),
            ("large_capacity", {"capacity": 9}),
            ("bool_max", {"max_issued": False}),
            ("large_max", {"max_issued": 9}),
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                explore(**kwargs)


if __name__ == "__main__":
    unittest.main()
