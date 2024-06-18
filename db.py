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

    def get_request_status(self, user: str, admin=False):
        assert user is not None
        assert user != ''
        
        with sqlite3.connect(DBManager.__dbfile) as conn:
            conn.row_factory = self.__dict_factory

            c = conn.cursor()
            c.execute(f"SELECT * FROM {DBManager.__tab_richieste} WHERE user = ?", (user,))

            rows = c.fetchall()
            c.close()

            if not admin:
                assert len(rows) <= 1

            return rows

if __name__ == "__main__":
    db = DBManager() 
    db.add_request('alice.alice@alice.it')
    db.get_request_status("alice.alice@alice.it")
   # db2 = DBManager() 
