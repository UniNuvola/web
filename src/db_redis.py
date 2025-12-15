"""
Redis database manager for UniNuvola user request management.

This module provides a database manager class that interfaces with Redis
to store and manage user access requests. It handles request lifecycle
including creation, status updates, approval workflows, and LDAP synchronization.

Classes
-------
DBManager
    Manager class for Redis-based user request storage and retrieval.
"""
from datetime import datetime
import redis
import requests


class DBManager:
    """
    Redis database manager for user access requests.

    This class provides methods to manage user requests stored in Redis,
    including creating, updating, deleting, and querying requests.
    It also handles notification of the LDAP sync service when requests
    are created or approved.

    Attributes
    ----------
    logger : logging.Logger
        Logger instance for debugging and error reporting.
    REDIS_IP : str
        IP address of the Redis server.
    REDIS_PASSWORD : str
        Password for Redis authentication.
    LDAPSYNC_IP : str
        IP address of the LDAP sync service.
    LDAPSYNC_PORT : str
        Port of the LDAP sync service.
    connection : redis.Redis
        Redis connection instance.

    Parameters
    ----------
    app : Flask
        Flask application instance containing configuration attributes.
    """
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
        self.__idx = "req"
        self.__infoidx = "info"
        self.__keys = {
            "startdate": "startdate",
            "enddate": "enddate",
            "status": "status",
            "groups": "groups",
        }
        self.__request_statuses = {
            "pending": "pending",
            "approved": "approved",
            "synced": "synced",
        }

    def __notify_ldapsync(self):
        self.logger.info("NOTIFY LDAPSYNC")
        try:
            r = requests.get(
                url=f"http://{self.LDAPSYNC_IP}:{self.LDAPSYNC_PORT}")
            self.logger.debug("TRIGGERED LDAPSYNC, RESPONSE: %s", r)
        except Exception as e:
            self.logger.error("CANNOT REACH LDAPSYNC ! ERROR: %s", e)

    def __del__(self):
        self.logger.debug("Closing DB connection")
        self.connection.close()

    def __valid_user(self, user: str):
        assert user is not None
        assert user != ""

    def __request_exists(self, user: str):
        self.__valid_user(user)

        q = f"{self.__idx}:{user}:*"

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
        if status == self.__request_statuses["pending"]:
            return self.__request_statuses["approved"]

        return self.__request_statuses["pending"]

        # match status:
        #     case self.__request_statuses.get('pending'):
        #         return self.__request_statuses['approved']
        #     case self.__request_statuses.get('approved'):
        #         return self.__request_statuses['pending']

    def add_request(self, user: str):
        """
        Add a new access request for a user.

        Creates a new request entry in Redis with pending status and current
        timestamp. Prevents duplicate requests from the same user.
        Notifies the LDAP sync service after successful creation.

        Parameters
        ----------
        user : str
            Unique identifier (username) of the user making the request.

        Notes
        -----
        If the user already has an existing request, the operation is
        silently ignored and a warning is logged.
        """
        self.__valid_user(user)

        self.logger.info("NEW REQUEST FOR USER: %s", user)

        # Prevent saturating DB with a-doc crafted POST request
        # Only one request is admitted per user
        if self.__request_exists(user):
            self.logger.warning(
                "USER %s TRY TO ADD DUPLICATED REQUESTS !!", user)
            return

        self.logger.debug("NO DUPLICATED REQUEST 👍")

        self.__set_key(
            f"{self.__idx}:{user}:{self.__keys['startdate']}",
            str(datetime.now()),
        )
        self.__set_key(
            f"{self.__idx}:{user}:{self.__keys['status']}",
            self.__request_statuses["pending"],
        )

        self.__notify_ldapsync()

    def delete_request(self, user: str):
        """
        Delete a user's access request from the database.

        Removes all Redis keys associated with the user's request.
        Approved or synced requests cannot be deleted for security reasons.

        Parameters
        ----------
        user : str
            Unique identifier (username) of the user whose request
            should be deleted.

        Notes
        -----
        If the request has been approved or synced, the deletion is
        silently ignored and a warning is logged.
        """
        self.__valid_user(user)

        # an approved/synced request cannot be removed !!
        request_status = self.__get_key(
            f"{self.__idx}:{user}:{self.__keys['status']}")
        if request_status in [
            self.__request_statuses["approved"],
            self.__request_statuses["synced"],
        ]:
            self.logger.warning(
                "TRYING TO REMOVE AN APPROVED REQUEST ! Ignoring")
            return

        self.logger.info("DELETE REQUEST FOR USER: %s", user)

        q = f"{self.__idx}:{user}:*"
        self.logger.debug("DELETE SCAN QUERY: %s", q)

        for key in self.connection.scan_iter(q):
            self.__del_key(key)

    def update_request_status(self, user: str):
        """
        Toggle the status of a user's access request.

        Switches the request status between 'pending' and 'approved'.
        When approved, sets the end date and adds the user to the 'users'
        group, then notifies the LDAP sync service.

        Parameters
        ----------
        user : str
            Unique identifier (username) of the user whose request
            status should be updated.

        Raises
        ------
        AssertionError
            If the request does not exist for the given user.
        """
        self.__valid_user(user)

        self.logger.info("UPDATING USER REQUEST STATUS: %s", user)

        request_status = self.__get_key(
            f"{self.__idx}:{user}:{self.__keys['status']}")

        assert request_status is not None

        new_request_status = self.__change_status(request_status)
        self.logger.debug("NEW REQUEST STATUS: %s", new_request_status)

        self.__set_key(
            f"{self.__idx}:{user}:{self.__keys['status']}", new_request_status
        )

        if new_request_status == self.__request_statuses["approved"]:
            self.__set_key(
                f"{self.__idx}:{user}:{self.__keys['enddate']}", str(datetime.now())
            )
            self.__add_to_set(f"{self.__idx}:{user}:{
                              self.__keys['groups']}", ["users"])
            self.__notify_ldapsync()

        else:
            self.__del_key(f"{self.__idx}:{user}:{self.__keys['enddate']}")

    def get_request_data(self, user: str) -> dict[str, str]:
        """
        Retrieve all data associated with a user's request.

        Fetches the request's start date, end date, status, and groups
        from Redis and returns them as a dictionary.

        Parameters
        ----------
        user : str
            Unique identifier (username) of the user whose request
            data should be retrieved.

        Returns
        -------
        dict[str, str]
            Dictionary containing request data with keys:
            - 'startdate': Request creation timestamp
            - 'enddate': Approval timestamp (if approved)
            - 'status': Current request status
            - 'groups': Set of groups the user belongs to
            Returns empty dict if no request exists.
        """
        self.logger.info("GETTING REQUEST DATA: %s", user)

        self.__valid_user(user)

        request_data = {}
        request_empty = True

        for _, key in self.__keys.items():
            if key == self.__keys["groups"]:
                request_data[key] = self.__get_skey(
                    f"{self.__idx}:{user}:{key}")
            else:
                request_data[key] = self.__get_key(
                    f"{self.__idx}:{user}:{key}")

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
                request_data[key] = datetime.strptime(
                    request_data[key], "%Y-%m-%d %H:%M:%S.%f"
                )

            except (
                ValueError,
                TypeError,
            ):
                self.logger.error(
                    "Wrong datetime format in %s: %s",
                    f"{user}:{key}",
                    request_data[key],
                )
                request_data[key] = None

                continue

        return request_data

    def get_all_request_data(self):
        """
        Retrieve data for all user requests in the database.

        Scans all request keys in Redis and aggregates data for each
        unique user. Results are sorted by start date in descending order.

        Returns
        -------
        list[dict]
            List of dictionaries, each containing request data for a user.
            Each dictionary includes 'user', 'infos', and all request fields.
            Sorted by 'startdate' in descending order (newest first).
        """
        self.logger.info("GETTING ALL REQUESTS DATA")

        users = []
        q = f"{self.__idx}:*"
        self.logger.debug("ALL REQUESTS SCAN QUERY: %s", q)

        for key in self.connection.scan_iter(q):
            user = key.split(":")[1]
            users.append(user)

        users = set(users)
        self.logger.debug("UNIQUE USERS: %s", users)

        all_requests_data = []
        for user in users:
            request_data = self.get_request_data(user)
            request_data["user"] = user
            request_data["infos"] = self.get_user_infos(user)

            all_requests_data.append(request_data)

        return sorted(all_requests_data, key=lambda d: d["startdate"], reverse=True)

    def get_user_infos(self, user: str) -> dict:
        """
        Retrieve additional information about a user.

        Fetches user metadata stored under the info index in Redis,
        such as display name, email, or other profile information.

        Parameters
        ----------
        user : str
            Unique identifier (username) of the user whose information
            should be retrieved.

        Returns
        -------
        dict
            Dictionary containing user information key-value pairs.
            Returns empty dict if no information exists for the user.
        """
        self.logger.info("GETTING USER %s INFOS", user)

        self.__valid_user(user)

        user_infos = {}
        infos_empty = True
        infokeys = self.connection.keys(f"{self.__infoidx}:{user}:*")

        self.logger.debug("USER %s KEYS: %s", user, infokeys)

        for key in infokeys:
            dictkey = key.split(":")[-1]
            user_infos[dictkey] = self.__get_key(key)

            if user_infos[dictkey] is not None:
                infos_empty = False

        self.logger.debug("USER INFOS: %s", user_infos)

        if infos_empty:
            return {}

        return user_infos
