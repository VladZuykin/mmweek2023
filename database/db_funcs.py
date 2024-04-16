import random
import sqlite3
import string
from typing import Union
import datetime as dt
from fuzzywuzzy import fuzz

import constants


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
                            id           INTEGER PRIMARY KEY AUTOINCREMENT,
                            name         TEXT    NOT NULL,
                            reward       INTEGER NOT NULL,
                            description  TEXT,
                            num          INTEGER,
                            button1_text TEXT,
                            button1_url  TEXT,
                            button2_text TEXT,
                            button2_url  TEXT,
                            [release]    INTEGER DEFAULT 0
                            );
                        """,
                     commit=True
                     )
        # 3 Уровня: Сила-персила, Галя и Владелец
        self.execute("""CREATE TABLE IF NOT EXISTS admins (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT
                                             NOT NULL,
                            tg_id    INTEGER NOT NULL,
                            level    INTEGER,
                            event_id INTEGER
                        );
                        """,
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS stuff (
                                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                                stuff_category_id INTEGER REFERENCES stuff_categories (id),
                                name              TEXT,
                                description       TEXT,
                                not_tuc_price     INTEGER,
                                tuc_price         INTEGER,
                                img_path          TEXT,
                                count             INTEGER,
                                show              INTEGER DEFAULT (1) 
                            );""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS stuff_categories (
                                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name        TEXT,
                                    description TEXT,
                                    img_path    TEXT
                                );
                                """, commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS purchases (
                            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                            tg_id                 INTEGER NOT NULL
                                                          REFERENCES users (tg_id),
                            stuff_id              INTEGER REFERENCES stuff (id),
                            stuff_sizes_colors_id INTEGER REFERENCES stuff_sizes_colors (id),
                            count                 INTEGER NOT NULL,
                            issued                INTEGER DEFAULT (0) 
                                  NOT NULL,
                            UNIQUE (
                                tg_id,
                                stuff_id,
                                stuff_sizes_colors_id
                            )
                            
                        );
