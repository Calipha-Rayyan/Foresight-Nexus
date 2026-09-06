"""Thin repository layer so pages depend on stable function names rather
than a specific storage backend — swapping SQLite for PostgreSQL later only
requires changes here."""
from database.sqlite_manager import save_settings_snapshot, latest_settings_snapshot
from database import duckdb_manager


class SettingsRepository:
    @staticmethod
    def save(settings_dict: dict) -> None:
        save_settings_snapshot(settings_dict)

    @staticmethod
    def load_latest() -> dict | None:
        return latest_settings_snapshot()


class SalesRepository:
    @staticmethod
    def load(df) -> None:
        duckdb_manager.load_dataframe(df, table_name="sales")

    @staticmethod
    def category_totals():
        return duckdb_manager.category_totals()

    @staticmethod
    def product_summary():
        return duckdb_manager.product_summary()
