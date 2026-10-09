"""Unrelated presentation helper for operational messages."""


def completion_message(job_name: str, affected_rows: int) -> str:
    noun = "row" if affected_rows == 1 else "rows"
    return f"{job_name} completed: {affected_rows} {noun} affected"
