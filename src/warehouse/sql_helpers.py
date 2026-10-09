"""Shared DB-API helpers used by warehouse jobs."""

from collections.abc import Iterable, Sequence
from typing import Any


def fetch_rows(connection: Any, statement: str) -> list[tuple[Any, ...]]:
    return list(connection.execute(statement).fetchall())


def replace_rows(
    connection: Any,
    *,
    delete_statement: str,
    insert_statement: str,
    rows: Iterable[Sequence[Any]],
) -> None:
    connection.execute(delete_statement)
    connection.executemany(insert_statement, rows)
    connection.commit()
