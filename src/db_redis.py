from datetime import datetime
import redis


class DBManager():

    def __init__(self, app):
        self.logger = app.logger
        self.REDIS_IP = app.redis_ip
        self.REDIS_PASSWORD = app.redis_password

        self.connection = redis.Redis(
            host=self.REDIS_IP,
            port=6379,
            password=self.REDIS_PASSWORD,
            decode_responses=True,
        )

        # consts
        self.__idx = 'req'
        self.__keys = {
            'startdate': 'startdate',
            'enddate': 'enddate',
            'status': 'status',
        }
        self.__request_statuses = {
            'pending': 'pending',
            'approved': 'approved'
        }


    def __del__(self):
        self.logger.debug("Closing DB connection")
        self.connection.close()

    def __valid_user(self, user: str):
        assert user is not None
        assert user != ''

    def __request_exists(self, user: str):
        self.__valid_user(user)

        q = f'{self.__idx}:{user}:*'

        self.logger.debug("DUPLICATE SCAN QUERY: %s", q)
        _, keys = self.connection.scan(match=q)

        self.logger.debug("FOUND %s REQUESTS", len(keys))
        if len(keys) == 0:
            return False

        return True

    def __set_key(self, key: str, value: str):
        self.logger.debug("SETTING KEY: %s --> %s", key, value)
        self.connection.set(key, value)

    def __get_key(self, key: str) -> str:
        value = self.connection.get(key)
        self.logger.debug("GET KEY: %s --> %s", key, value)

        return value

    def __del_key(self, key: str):
        self.logger.debug("DELETING KEY: %s", key)
        self.connection.delete(key)

    def __change_status(self, status: str):
        if status == self.__request_statuses['pending']:
            return self.__request_statuses['approved']

        return self.__request_statuses['pending']

        # match status:
        #     case self.__request_statuses.get('pending'):
        #         return self.__request_statuses['approved']
        #     case self.__request_statuses.get('approved'):
        #         return self.__request_statuses['pending']

    def add_request(self, user: str):
        self.__valid_user(user)

        self.logger.info("NEW REQUEST FOR USER: %s", user)

        # Prevent saturating DB with a-doc crafted POST request
        # Only one request is admitted per user
        if self.__request_exists(user):
            self.logger.warning("USER %s TRY TO ADD DUPLICATED REQUESTS !!", user)
            return

        self.logger.debug("NO DUPLICATED REQUEST 👍")

        self.__set_key(
            f'{self.__idx}:{user}:{self.__keys["startdate"]}',
            str(datetime.now()),
        )
        self.__set_key(
            f'{self.__idx}:{user}:{self.__keys["status"]}',
            self.__request_statuses['pending'],
        )

    def delete_request(self, user: str):
        self.__valid_user(user)

        self.logger.info("DELETE REQUEST FOR USER: %s", user)

        q = f'{self.__idx}:{user}:*'
        self.logger.debug("DELETE SCAN QUERY: %s", q)

        for key in self.connection.scan_iter(q):
            self.__del_key(key)

    def update_request_status(self, user: str):
        self.__valid_user(user)

        self.logger.info("UPDATING USER REQUEST STATUS: %s", user)

        request_status = self.__get_key(f'{self.__idx}:{user}:{self.__keys["status"]}')

        assert request_status is not None

        new_request_status = self.__change_status(request_status)
        self.logger.debug("NEW REQUEST STATUS: %s", new_request_status)

        self.__set_key(f'{self.__idx}:{user}:{self.__keys["status"]}', new_request_status)
        self.__set_key(f'{self.__idx}:{user}:{self.__keys["enddate"]}', str(datetime.now()))

    def get_request_data(self, user: str) -> dict[str, str]:
        self.logger.info("GETTING REQUEST DATA: %s", user)

        self.__valid_user(user)

        request_data = {}
        for _, key in self.__keys.items():
            request_data[key] = self.__get_key(f'{self.__idx}:{user}:{key}')

        # convert datetime keys from string to datetime
        for key in [self.__keys["startdate"], self.__keys["enddate"]]:
            try:
                request_data[key] = datetime.strptime(request_data[key], '%Y-%m-%d %H:%M:%S.%f')

            except (ValueError, TypeError,):
                self.logger.error("Wrong datetime format in %s: %s", f'{user}:{key}', request_data[key])
                request_data[key] = None

                continue

        return request_data

    def get_all_request_data(self):
        self.logger.info("GETTING ALL REQUESTS DATA")

        users = []
        q = f'{self.__idx}:*'
        self.logger.debug("ALL REQUESTS SCAN QUERY: %s", q)

        for key in self.connection.scan_iter(q):
            user = key.split(":")[1]
            users.append(user)

        users = set(users)
        self.logger.debug("UNIQUE USERS: %s", users)

        all_requests_data = []
        for user in users:
            request_data = self.get_request_data(user)
            request_data['user'] = user

            all_requests_data.append(request_data)

        return all_requests_data
