"""Small bounded CONTROL-versus-DATA interleaving regression, host model only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "validation"))
from bounded_mailbox_model import State, explore, invariant, next_states


class MailboxWave31Tests(unittest.TestCase):
    def test_exhaustive_transitions_conserve_credits_under_small_budgets(self):
        for capacity in (1, 2, 3):
            for issued in (0, 1, 2, 3):
                states, edges = explore(capacity=capacity, max_issued=issued)
                self.assertTrue(states)
                for state in states:
                    invariant(state, capacity)
                for old, action, new in edges:
                    invariant(old, capacity)
                    invariant(new, capacity)
                    if action == "control_finalize":
                        self.assertTrue(new.stopped and new.control_delivered)
                        self.assertFalse(new.queued or new.reserved)
                        self.assertEqual(next_states(new, capacity=capacity,
                                                     max_issued=issued), ())

    def test_control_can_enter_at_full_data_capacity(self):
        for capacity in (1, 2, 3):
            states, _ = explore(capacity=capacity, max_issued=3)
            full = [s for s in states if not s.stopped
                    and s.queued + s.reserved == capacity and not s.control_pending]
            self.assertTrue(full)
            for state in full:
                actions = dict(next_states(state, capacity=capacity, max_issued=3))
                self.assertIn("control_arrival", actions)
                after = dict(next_states(actions["control_arrival"],
                                         capacity=capacity, max_issued=3))
                self.assertIn("control_finalize", after)

    def test_boolean_message_counter_is_never_accepted_as_credit(self):
        with self.assertRaisesRegex(AssertionError, "invalid negative message"):
            invariant(State(issued=True, reserved=True), 2)

    def test_terminal_control_state_cannot_reopen_data_lane(self):
        stopped = State(issued=2, cancelled=2, stopped=True, control_delivered=True)
        invariant(stopped, 2)
        self.assertEqual(next_states(stopped, capacity=2, max_issued=3), ())


if __name__ == "__main__":
    unittest.main()
