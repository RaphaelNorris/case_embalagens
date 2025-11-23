"""
Oracle database connection utilities.
Provides connection functions for different data layers (RAW, TRUSTED, REFINED).
"""

from contextlib import contextmanager
from typing import Generator

import oracledb

from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


class OracleConnectionError(Exception):
    """Custom exception for Oracle connection errors."""

    pass


def connect_oracle(user: str, password: str) -> oracledb.Connection:
    """
    Create a connection to Oracle database.

    Args:
        user: Database username
        password: Database password

    Returns:
        Oracle database connection

    Raises:
        OracleConnectionError: If connection fails
    """
    config = get_config()
    oracle_config = config.oracle

    try:
        logger.info(
            f"Connecting to Oracle database at {oracle_config.host}:{oracle_config.port}"
        )

        connection = oracledb.connect(
            user=user,
            password=password,
            host=oracle_config.host,
            port=oracle_config.port,
            service_name=oracle_config.service_name,
        )

        logger.info(f"Successfully connected to Oracle as user: {user}")
        return connection

    except oracledb.Error as e:
        error_msg = f"Failed to connect to Oracle database: {e}"
        logger.error(error_msg)
        raise OracleConnectionError(error_msg) from e


def connect_oracle_raw() -> oracledb.Connection:
    """
    Connect to Oracle RAW layer.

    Returns:
        Oracle connection to RAW layer
    """
    config = get_config()
    logger.debug("Connecting to Oracle RAW layer")
    return connect_oracle(config.oracle.raw_user, config.oracle.raw_password)


def connect_oracle_trusted() -> oracledb.Connection:
    """
    Connect to Oracle TRUSTED layer.

    Returns:
        Oracle connection to TRUSTED layer
    """
    config = get_config()
    logger.debug("Connecting to Oracle TRUSTED layer")
    return connect_oracle(config.oracle.trusted_user, config.oracle.trusted_password)


def connect_oracle_refined() -> oracledb.Connection:
    """
    Connect to Oracle REFINED layer.

    Returns:
        Oracle connection to REFINED layer
    """
    config = get_config()
    logger.debug("Connecting to Oracle REFINED layer")
    return connect_oracle(config.oracle.refined_user, config.oracle.refined_password)


@contextmanager
def oracle_connection(layer: str = "trusted") -> Generator[oracledb.Connection, None, None]:
    """
    Context manager for Oracle database connections.

    Args:
        layer: Data layer to connect to ('raw', 'trusted', or 'refined')

    Yields:
        Oracle database connection

    Example:
        >>> with oracle_connection('trusted') as conn:
        ...     df = pd.read_sql("SELECT * FROM table", conn)
    """
    connection_map = {
        "raw": connect_oracle_raw,
        "trusted": connect_oracle_trusted,
        "refined": connect_oracle_refined,
    }

    if layer not in connection_map:
        raise ValueError(f"Invalid layer: {layer}. Must be one of {list(connection_map.keys())}")

    conn = None
    try:
        conn = connection_map[layer]()
        yield conn
    except Exception as e:
        logger.error(f"Error in Oracle connection context: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug(f"Closed Oracle connection to {layer} layer")
