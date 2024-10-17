from datetime import datetime
import redis
import requests


class DBManager():

    def __init__(self, app):
        self.logger = app.logger
        self.REDIS_IP = app.redis_ip
        self.REDIS_PASSWORD = app.redis_password
        self.LDAPSYNC_IP = app.ldapsync_ip
        self.LDAPSYNC_PORT = app.ldapsync_port

        self.connection = redis.Redis(
            host=self.REDIS_IP,
            port=6379,
            password=self.REDIS_PASSWORD,
            decode_responses=True,
        )

        # consts
        self.__idx = 'req'
        self.__infoidx = 'info'
        self.__keys = {
            'startdate': 'startdate',
            'enddate': 'enddate',
            'status': 'status',
            'groups': 'groups',
        }
        self.__request_statuses = {
            'pending': 'pending',
            'approved': 'approved',
            'synced': 'synced',
        }

    def __notify_ldapsync(self):
        self.logger.info('NOTIFY LDAPSYNC')
        r = requests.get(url=f"{self.LDAPSYNC_IP}:{self.LDAPSYNC_PORT}")
        self.logger.debug("TRIGGERED LDAPSYNC, RESPONSE: %s", r)

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

    def __add_to_set(self, key: str, values: list):
        self.logger.debug("ADDING %s TO %s", values, key)
        self.connection.sadd(key, *values)

    def __get_key(self, key: str) -> str:
        value = self.connection.get(key)
        self.logger.debug("GET KEY: %s --> %s", key, value)

        return value

    def __get_skey(self, key: str) -> str:
        value = self.connection.smembers(key)
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

        self.__notify_ldapsync()

    def delete_request(self, user: str):
        self.__valid_user(user)

        # an approved/synced request cannot be removed !!
        request_status = self.__get_key(f'{self.__idx}:{user}:{self.__keys["status"]}')
        if request_status in [self.__request_statuses['approved'], self.__request_statuses['synced']]:
            self.logger.warning("TRYING TO REMOVE AN APPROVED REQUEST ! Ignoring")
            return

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

        if new_request_status == self.__request_statuses['approved']:
            self.__set_key(f'{self.__idx}:{user}:{self.__keys["enddate"]}', str(datetime.now()))
            self.__add_to_set(f'{self.__idx}:{user}:{self.__keys["groups"]}', ["users"])
            self.__notify_ldapsync()

        else:
            self.__del_key(f'{self.__idx}:{user}:{self.__keys["enddate"]}')

    def get_request_data(self, user: str) -> dict[str, str]:
        self.logger.info("GETTING REQUEST DATA: %s", user)

        self.__valid_user(user)

        request_data = {}
        request_empty = True

        for _, key in self.__keys.items():
            if key == self.__keys['groups']:
                request_data[key] = self.__get_skey(f'{self.__idx}:{user}:{key}')
            else:
                request_data[key] = self.__get_key(f'{self.__idx}:{user}:{key}')

            # `request_data[key]` could be `None` (because it's a string Key) or
            # `set()` (because it's a set Key), respectively generated by `__get_key()` and
            # `__get_skey`. Need to check that req. data is not None and then is not an
            # empty set.
            if request_data[key] is not None and request_data[key] != set():
                request_empty = False

        if request_empty:
            return {}

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
            request_data['infos'] = self.get_user_infos(user)

            all_requests_data.append(request_data)

        return all_requests_data

    def get_user_infos(self, user: str) -> dict:
        self.logger.info("GETTING USER %s INFOS", user)

        self.__valid_user(user)

        user_infos = {}
        infos_empty = True
        infokeys = self.connection.keys(f'{self.__infoidx}:{user}:*')

        self.logger.debug("USER %s KEYS: %s", user, infokeys)

        for key in infokeys:
            dictkey = key.split(':')[-1]
            user_infos[dictkey] = self.__get_key(key)

            if user_infos[dictkey] is not None:
                infos_empty = False

        self.logger.debug("USER INFOS: %s", user_infos)

        if infos_empty:
            return {}
        
        return user_infos
