"""Frozen qualification fixture with one intentional ordering defect."""


def summarize_tasks(records):
    """Return task totals and status buckets without changing ``records``."""
    completed = []
    pending = []
    for record in records:
        status = record["status"]
        if status == "completed":
            completed.append(record["id"])
        elif status == "pending":
            pending.append(record["id"])
        else:
            raise ValueError(f"unknown task status: {status}")
    return {
        "total": len(records),
        "completed_ids": sorted(completed),
        "pending_ids": sorted(pending),
    }
