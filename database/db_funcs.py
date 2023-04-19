import asyncio
import itertools
import random
import sqlite3
import string
from typing import Union
import datetime as dt
from fuzzywuzzy import fuzz

import constants
from middleware import texts

from functions import registration_functions


class DataBase:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.create()

    def create(self):
        self.execute("""CREATE TABLE IF NOT EXISTS users(
                        tg_id INTEGER NOT NULL PRIMARY KEY,
                        username TEXT,
                        fullname TEXT NOT NULL,
                        money   INTEGER NOT NULL DEFAULT 0,
                        tuc INTEGER  NOT NULL DEFAULT 0,
                        enter_code TEXT UNIQUE);""",  # tuc - состоит ли в Профкоме
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS blacklist(
                                    tg_id INTEGER NOT NULL PRIMARY KEY);""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS events (
                            id   INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            reward INTEGER NOT NULL,
                            description TEXT,
                            datetime TEXT NOT NULL, 
                            img_path TEXT,
                            img_id TEXT,
                            button_text TEXT,
                            button_url TEXT,
                            release INTEGER DEFAULT 0                        
                        );
                        """,
                     commit=True
                     )
        self.execute("""CREATE TABLE IF NOT EXISTS admins (
                            tg_id    INTEGER NOT NULL
                                             PRIMARY KEY,
                            level    INTEGER,
                            event_id INTEGER
                            );""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS stuff (
                            id            INTEGER PRIMARY KEY AUTOINCREMENT,
                            name          TEXT,
                            description   TEXT,
                            not_tuc_price INTEGER,
                            tuc_price     INTEGER,
                            img_path      TEXT,
                            count         INTEGER NOT NULL
                            );""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS purchases (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            tg_id    INTEGER NOT NULL
                                             REFERENCES users (tg_id),
                            stuff_id INTEGER NOT NULL
                                             REFERENCES stuff (id),
                            count    INTEGER NOT NULL,
                            cost     INTEGER NOT NULL,
                            UNIQUE (
                                tg_id,
                                stuff_id
                            )
                        );""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS tuc_list (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            fullname UNIQUE NOT NULL
                        );""", commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS texts(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        content TEXT);
                        """, commit=True)
        self.execute("""INSERT INTO texts (name, content) VALUES 
                        ("help",  "На неделе профкома...")
                        ON CONFLICT DO NOTHING""", commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS promo(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        money INTEGER NOT NULL,
                        can_use INTEGER NOT NULL,
                        used INTEGER NOT NULL DEFAULT 0,
                        time_registered TEXT NOT NULL,
                        time_ends TEXT NOT NULL);""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS promo_usages(
                                promo_id TEXT NOT NULL,
                                tg_id INTEGER NOT NULL,
                                datetime TEXT NOT NULL,
                                CONSTRAINT was PRIMARY KEY (promo_id, tg_id));""",
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

    def add_event(self, name, datetime, reward, description=None, img_path=None, img_id=None):
        self.execute("INSERT INTO events (name, description, reward, datetime, img_path, img_id)"
                     "VALUES (?, ?, ?, ?, ?, ?)",
                     name,
                     description,
                     reward,
                     dt.datetime.strftime(datetime,
                                          texts.DATE_TIME_TEMPLATE),
                     img_path,
                     img_id,
                     commit=True)

    def get_events_summary(self, show_all=False):
        if show_all:
            res = self.execute("SELECT id, name, datetime FROM events", fetch=True)
        else:
            res = self.execute("SELECT id, name, datetime  FROM events WHERE release = 1", fetch=True)
        # Меняем строковую дату на datetime
        return list(map(lambda x: (x[0], x[1], dt.datetime.strptime(x[2], texts.DATE_TIME_TEMPLATE)), res))

    def get_event(self, event_id) -> Union[dict, None]:
        res = self.execute("SELECT name, datetime, description, img_path, img_id, release, button_text, button_url  "
                           "FROM events "
                           "WHERE id = ?",
                           event_id,
                           fetch="one")
        if not res:
            return None
        name, datetime, description, img_path, img_id, release, button_text, button_url = res
        return {
            "name": name,
            "datetime": dt.datetime.strptime(datetime, texts.DATE_TIME_TEMPLATE),
            "description": description,
            "img_path": img_path,
            "img_id": img_id,
            "button_text": button_text,
            "button_url": button_url
        }

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

    def add_user(self, tg_id, username, fullname, tuc=0):
        self.execute("INSERT INTO users (tg_id, username, fullname, tuc) VALUES (?, ?, ?, ?) "
                     "ON CONFLICT(tg_id) DO UPDATE SET username = ?, fullname = ?, tuc = ?",
                     tg_id, username, fullname, tuc, username, fullname, tuc,
                     commit=True)

    def get_text(self, name):
        res = self.execute("SELECT content FROM texts WHERE name = ?", name, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_help_text(self):
        return self.get_text("help")

    def get_user_info(self, tg_id, what: str):
        """
        Вытаскивает заданные в what колонки определённого пользователя
        :param tg_id:
        :param what:
        :return:
        """
        return self.execute("SELECT " + what + " FROM users WHERE tg_id = ?", tg_id, fetch="ONE")

    def get_fullname(self, tg_id):
        res = self.get_user_info(tg_id, "fullname")
        if not res or not res[0]:
            return False
        return res[0]

    def set_user_tuc(self, tg_id, value: int):
        """
        Устанавливает значение профкомности
        :param tg_id:
        :param value:
        :return:
        """
        self.execute("UPDATE users SET tuc = ? WHERE tg_id = ?", value, tg_id, commit=True)

    def user_registered(self, tg_id):
        return bool(self.get_user_info(tg_id, "tg_id"))

    # Ищет наиболее похожие ФИО
    def get_similar(self, fullname, bottom=90):
        response = self.execute("SELECT fullname FROM tuc_list", fetch=True)
        sort_list = list(map(lambda data: (fuzz.token_sort_ratio(fullname, data[0]), data[0]),
                             response))
        sort_list.sort(reverse=True)
        if not sort_list or sort_list[0][0] < bottom:
            return None
        return sort_list[0][1]

    def get_enter_code(self, tg_id):
        res = self.execute("SELECT enter_code FROM users WHERE tg_id = ?", tg_id, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_enter_codes(self):
        return list(map(lambda x: x[0], self.execute("SELECT enter_code FROM users", fetch=True)))

    def create_enter_code(self, tg_id, enter_code):
        self.execute("UPDATE users SET enter_code = ? WHERE tg_id = ?", enter_code, tg_id, commit=True)

    def create_get_enter_code(self, tg_id, digits=5):
        if not (code := self.get_enter_code(tg_id)):
            codes = self.get_enter_codes()

            code = "".join(str(random.choice(string.digits)) for _ in range(digits))
            while code in codes:
                code = "".join(str(random.choice(string.digits)) for _ in range(digits))
            self.create_enter_code(tg_id, code)
        return code

    def use_promo(self, tg_id, promo):
        """

        :param tg_id:
        :param promo:
        :return: 0 - сработало, 1 - нет кода, 2 - уже использовано, 3 - просрочен, 4 - использован много раз,
         5 - транзакция не завершена
        """
        data = self.execute("SELECT id, money, time_ends, used, can_use FROM promo WHERE name = ?",
                            promo,
                            fetch="one")
        if not data:
            return 1
        promo_id, money, time_ends, used, can_use = data
        if promo_id:
            dt_ends = dt.datetime.strptime(time_ends, constants.DATETIME_FORMAT).astimezone(constants.TZ)
            if dt.datetime.now(constants.TZ) <= dt_ends:
                # await asyncio.sleep(20)
                if used < can_use:
                    used_user = self.execute("SELECT promo_id FROM promo_usages WHERE promo_id = ? and tg_id = ?",
                                             promo_id,
                                             tg_id, fetch="one")
                    if not used_user:
                        cur = self.con.cursor()
                        try:
                            cur.execute("BEGIN EXCLUSIVE TRANSACTION;")
                            cur.execute("UPDATE promo SET used = used + 1 WHERE id = ?;", (promo_id,))
                            cur.execute("INSERT INTO promo_usages (promo_id, tg_id, datetime) VALUES (?, ?, ?);",
                                        (promo_id, tg_id,
                                         dt.datetime.strftime(dt.datetime.now(tz=constants.TZ),
                                                              constants.DATETIME_FORMAT)))
                            cur.execute("UPDATE users SET money = money + ? WHERE tg_id = ?;", (money, tg_id))
                            cur.execute("END TRANSACTION;")
                            self.con.commit()
                            cur.close()
                            return 0
                        except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                            cur.close()
                            return 5
                    else:
                        return 2
                else:
                    return 4
            else:
                return 3
        else:
            return 1


def __del__(self):
    self.con.close()


if __name__ == '__main__':
    db = DataBase("mmweek2023db.db")
    db.add_event("Отчисление", dt.datetime(year=2023, month=4, day=25, hour=18, minute=0), 50,
                 description="Это крутое и очень крутое мероприятие, которое преподы сделали специально для вас крутых")
    # print(db.get_events_summary())
    # print(db.get_event(2))
