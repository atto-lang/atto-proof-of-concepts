"""Bounded Python mailbox model checks; not native AttoLang runtime evidence."""
import unittest

from src.validation.bounded_mailbox_model import State, explore, invariant, next_states


class BoundedControlOverData(unittest.TestCase):
    def test_full_data_admits_control_without_consuming_a_data_credit(self):
        full = State(issued=1, queued=1)
        actions = dict(next_states(full, capacity=1, max_issued=2))
        self.assertNotIn("reserve", actions)
        self.assertIn("control_arrival", actions)
        pending = actions["control_arrival"]
        self.assertEqual((pending.queued, pending.reserved), (1, 0))
        final = dict(next_states(pending, capacity=1, max_issued=2))[
            "control_finalize"
        ]
        self.assertTrue(final.stopped)
        self.assertTrue(final.control_delivered)
        self.assertEqual((final.queued, final.reserved, final.cancelled), (0, 0, 1))
        invariant(final, 1)

    def test_reserved_data_is_cancelled_on_control_finalization(self):
        reserved = State(issued=1, reserved=1)
        pending = dict(next_states(reserved, capacity=1, max_issued=2))[
            "control_arrival"
        ]
        final = dict(next_states(pending, capacity=1, max_issued=2))[
            "control_finalize"
        ]
        self.assertEqual((final.issued, final.cancelled, final.completed), (1, 1, 0))
        self.assertEqual(next_states(final, capacity=1, max_issued=2), ())

    def test_complete_small_state_graph_preserves_double_entry_accounting(self):
        states, transitions = explore(capacity=1, max_issued=2)
        self.assertTrue(states)
        self.assertTrue(transitions)
        self.assertTrue(any(action == "control_finalize" for _, action, _ in transitions))
        for source, action, successor in transitions:
            with self.subTest(action=action):
                invariant(source, 1)
                invariant(successor, 1)
                self.assertEqual(
                    successor.issued,
                    successor.reserved + successor.queued
                    + successor.completed + successor.cancelled,
                )


if __name__ == "__main__":
    unittest.main()
