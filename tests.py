import logging
import os
from flask import Flask
from src.db_redis import DBManager
from dotenv import load_dotenv


def main():
    load_dotenv()

    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)

    app = Flask(__name__)

    test_redisdb(app, logger)


def test_redisdb(app, logger):
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
