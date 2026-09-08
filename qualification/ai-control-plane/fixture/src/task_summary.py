"""Frozen qualification fixture with one intentional ordering defect."""


def summarize_tasks(records):
    """Return task totals and status buckets without changing ``records``."""
    completed = []
    pending = []
    for record in records:
        # Intentional frozen defects: truthiness replaces the status contract,
        # and bucket order follows input rather than the required sort order.
        if record["status"]:
            completed.append(record["id"])
        else:
            pending.append(record["id"])
    return {
        "total": len(records),
        "completed_ids": completed,
        "pending_ids": pending,
    }
