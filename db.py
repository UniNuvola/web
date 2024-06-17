import sqlite3


class DBManager():
    __db_instance = None
    __tab_richieste = 'richieste'
    __dbfile = 'database_richieste.db'

    # TODO: introduce a db connection LazyLoad ?
    def __init__(self):
        if DBManager.__db_instance is None:
            DBManager.__db_instance = sqlite3.connect(DBManager.__dbfile)

        self.__check_db()


    def __check_db(self):
        # Check if main table exists
        c = DBManager.__db_instance.cursor()
        c.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{DBManager.__tab_richieste}' ''')

        # Table exists ! No operation needed
        if c.fetchone()[0] == 1:
            return

        # Table do not exists !
        c = DBManager.__db_instance.cursor()
        c.execute(f"CREATE TABLE {DBManager.__tab_richieste}(user, start_date, state, end_date)")

        DBManager.__db_instance.commit()

if __name__ == "__main__":
   db = DBManager() 
   # db2 = DBManager() 
