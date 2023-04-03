import sqlite3
from typing import Union


class DataBase:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.create()

    def create(self):
        self.execute("""CREATE TABLE IF NOT EXISTS blacklist(
                            tg_id INTEGER NOT NULL PRIMARY KEY)""", commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS users(
                        tg_id INTEGER NOT NULL PRIMARY KEY,
                        username TEXT,
                        fullname TEXT,
                        money   INTEGER NOT NULL DEFAULT 0,
                        tuc INTEGER  NOT NULL DEFAULT 0)""",  # tuc - состоит ли в Профкоме
                     commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS admins(
                                tg_id INTEGER NOT NULL PRIMARY KEY,
                                level INTEGER)""",
                     commit=True)

    def execute(self, clause: str, *args, commit: bool = False, fetch: Union[bool, str] = False) -> Union[list, None]:
        """
        Запрос к БД SQLite
        :param clause:
        :param args: Аргументы, замещающие "?" в запросе
        :param commit:
        :param fetch: Сколько данных нужно возвращать: True | "ALL" - все, "ONE" - одну запись, False - ничего
        :return:
        """
        cur = self.con.cursor()
        executor = cur.execute(clause, args)
        if commit:
            self.con.commit()
        if fetch:
            if isinstance(fetch, str) and fetch.upper() == "ALL" or isinstance(fetch, bool) and fetch:
                data = executor.fetchall()
            elif isinstance(fetch, str) and fetch.upper() == "ONE":
                data = executor.fetchone()
            else:
                raise ValueError("Неверный fetch аргумент.")

        cur.close()

        if fetch:
            return data

    def in_blacklist(self, tg_id):
        data = self.execute("SELECT tg_id FROM blacklist WHERE tg_id = ?", tg_id, fetch="one")
        if not data:
            return False
        return True

    def get_admin_level(self, tg_id):
        data = self.execute("SELECT level FROM admins WHERE tg_id = ?", tg_id, fetch="one")
        if not data:
            return 0
        return data[0]

    def add_user(self, tg_id, username, fullname):
        self.execute("INSERT INTO users (tg_id, username, fullname) VALUES (?, ?, ?) "
                     "ON CONFLICT(tg_id) DO UPDATE SET username = ?, fullname = ?",
                     tg_id, username, fullname, username, fullname,
                     commit=True)

    def get_user_info(self, tg_id, what: str):
        return self.execute("SELECT " + what + " FROM users WHERE tg_id = ?", tg_id, fetch="ONE")

    def set_user_tuc(self, tg_id, value: int):
        self.execute("UPDATE users SET tuc = ? WHERE tg_id = ?", value, tg_id, commit=True)

    def __del__(self):
        self.con.close()


if __name__ == '__main__':
    db = DataBase("mmweek2023db.db")
