import sqlite3
import unittest

from warehouse.customer_cleanup import run_customer_cleanup
from warehouse.daily_orders import (
    build_order_summary,
    daily_orders_registry,
    read_raw_orders,
    write_order_summary,
)
from warehouse.notifications import completion_message


class WarehouseJobsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.executescript(
            """
            CREATE TABLE raw_orders (order_date TEXT, amount REAL);
            CREATE TABLE order_summary (
                order_date TEXT,
                order_count INTEGER,
                gross_amount REAL
            );
            CREATE TABLE raw_customers (customer_id TEXT, email TEXT);
            CREATE TABLE clean_customers (customer_id TEXT, email TEXT);
            """
        )

    def tearDown(self) -> None:
        self.connection.close()

    def test_registered_order_workflow_has_explicit_dependencies(self) -> None:
        workflow = daily_orders_registry.workflows["daily_order_summary"]
        self.assertEqual(
            [step.name for step in workflow.steps],
            ["read_raw_orders", "build_order_summary", "write_order_summary"],
        )
        self.assertEqual(workflow.steps[2].after, ("build_order_summary",))

    def test_order_summary_reads_raw_orders_and_writes_summary(self) -> None:
        self.connection.executemany(
            "INSERT INTO raw_orders VALUES (?, ?)",
            [("2026-10-08", 10.0), ("2026-10-08", 7.5)],
        )
        orders = read_raw_orders(self.connection)
        summary = build_order_summary(orders)
        write_order_summary((self.connection, summary))
        self.assertEqual(
            self.connection.execute("SELECT * FROM order_summary").fetchall(),
            [("2026-10-08", 2, 17.5)],
        )

    def test_customer_cleanup_is_a_separate_composed_flow(self) -> None:
        self.connection.execute(
            "INSERT INTO raw_customers VALUES (?, ?)",
            (" c-100 ", " USER@EXAMPLE.COM "),
        )
        run_customer_cleanup(self.connection)
        self.assertEqual(
            self.connection.execute("SELECT * FROM clean_customers").fetchall(),
            [("C-100", "user@example.com")],
        )

    def test_notification_formatting_is_independent(self) -> None:
        self.assertEqual(
            completion_message("daily orders", 2),
            "daily orders completed: 2 rows affected",
        )


if __name__ == "__main__":
    unittest.main()
