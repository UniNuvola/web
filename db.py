import sqlite3
from datetime import datetime


# TODO: gestione loggign (passare instanza app ?)
class DBManager():
    __db_instance = None
    __tab_richieste = 'richieste'
    __dbfile = 'database_richieste.db'

    # TODO: introduce a db connection LazyLoad ?
    # TODO: db name as input or others ?
    def __init__(self):
        if DBManager.__db_instance is None:
            DBManager.__db_instance = sqlite3.connect(DBManager.__dbfile)

        self.__check_db()

    def __check_db(self):
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
            c = conn.cursor()
            c.execute(f"CREATE TABLE {DBManager.__tab_richieste}(user, start_date, state, end_date)")

            conn.commit()
            c.close()

    def __dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def add_request(self, user: str):
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
        assert user is not None
        assert user != ''

        with sqlite3.connect(DBManager.__dbfile) as conn:
            c = conn.cursor()
            c.execute(f"DELETE FROM {DBManager.__tab_richieste} WHERE user = ?", (user, ))
            c.close()
            conn.commit()

    def update_request_status(self, user: str):
        assert user is not None
        assert user != ''

        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT state FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()
            c.close()

            assert len(rows) == 1
            req_status = rows[0]['state']
            new_req_status = (req_status + 1)%2

            new_date = datetime.now() if new_req_status else None

            c = conn.cursor()
            c.execute(f"UPDATE {DBManager.__tab_richieste} SET state=?, end_date=? WHERE user = ?", (new_req_status, new_date, user,))
            c.close()
            conn.commit()

    def get_request_status(self, user: str):
        assert user is not None
        assert user != ''
        
        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT * FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()
            c.close()

            assert len(rows) <= 1

            return rows[0] if len(rows) == 1 else []

    def get_all_requests_status(self):
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
