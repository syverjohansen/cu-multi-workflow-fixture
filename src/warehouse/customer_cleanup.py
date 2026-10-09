"""A conventional function-composed customer cleanup flow."""

from typing import Any

from .sql_helpers import fetch_rows, replace_rows


def extract_customers(connection: Any) -> list[tuple[str, str]]:
    return fetch_rows(connection, "SELECT customer_id, email FROM raw_customers")


def normalize_customers(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [
        (customer_id.strip().upper(), email.strip().lower())
        for customer_id, email in rows
    ]


def load_clean_customers(connection: Any, rows: list[tuple[str, str]]) -> None:
    replace_rows(
        connection,
        delete_statement="DELETE FROM clean_customers",
        insert_statement=(
            "INSERT INTO clean_customers (customer_id, email) VALUES (?, ?)"
        ),
        rows=rows,
    )


def run_customer_cleanup(connection: Any) -> None:
    customers = extract_customers(connection)
    normalized = normalize_customers(customers)
    load_clean_customers(connection, normalized)
