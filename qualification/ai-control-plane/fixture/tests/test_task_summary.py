from copy import deepcopy
import unittest

from src.task_summary import summarize_tasks


class TaskSummaryTests(unittest.TestCase):
    def test_status_buckets_are_exact_and_input_is_preserved(self):
        records = [
            {"id": "task-z", "status": "pending"},
            {"id": "task-b", "status": "completed"},
            {"id": "task-a", "status": "completed"},
            {"id": "task-c", "status": "pending"},
        ]
        before = deepcopy(records)
        self.assertEqual(
            summarize_tasks(records),
            {
                "total": 4,
                "completed_ids": ["task-a", "task-b"],
                "pending_ids": ["task-c", "task-z"],
            },
        )
        self.assertEqual(records, before)

    def test_buckets_are_sorted(self):
        self.assertEqual(
            summarize_tasks([
                {"id": "task-z", "status": "completed"},
                {"id": "task-a", "status": "completed"},
            ])["completed_ids"],
            ["task-a", "task-z"],
        )

    def test_unknown_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown task status"):
            summarize_tasks([{"id": "task-x", "status": "cancelled"}])


if __name__ == "__main__":
    unittest.main()
