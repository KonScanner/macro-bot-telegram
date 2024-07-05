import logging
import os
from typing import Literal, Union

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker



def get_session_factory(
    db_uri: str="",
    pool_size: int = 5,
    max_overflow: int = 32,
    autoflush: bool = False,
    echo: Union[None, bool, Literal["debug"]] = None,
) -> sessionmaker:
    """
    Create a session factory.

    :param db_uri: The URI for the database connection.
    :param pool_size: The size of the connection pool. Default is 5.
    :param max_overflow: The maximum overflow size of the connection pool. Default is 32.
    :param autoflush: Whether to autoflush changes. Default is False.

    :return A session factory for creating database sessions.
    """
    load_dotenv()
    db_uri_replacement = os.getenv("DB_URI")
    if not db_uri:
        db_uri = db_uri_replacement if db_uri_replacement else ""
        logging.debug(f"DB_URI not found, replacing with {db_uri}")
    if pool_size < 0:
        raise ArgumentError("Pool size cannot be negative")

    if max_overflow < 0:
        raise ArgumentError("Max overflow cannot be negative")

    try:
        engine = create_engine(
            db_uri,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=echo,
            echo_pool=echo,
        )
    except Exception as e:
        logging.error(f"Error creating engine: {e}")
        raise

    logging.debug("Session factory created with URI: %s", db_uri)
    return sessionmaker(bind=engine, autoflush=autoflush)

def get_unique_hashes(session) -> set:
    """
    Get all unique hashes from the database.

    :param session: The database session.

    :return A set of all the unique hashes.
    """
    query = text("SELECT distinct hash FROM core.macro_events;")
    
    try:
        return {row.hash for row in session.execute(query)}
    except Exception as e:
        logging.error(f"Error reading hashes from the database: {e}")
        return set()