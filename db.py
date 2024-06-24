import sqlite3
from datetime import datetime
from typing import Dict, List, Any


# TODO: gestione loggign (passare instanza app ?)
class DBManager():
    """Database manager.

    This class is responsible for managing the database and interacting with users (admins or users).
    It provides methods with presets for queries such as updating, removing, and approving a request.
    """

    __tab_richieste = 'richieste'
    __dbfile = 'database_richieste.db'


    def __init__(self):
        self.__check_db()

    def __check_db(self):
        """Check database status.

        This function checks for the existence of the database and,
        if necessary, creates a new instance (file) with the corresponding table.

        Parameters
        ----------
            

        Returns
        -------

        """

        with sqlite3.connect(DBManager.__dbfile) as conn:
            # Check if main table exists
            c = conn.cursor()
            c.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{DBManager.__tab_richieste}' ''')

            # Table exists ! No operation needed
            if c.fetchone()[0] == 1:
                c.close()
                return
            
            c.close()

            # Table do not exists !
            # TODO: potrebbe essere migliorato usando un file SQL che definisce la struttura
            c = conn.cursor()
            c.execute(f"CREATE TABLE {DBManager.__tab_richieste}(user, start_date, state, end_date)")

            conn.commit()
            c.close()

    def __dict_factory(self, cursor: sqlite3.Cursor , row: List) -> Dict[str, Any]:
        """Set the query return as a dict.

        This function modifies the type of return of the SQL query from list to dictionary.
        The returned dictionary is composed as follows:
            
            key: COLUMN NAME        value: COLUMN VALUE

        Parameters
        ----------
        cursor: sqlite3.Cursor : Query cursor 
        row   : List           : Actual row

        Returns
        -------
        Dict version of current row
        """

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def add_request(self, user: str):
        """ Insert a single user request into the database

        This function adds a new user request to the database by setting the necessary fields as
        'user', 'start_date', etc. The function prevents adding multiple requests
        for a single user: before adding the request to the db it checks if there are other requests
        from the same user (there will be at most one), and terminates the execution.

        Parameters
        ----------
        user: str : unique ID of the user who makes the request
            

        Returns
        -------

        """

        assert user is not None
        assert user != ''

        with sqlite3.connect(DBManager.__dbfile) as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()

            # Prevent saturating DB with a-doc crafted POST request
            # Only one request is admitted per user
            if len(rows) != 0:
                c.close()

                return

            # WARNING:  DeprecationWarning: The default datetime adapter is deprecated as of Python 3.12;
            #           see the sqlite3 documentation for suggested replacement recipes
            c.execute(f"INSERT INTO {DBManager.__tab_richieste} VALUES(?, ?, ?, ?)", (user, datetime.now(), 0, None))
            c.close()
            conn.commit()

    def delete_request(self, user: str):
        """ Removes a user request from the database

        Parameters
        ----------
        user: str : unique ID of the user who makes the request
            

        Returns
        -------

        """

        assert user is not None
        assert user != ''

        with sqlite3.connect(DBManager.__dbfile) as conn:
            c = conn.cursor()
            c.execute(f"DELETE FROM {DBManager.__tab_richieste} WHERE user = ?", (user, ))
            c.close()
            conn.commit()

    def update_request_status(self, user: str):
        """ Updates the user's request status

        This function updates the status of the user's request passed as input.
        The update of the request is done by reversing its current state.

        For example:
            - If the current request is in 'Pending' (0) state, it will be modified to 'Approved' (1)
              and the approval date will be set.

            - If the current request is in 'Approved' (1) state, it will be modified to 'Pending' (0)
              and the approval date will be removed.

        Parameters
        ----------
        user: str : unique ID of the user's request to update
            

        Returns
        -------

        """

        assert user is not None
        assert user != ''

        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT state FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()
            c.close()
            
            # only one request per user must exists !
            assert len(rows) == 1
            req_status = rows[0]['state']
            new_req_status = (req_status + 1)%2 # update state: if 0 --> 1. if 1 --> 0

            new_date = datetime.now() if new_req_status else None

            c = conn.cursor()
            c.execute(f"UPDATE {DBManager.__tab_richieste} SET state=?, end_date=? WHERE user = ?", (new_req_status, new_date, user,))
            c.close()
            conn.commit()

    def get_request_status(self, user: str) -> Dict[str, Any]:
        """Get the user's request status.

        Parameters
        ----------
        user: str : unique ID of the user who makes the request
            

        Returns
        -------
        Dict with request values or empty Dict
        """

        assert user is not None
        assert user != ''
        
        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT * FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()
            c.close()

            assert len(rows) <= 1

            return rows[0] if len(rows) == 1 else [] # TODO: 'else' dovrebbe ritornare {} (dict vuoto)

    def get_all_requests_status(self) -> Dict[str, Any]:
        """Get all user's requests status.

        This function is Admin role only.

        Parameters
        ---------- 

        Returns
        -------
        Dict with requests values or empty Dict
        """

        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT * FROM {DBManager.__tab_richieste}")

            rows = c.fetchall()
            c.close()

            return rows


if __name__ == "__main__":
    db = DBManager() 
    # db.delete_request("alice.alice@alice.it")
    # db.add_request('alice.alice@alice.it')
    # db.add_request('bob.bob@bob.it')
    # print(db.get_request_status("alice.alice@alice.it"))
    # print(db.get_all_requests_status())
    # db.delete_request("alice.alice@alice.it")
    # db.update_request_status("alice.alice@alice.it")
    # print(db.get_all_requests_status())
