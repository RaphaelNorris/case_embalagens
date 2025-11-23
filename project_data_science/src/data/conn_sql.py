"""
SQL Server database connection utilities.
Supports multiple connection methods (pymssql, pyodbc) with automatic fallback.
"""

from contextlib import contextmanager
from typing import Any, Generator, Optional, Tuple

import pandas as pd

from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


class SQLServerConnectionError(Exception):
    """Custom exception for SQL Server connection errors."""

    pass


def get_connection_sqlserver() -> Tuple[Optional[Any], Optional[str]]:
    """
    Establish a connection to SQL Server using multiple drivers.

    Tries the following methods in order:
    1. pymssql (preferred)
    2. pyodbc with various drivers

    Returns:
        Tuple of (connection, method_used) or (None, None) if all methods fail
    """
    config = get_config()
    sqlserver = config.sqlserver

    # Try pymssql first
    try:
        import pymssql

        logger.debug("Attempting connection via pymssql...")
        conn = pymssql.connect(
            server=sqlserver.host,
            user=sqlserver.user,
            password=sqlserver.password,
            database=sqlserver.database,
            timeout=10,
        )
        logger.info("Successfully connected to SQL Server via pymssql")
        return conn, "pymssql"
    except ImportError:
        logger.debug("pymssql not available")
    except Exception as e:
        logger.debug(f"pymssql connection failed: {str(e)[:100]}")

    # Try pyodbc with different drivers
    try:
        import pyodbc

        drivers = [
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0",
            "FreeTDS",
            "SQL Server",
        ]

        for driver in drivers:
            try:
                logger.debug(f"Attempting connection via pyodbc with {driver}...")
                conn_string = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={sqlserver.host};"
                    f"DATABASE={sqlserver.database};"
                    f"UID={sqlserver.user};"
                    f"PWD={sqlserver.password};"
                    f"TrustServerCertificate=yes;"
                )
                conn = pyodbc.connect(conn_string, timeout=10)
                logger.info(f"Successfully connected to SQL Server via pyodbc + {driver}")
                return conn, "pyodbc"
            except Exception as e:
                logger.debug(f"pyodbc with {driver} failed: {str(e)[:100]}")
                continue
    except ImportError:
        logger.debug("pyodbc not available")

    logger.error("All SQL Server connection methods failed")
    return None, None


def get_connection() -> Any:
    """
    Create a connection to SQL Server.

    Returns:
        SQL Server connection object

    Raises:
        SQLServerConnectionError: If connection fails
    """
    conn, method = get_connection_sqlserver()
    if conn is None:
        raise SQLServerConnectionError("Failed to connect to SQL Server with all available methods")
    return conn


def query_sqlserver(query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
    """
    Execute a SQL query on SQL Server.

    Args:
        query: SQL query to execute
        params: Optional tuple of parameters for the query

    Returns:
        DataFrame with query results

    Raises:
        SQLServerConnectionError: If query execution fails
    """
    conn = None
    try:
        conn, method = get_connection_sqlserver()
        if not conn:
            raise SQLServerConnectionError("Could not establish SQL Server connection")

        if params:
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(query, conn)

        logger.info(f"Query executed successfully, returned {len(df)} rows")
        return df

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise SQLServerConnectionError(f"Query execution failed: {e}") from e
    finally:
        if conn:
            conn.close()
            logger.debug("Closed SQL Server connection")


def query_sqlserver_safe(query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
    """
    Execute a SQL query on SQL Server safely (returns empty DataFrame on failure).

    Args:
        query: SQL query to execute
        params: Optional tuple of parameters for the query

    Returns:
        DataFrame with query results or empty DataFrame on failure
    """
    try:
        return query_sqlserver(query, params)
    except Exception as e:
        logger.error(f"Query failed (safe mode): {e}")
        return pd.DataFrame()


def build_filtered_query(
    table_name: str,
    schema: str = "dbo",
    filters: Optional[dict] = None,
    columns: Optional[list] = None,
) -> Tuple[str, Tuple]:
    """
    Build a dynamic SQL query with column selection and parameterized filters.

    Args:
        table_name: Name of the table to query
        schema: Database schema (default: 'dbo')
        filters: Dictionary of column:value pairs for WHERE clause
        columns: List of columns to select (default: all columns)

    Returns:
        Tuple of (query_string, parameters_tuple)

    Example:
        >>> query, params = build_filtered_query(
        ...     'tb_pedidos',
        ...     filters={'status': 'active', 'year': 2024},
        ...     columns=['id', 'date', 'value']
        ... )
    """
    # Select columns
    if columns:
        select_clause = ", ".join(columns)
    else:
        select_clause = "*"

    # Build base query
    query = f"SELECT {select_clause} FROM {schema}.{table_name}"

    # Build WHERE clause
    params = []
    if filters:
        conditions = []
        for col, value in filters.items():
            conditions.append(f"{col} = ?")
            params.append(value)
        query += " WHERE " + " AND ".join(conditions)

    return query, tuple(params)


@contextmanager
def sqlserver_connection() -> Generator[Any, None, None]:
    """
    Context manager for SQL Server database connections.

    Yields:
        SQL Server database connection

    Example:
        >>> with sqlserver_connection() as conn:
        ...     df = pd.read_sql("SELECT * FROM table", conn)
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        logger.error(f"Error in SQL Server connection context: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Closed SQL Server connection")


if __name__ == "__main__":
    # Test connection
    logger.info("Testing SQL Server connection...")
    try:
        df = query_sqlserver("SELECT COUNT(*) as total FROM dbo.Clientes")
        logger.info(f"Connection successful! Total clients: {df.iloc[0]['total']}")
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
