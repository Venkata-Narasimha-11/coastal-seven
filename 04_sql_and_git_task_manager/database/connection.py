"""PostgreSQL Database Connection and Schema Management using psycopg2."""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

import config

logger = logging.getLogger("TaskManager.Database")


class DatabaseConnection:
    """Manages PostgreSQL connection pooling and transactional execution."""

    _instance: Optional["DatabaseConnection"] = None

    def __init__(self, db_config: Optional[dict] = None) -> None:
        """Initialize connection manager with configuration dictionary."""
        self.config = db_config or config.get_db_config()
        self._connection: Optional[PgConnection] = None

    @classmethod
    def get_instance(cls, db_config: Optional[dict] = None) -> "DatabaseConnection":
        """Singleton accessor for shared database connection."""
        if cls._instance is None:
            cls._instance = cls(db_config)
        return cls._instance

    def connect(self) -> PgConnection:
        """Establish or return an active connection to PostgreSQL."""
        try:
            if self._connection is None or self._connection.closed != 0:
                logger.debug(
                    "Connecting to PostgreSQL at %s:%s dbname=%s",
                    self.config["host"],
                    self.config["port"],
                    self.config["dbname"],
                )
                self._connection = psycopg2.connect(**self.config)
            return self._connection
        except psycopg2.OperationalError as e:
            logger.error("Failed to connect to PostgreSQL: %s", e)
            raise ConnectionError(
                f"Could not connect to PostgreSQL on {self.config['host']}:{self.config['port']}. "
                f"Ensure PostgreSQL is running. Details: {e}"
            ) from e

    def close(self) -> None:
        """Close the underlying connection if open."""
        if self._connection and self._connection.closed == 0:
            self._connection.close()
            logger.debug("PostgreSQL connection closed.")

    @contextmanager
    def get_cursor(self, dict_cursor: bool = True) -> Generator:
        """Context manager providing a transactional cursor.
        
        Commits upon normal completion; rolls back on unhandled exceptions.
        """
        conn = self.connect()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Transaction rolled back due to error: %s", e)
            raise
        finally:
            cursor.close()

    def init_schema(self, schema_path: Optional[Path] = None) -> None:
        """Execute the SQL schema DDL file to build tables, constraints, and indexes."""
        if schema_path is None:
            schema_path = Path(__file__).resolve().parent / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        logger.info("Initializing database schema from %s", schema_path)
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with self.get_cursor(dict_cursor=False) as cur:
            cur.execute(sql_script)
        logger.info("Database schema initialized successfully.")

    def ping(self) -> bool:
        """Verify database connectivity with a lightweight ping query."""
        try:
            with self.get_cursor(dict_cursor=False) as cur:
                cur.execute("SELECT 1;")
                row = cur.fetchone()
                return bool(row and row[0] == 1)
        except Exception as e:
            logger.warning("Ping failed: %s", e)
            return False


def get_db_connection(db_config: Optional[dict] = None) -> DatabaseConnection:
    """Convenience helper to retrieve database connection instance."""
    return DatabaseConnection.get_instance(db_config)
