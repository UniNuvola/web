"""
Test module for the UniNuvola Redis database manager.

This module contains test functions for verifying the functionality
of the DBManager class with Redis backend. It tests request creation,
status updates, data retrieval, and deletion operations.

Usage
-----
Run this module directly to execute the Redis database tests:
    python tests.py
"""
import logging
import os

from dotenv import load_dotenv
from flask import Flask

from src.db_redis import DBManager


def main():
    """
    Initialize the Flask application and run Redis database tests.

    Loads environment variables, configures logging, and executes
    the Redis database test suite.
    """
    load_dotenv()

    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)

    app = Flask(__name__)

    test_redisdb(app, logger)


def test_redisdb(app, logger):
    """
    Test the Redis database manager functionality.

    Performs a series of operations to verify that the DBManager
    correctly handles request creation, status updates, data retrieval,
    and deletion.

    Parameters
    ----------
    app : Flask
        Flask application instance with Redis configuration.
    logger : logging.Logger
        Logger instance for test output.

    Notes
    -----
    This function creates test requests for users 'lello' and 'pippo',
    then cleans up by deleting them after testing.
    """
    app.redis_ip = os.getenv('REDIS_IP')
    app.redis_password = os.getenv('REDIS_PASSWORD')
    app.logger = logger

    dbms = DBManager(app)
    dbms.add_request('lello')

    dbms.update_request_status('lello')
    print(dbms.get_request_data('lello'))

    dbms.add_request('pippo')

    print(dbms.get_all_request_data())

    dbms.delete_request('lello')
    dbms.delete_request('pippo')


if __name__ == "__main__":
    main()
