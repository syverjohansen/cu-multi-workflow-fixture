"""Explicitly registered daily order summary workflow."""

from collections.abc import Iterable
from typing import Any

from .runtime import Registry, Step
from .sql_helpers import fetch_rows, replace_rows


def read_raw_orders(connection: Any) -> list[tuple[str, float]]:
    return fetch_rows(connection, "SELECT order_date, amount FROM raw_orders")


def build_order_summary(
    orders: Iterable[tuple[str, float]],
) -> list[tuple[str, int, float]]:
    totals: dict[str, tuple[int, float]] = {}
    for order_date, amount in orders:
        count, gross_amount = totals.get(order_date, (0, 0.0))
        totals[order_date] = (count + 1, gross_amount + float(amount))
    return [
        (order_date, count, round(gross_amount, 2))
        for order_date, (count, gross_amount) in sorted(totals.items())
    ]


def write_order_summary(connection_and_rows: tuple[Any, list[tuple[str, int, float]]]) -> Any:
    connection, rows = connection_and_rows
    replace_rows(
        connection,
        delete_statement="DELETE FROM order_summary",
        insert_statement=(
            "INSERT INTO order_summary (order_date, order_count, gross_amount) "
            "VALUES (?, ?, ?)"
        ),
        rows=rows,
    )
    return connection


daily_orders_registry = Registry()
daily_orders_registry.register(
    "daily_order_summary",
    [
        Step("read_raw_orders", read_raw_orders),
        Step("build_order_summary", build_order_summary, after=("read_raw_orders",)),
        Step("write_order_summary", write_order_summary, after=("build_order_summary",)),
    ],
)