""",
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

        self.execute("""CREATE TABLE IF NOT EXISTS transactions(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                type TEXT NOT NULL,
                                tg_id1 INTEGER,
                                tg_id2 INTEGER,
                                datetime TEXT,
                                data TEXT);
                                """, commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS stuff_sizes_colors (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            stuff_id INTEGER REFERENCES stuff (id),
                            size     TEXT,
                            color    TEXT,
                            count    INTEGER NOT NULL
                        );
                        """, commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS img_cache (
                        id     INTEGER PRIMARY KEY AUTOINCREMENT,
                        path   TEXT    UNIQUE,
                        img_id TEXT
                    )""", commit=True)

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

    def get_events_summary(self, show_all=False):
        if show_all:
            res = self.execute("SELECT id, name, num FROM events", fetch=True)
        else:
            res = self.execute("SELECT id, name, num  FROM events WHERE release = 1", fetch=True)
        # Меняем строковую дату на datetime
        return res

    def get_event(self, event_id) -> Union[dict, None]:
        res = self.execute("SELECT name, description, num, button1_text, button1_url, "
                           "button2_text, button2_url "
                           "FROM events "
                           "WHERE id = ?",
                           event_id,
                           fetch="one")
        if not res:
            return None
        name, description, order, button1_text, button1_url, button2_text, button2_url = res
        return {
            "name": name,
            "order": order,
            "description": description,
            "button1_text": button1_text,
            "button1_url": button1_url,
            "button2_text": button2_text,
            "button2_url": button2_url,
        }

    def in_blacklist(self, tg_id):
        data = self.execute("SELECT tg_id FROM blacklist WHERE tg_id = ?", tg_id, fetch="one")
        if not data:
            return False
        return True

    def in_tuc(self, tg_id):
        data = self.execute("SELECT tuc FROM users WHERE tg_id = ?", tg_id, fetch="one")
        if not data or not data[0] or data[0] == 2:
            return False
        return True

    def is_color_size_stuff(self, stuff_id):
        data = self.execute("SELECT count FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data:
            raise ValueError("Bad stuff id.")
        if data[0] is None:
            return True
        return False

    def get_purchases_num_by_stuff_id(self, stuff_id):  # Для вещей без укзания размера/цвета
        data = self.execute("SELECT count FROM purchases WHERE stuff_id = ?", stuff_id, fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_category_img_path(self, category_id):
        data = self.execute("SELECT img_path FROM stuff_categories WHERE id = ?", category_id, fetch="one")
        if not data or not data[0]:
            return None
        return data[0]

    def get_category_description(self, category_id):
        data = self.execute("SELECT description FROM stuff_categories WHERE id = ?", category_id, fetch="one")
        if not data or not data[0]:
            return ""
        return data[0]

    def get_stuff_img_path(self, stuff_id):
        data = self.execute("SELECT img_path FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data or not data[0]:
            return None
        return data[0]

    def how_many_stuff_booked(self, tg_id, stuff_id):
        data = self.execute("SELECT count FROM purchases WHERE tg_id = ? and stuff_id = ?",
                            tg_id, stuff_id, fetch="ALL")
        res = 0
        for count, in data:
            res += count
        return res

    def how_many_sizes_colors_booked(self, tg_id, stuff_sizes_colors_id):
        data = self.execute("SELECT count FROM purchases WHERE tg_id = ? and stuff_sizes_colors_id = ?",
                            tg_id, stuff_sizes_colors_id, fetch="ALL")
        res = 0
        for count, in data:
            res += count
        return res

    def booked_list(self, tg_id):
        data = self.execute("SELECT stuff_id, stuff_sizes_colors_id, count "
                            "FROM purchases WHERE tg_id = ?",
                            tg_id, fetch="ALL")
        res = []
        for stuff_id, stuff_sizes_colors_id, count in data:
            name, = self.get_stuff_info(stuff_id, "name")
            if stuff_sizes_colors_id is not None:
                color, size = self.get_stuff_sizes_colors_texts_info(stuff_sizes_colors_id, "color, size")
            else:
                color, size = None, None
            res.append((stuff_id, stuff_sizes_colors_id, name, color, size, count))
        return res

    def get_stuff_count_num_by_stuff_id(self, stuff_id):
        """
        Подсчитывает количество на складе любой вещи
        :param stuff_id:
        :return:
        """
        data = self.execute("SELECT count FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data:
            return None
        if data[0] is not None:
            return data[0]
        data = self.execute("SELECT count FROM stuff_sizes_colors WHERE stuff_id = ?", stuff_id, fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_purchases_num_by_sizes_colors_id(self, stuff_sizes_colors_id):  # Для определённого цвета/размера вещи
        data = self.execute("SELECT count FROM purchases WHERE stuff_sizes_colors_id = ?", stuff_sizes_colors_id,
                            fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_all_color_size_combinations(self, stuff_id):
        """
        Возвращает [(color_size_id, color, size, count),...]
        :param stuff_id:
        :return:
        """
        stuff = self.execute(
            "SELECT id, color, size, count FROM stuff_sizes_colors WHERE stuff_id = ?",
            stuff_id,
            fetch=True)
        res = []
        for size_color_id, color, size, count in stuff:
            if count > 0:
                res.append((size_color_id, color, size, count))
        return res

    def get_all_colors_by_stuff_id(self, stuff_id):
        """
        Возвращает [(colors_sizes_id, color) for colors_sizes_id, color in ...]
        :param stuff_id:
        :return:
        """
        res = []
        colors = self.execute(
            "SELECT id, color, count FROM stuff_sizes_colors WHERE stuff_id = ? and color IS NOT NULL",
            stuff_id,
            fetch=True)
        for colors_sizes_id, color, count in colors:
            if count > 0:
                res.append((colors_sizes_id, color))
        return res

    def get_all_sizes_by_stuff_id(self, stuff_id):
        """
        Возвращает [(colors_sizes_id, size) for colors_sizes_id, size in ...]
        :param stuff_id:
        :return:
        """
        res = []
        sizes = self.execute(
            "SELECT id, size, count FROM stuff_sizes_colors WHERE stuff_id = ? and size IS NOT NULL",
            stuff_id,
            fetch=True)
        for colors_sizes_id, size, count in sizes:
            if count > 0:
                res.append((colors_sizes_id, size))
        return res

    def get_stuff_sizes_colors(self, sizes_colors_id, what: str):
        data = self.execute("SELECT " + what + " FROM stuff_sizes_colors WHERE id = ?", sizes_colors_id,
                            fetch="one")
        return data

    def get_stuff_categories(self):
        data = self.execute("SELECT id, name FROM stuff_categories", fetch=True)
        return data

    def get_user_money(self, tg_id):
        data = self.get_user_info(tg_id, "money")
        if not data:
            return None
        return data[0]

    def get_stuff_sizes_colors_texts_info(self, colors_sizes_id, what: str):
        data = self.execute("SELECT " + what + " FROM stuff_sizes_colors WHERE id = ?",
                            colors_sizes_id, fetch="one")
        return data

    def get_stuff_category_info(self, stuff_category_id, what: str):
        return self.execute("SELECT " + what + " FROM stuff_categories WHERE id = ?", stuff_category_id, fetch="one")

    def get_stuff_info(self, stuff_id, what: str):
        return self.execute("SELECT " + what + " FROM stuff WHERE id = ?", stuff_id, fetch="one")

    def get_user_info_by_code(self, code: str, what: str):
        return self.execute("SELECT " + what + " FROM users WHERE enter_code = ?", code, fetch="one")

    def get_stuff_by_category_id(self, stuff_category_id, what: str):
        data = self.execute("SELECT " + what + " FROM stuff WHERE stuff_category_id = ?", stuff_category_id, fetch=True)
        return data

    def have_admin_rights(self, tg_id, level):
        data = self.execute("SELECT tg_id FROM admins WHERE tg_id = ? and level = ?", tg_id, level, fetch="ONE")
        if data:
            return True
        return False

    def get_schedule_text(self):
        return self.execute("SELECT content FROM texts WHERE name = 'schedule_text'", fetch="one")[0]

    def add_user(self, tg_id, username, fullname, tuc=0):
        self.add_transaction(constants.TransactionTypes.USER_REGISTER.value,
                             tg_id,
                             None,
                             f"tuc: {tuc}")
        self.execute("INSERT INTO users (tg_id, username, fullname, tuc) VALUES (?, ?, ?, ?) "
                     "ON CONFLICT(tg_id) DO UPDATE SET username = ?, fullname = ?, tuc = ?",
                     tg_id, username, fullname, tuc, username, fullname, tuc,
                     commit=True)

    def add_money(self, tg_id, money, transaction_data=None):
        self.add_transaction(constants.TransactionTypes.MONEY_GET.value,
                             tg_id,
                             None,
                             transaction_data)
        self.execute("UPDATE users SET money = money + ? WHERE tg_id = ?", money, tg_id, commit=True)

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

    def get_user_id_by_username(self, username):
        if username.startswith("@"):
            username = username[1:]
        tg_id = self.execute("SELECT tg_id FROM users WHERE username LIKE ?", username, fetch="ONE")
        if not tg_id:
            return None
        return tg_id[0]

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
        self.add_transaction(constants.TransactionTypes.SET_TUC.value,
                             tg_id,
                             None,
                             f"{value}")

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
            self.add_transaction(constants.TransactionTypes.CODE_GENERATE.value,
                                 tg_id,
                                 None,
                                 code)
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
            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                 tg_id,
                                 None,
                                 f"promo: {promo} doesn't activated: doesn't exists")
            return 1
        promo_id, money, time_ends, used, can_use = data
        if promo_id:
            dt_ends = dt.datetime.strptime(time_ends, constants.DATETIME_FORMAT).astimezone(constants.TZ)
            if dt.datetime.now(constants.TZ) <= dt_ends:
                if used < can_use or can_use == -1:
                    used_user = self.execute("SELECT promo_id FROM promo_usages WHERE promo_id = ? and tg_id = ?",
                                             promo_id,
                                             tg_id, fetch="one")
                    if not used_user:
                        cur = self.con.cursor()
                        fail = False
                        try:
                            cur.execute("INSERT INTO promo_usages (promo_id, tg_id, datetime) VALUES (?, ?, ?);",
                                        (promo_id, tg_id,
                                         dt.datetime.strftime(dt.datetime.now(tz=constants.TZ),
                                                              constants.DATETIME_FORMAT)))
                            cur.execute("UPDATE promo SET used = used + 1 WHERE id = ?;", (promo_id,)),
                            cur.execute("UPDATE users SET money = money + ? WHERE tg_id = ?;", (money, tg_id))
                        except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                            fail = True
                            self.con.rollback()
                        cur.close()
                        if fail:
                            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                                 tg_id,
                                                 None,
                                                 f"promo: {promo} doesn't activated bad transaction")
                            return 5
                        else:
                            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                                 tg_id,
                                                 None,
                                                 f"promo: {promo} activated {money} added")
                            return 0
                    else:
                        self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                             tg_id,
                                             None,
                                             f"promo: {promo} doesn't activated: already used")
                        return 2
                else:
                    self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                         tg_id,
                                         None,
                                         f"promo: {promo} doesn't activated: used too many times")
                    return 4
            else:
                self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                     tg_id,
                                     None,
                                     f"promo: {promo} doesn't activated: expired")
                return 3
        else:
            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                 tg_id,
                                 None,
                                 f"promo: {promo} doesn't activated: doesn't exists")
            return 1

    def add_transaction(self, transaction_type, tg_id1, tg_id2, data):
        """

        :param transaction_type:
        :param tg_id1:
        :param tg_id2:
        :param data:
        :return:
        """
        datetime = dt.datetime.now(tz=constants.TZ).strftime(constants.LOG_DATETIME_FORMAT)
        self.execute("INSERT INTO transactions (type, tg_id1, tg_id2, datetime, data) VALUES (?, ?, ?, ?, ?)",
                     transaction_type, tg_id1, tg_id2, datetime, data, commit=True)

    def get_last_transaction(self, transaction_type, tg_id1=None, tg_id2=None):
        if tg_id2 is None:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id1 = ?",
                                transaction_type, tg_id1, fetch="all")
        elif tg_id1 is None:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id2 = ?",
                                transaction_type, tg_id2, fetch="all")
        else:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id1 = ? and tg_id2 = ?",
                                transaction_type, tg_id1, tg_id2, fetch="all")
        if not data:
            return None
        maxim = max(data, key=lambda x:
        dt.datetime.strptime(x[3], constants.LOG_DATETIME_FORMAT).astimezone(tz=constants.TZ))
        return dt.datetime.strptime(maxim[3], constants.LOG_DATETIME_FORMAT).astimezone(tz=constants.TZ)

    def get_last_support_request_time(self, tg_id):
        data = self.get_last_transaction(constants.TransactionTypes.SUPPORT_REQUEST.value, tg_id1=tg_id)
        if not data:
            return None
        return data

    def get_admin_list(self, level=None):
        if level is not None:
            data = self.execute("SELECT tg_id, event_id FROM admins WHERE level = ?", level, fetch=True)
        else:
            data = self.execute("SELECT tg_id, event_id FROM admins", fetch=True)
        res = []
        for tg_id, event_id in data:
            username, full_name = self.get_user_info(tg_id, "username, fullname")
            res.append((tg_id, username, full_name, event_id))
        return res

        # 1 - недостаточно денег, 2 - мерча уже нет, 3 - ошибка при транзакции

    def buy_size_color_stuff(self, tg_id, sizes_colors_id):
        stuff_id, count = self.get_stuff_sizes_colors_texts_info(sizes_colors_id, "stuff_id, count")
        tuc_price, not_tuc_price = self.get_stuff_info(stuff_id, "tuc_price, not_tuc_price")
        if self.in_tuc(tg_id):
            price = tuc_price
        else:
            price = not_tuc_price
        user_money = self.get_user_money(tg_id)
        if user_money < price:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough money, sizes_colors_id = {sizes_colors_id}")
            return 1
        elif count <= 0:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough items, sizes_colors_id = {sizes_colors_id}")
            return 2
        else:
            cur = self.con.cursor()
            fail = False
            try:
                cur.execute("UPDATE users SET money = money - ? WHERE tg_id = ?;", (price, tg_id))
                cur.execute("UPDATE stuff_sizes_colors SET count = count - 1 WHERE id = ?;", (sizes_colors_id,))
                cur.execute("INSERT INTO purchases (tg_id, stuff_id, stuff_sizes_colors_id, count) "
                            "VALUES (?, ?, ?, 1) "
                            "ON CONFLICT (tg_id, stuff_id, stuff_sizes_colors_id) DO UPDATE SET count = count + 1 "
                            "WHERE tg_id = ? and stuff_id = ? and stuff_sizes_colors_id = ?",
                            (tg_id, stuff_id, sizes_colors_id, tg_id, stuff_id, sizes_colors_id))
                # update purchases
                self.con.commit()
            except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                print(e)
                self.con.rollback()
                fail = True
            cur.close()
            if fail:
                self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                     f"transaction fail, sizes_colors_id = {sizes_colors_id}")
                return 3
            self.add_transaction(constants.TransactionTypes.PURCHASE_SUCCESS.value, tg_id, None,
                                 f"sizes_colors_id = {sizes_colors_id}")
            return 0

    # 1 - недостаточно денег, 2 - мерча уже нет, 3 - ошибка при транзакции
    def buy_no_size_color_stuff(self, tg_id, stuff_id):
        tuc_price, not_tuc_price, count = self.get_stuff_info(stuff_id, "tuc_price, not_tuc_price, count")
        if self.in_tuc(tg_id):
            price = tuc_price
        else:
            price = not_tuc_price
        user_money = self.get_user_money(tg_id)
        if self.execute("SELECT id FROM purchases WHERE tg_id = ? and stuff_id = ?",
                        tg_id, stuff_id, fetch="one"):
            have_purchase = True
        else:
            have_purchase = False
        if user_money < price:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough money, stuff_id = {stuff_id}")
            return 1
        elif count <= 0:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough items, stuff_id = {stuff_id}")
            return 2
        else:
            cur = self.con.cursor()
            fail = False
            try:
                cur.execute("UPDATE users SET money = money - ? WHERE tg_id = ?;", (price, tg_id))
                cur.execute("UPDATE stuff SET count = count - 1 WHERE id = ?;", (stuff_id,))
                if not have_purchase:
                    cur.execute("INSERT INTO purchases (tg_id, stuff_id, stuff_sizes_colors_id, count) "
                                "VALUES (?, ?, NULL, 1) ",
                                (tg_id, stuff_id))
                else:
                    cur.execute("UPDATE purchases SET count = count + 1 "
                                "WHERE tg_id = ? and stuff_id = ? and stuff_sizes_colors_id is NULL",
                                (tg_id, stuff_id))
                self.con.commit()
            except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                print(e)
                fail = True
                self.con.rollback()
            cur.close()
            if fail:
                self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                     f"transaction fail, stuff_id = {stuff_id}")
                return 3
            self.add_transaction(constants.TransactionTypes.PURCHASE_SUCCESS.value, tg_id, None,
                                 f"stuff_id = {stuff_id}")
            return 0

    def get_purchases_by_id(self, tg_id, what: str):
        return self.execute("SELECT " + what + " FROM purchases WHERE tg_id = ?", tg_id, fetch=True)





def __del__(self):
    self.con.close()


if __name__ == '__main__':
    db = DataBase("mmweek2023db.db")
    # db.add_event("Отчисление", dt.datetime(year=2023, month=4, day=25, hour=18, minute=0), 50,
    #              description="Это крутое и очень крутое мероприятие, которое преподы сделали специально для вас крутых")
    # print(db.get_last_support_request_time(702447805))
