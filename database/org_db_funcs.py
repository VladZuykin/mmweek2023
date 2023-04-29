import sqlite3

import constants
from database.db_funcs import DataBase
import datetime as dt


class OrgDataBase(DataBase):
    def __init__(self, path):
        super().__init__(path)
        self.create_visits()

    def create_visits(self):
        """ таблица с парами мероприятие-участник для фиксирования посещаемости """
        self.execute("""CREATE TABLE IF NOT EXISTS visits(
                        id       INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id INTEGER,
                        tg_id    INTEGER
                        );""",
                     commit=True
                     )

    def set_level_1_admin(self, tg_id, event_id, tg_who_gave):
        if self.execute("SELECT tg_id FROM admins WHERE tg_id = ? and level = 1", tg_id, fetch="ONE"):
            self.execute("UPDATE admins SET event_id = ? WHERE tg_id = ? and level = 1",
                         event_id, tg_id, commit=True)
        else:
            self.execute("""INSERT INTO admins(tg_id, level, event_id) VALUES (?, 1, ?)""",
                         tg_id, event_id, commit=True)
        self.add_transaction(constants.TransactionTypes.ADMIN_GAVE.value,
                             tg_who_gave, tg_id, "admin level 1 add")

    def set_level_2_3_admin(self, tg_id, level, tg_who_gave):
        if self.execute("SELECT tg_id FROM admins WHERE tg_id = ? and level = ?", tg_id, level, fetch="ONE"):
            self.execute("UPDATE admins SET event_id = NULL WHERE tg_id = ? and level = ?",
                         tg_id, level, commit=True)
        else:
            self.execute("""INSERT INTO admins(tg_id, level, event_id) VALUES (?, ?, NULL)""",
                         tg_id, level, commit=True)
        self.add_transaction(constants.TransactionTypes.ADMIN_GAVE.value,
                             tg_who_gave, tg_id, f"admin level {level} add")

    def get_id_with_code(self, enter_code):
        res = self.execute("SELECT tg_id FROM users WHERE enter_code = ?", enter_code, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_event_by_tg_id(self, tg_id):
        res = self.execute("SELECT event_id FROM admins WHERE tg_id = ? and level = 1", tg_id, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_event_name(self, event_id):
        res = self.execute("SELECT name FROM events WHERE id = ?", event_id, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_event_reward(self, event_id):
        res = self.execute("SELECT reward FROM events WHERE id = ?", event_id, fetch="ONE")
        if not res or not res[0]:
            return 0
        return res[0]

    def get_events_visited(self, tg_id):
        res = self.execute("SELECT event_id FROM visits WHERE tg_id = ?", tg_id, fetch=True)
        res = list(map(lambda x: x[0], res))
        return res

    def update_event_visits(self, tg_id, event_id, tg_who_scanned):
        self.add_transaction(constants.TransactionTypes.ENTER.value,
                             tg_who_scanned, tg_id, None)
        self.execute("INSERT INTO visits (event_id, tg_id) VALUES (?, ?)", event_id, tg_id, commit=True)

    def add_promo(self, name, money, can_use, time_registered, time_ends, id_who_created):
        self.execute("INSERT INTO promo (name, money, can_use, time_registered, time_ends) VALUES (?, ?, ?, ?, ?)",
                     name, money, can_use, time_registered, time_ends, commit=True)
        self.add_transaction(constants.TransactionTypes.PROMO_CREATE.value,
                             id_who_created, None, f"{name}  money:{money}  can use:{can_use}")

    def get_promo_id(self, name):
        res = self.execute("SELECT id FROM promo WHERE name = ?", name, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_promo_list(self):
        res = self.execute("SELECT name, money, can_use, used, time_ends FROM promo", fetch=True)
        return list(map(lambda x:
                        [x[0],
                         x[1],
                         x[2],
                         x[3],
                         dt.datetime.strptime(x[4], constants.DATETIME_FORMAT).astimezone(constants.TZ)],
                        res))

    def issue_merch(self, purchase_id, k,
                    checker_tg_id):  # 0 - успех,  1 - нет такой записи, 2 - k < 0, 3 - k > count - issued, 4 - error
        any_records = self.execute("SELECT count, issued, tg_id FROM purchases WHERE id = ?", purchase_id, fetch="ONE")
        if not any_records:
            return 1
        count, issued, tg_id = any_records
        if k < 0:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"less than zero")
            return 2
        if k > count - issued:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"too many to issue")
            return 3
        fail = False
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE purchases SET issued = issued + ? WHERE id = ?", (k, purchase_id))
            self.con.commit()
        except (sqlite3.DatabaseError, sqlite3.InternalError, sqlite3.OperationalError) as e:
            print(e)
            self.con.rollback()
            fail = True
        cur.close()
        if fail:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"updating error")
            return 4
        else:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH.value, checker_tg_id, tg_id,
                                 None)
            return 0

    def return_back_merch(self, purchase_id, k, checker_tg_id):
        any_records = self.execute("SELECT purchases.count, purchases.issued, purchases.tg_id, "
                                   "stuff.tuc_price, stuff.not_tuc_price, users.tuc, "
                                   "purchases.stuff_sizes_colors_id, purchases.stuff_id "
                                   "FROM purchases "
                                   "JOIN stuff ON purchases.stuff_id = stuff.id "
                                   "JOIN users ON purchases.tg_id = users.tg_id "
                                   "WHERE purchases.id = ?",
                                   purchase_id, fetch="ONE")
        if not any_records:
            return 1
        count, issued, tg_id, tuc_price, not_tuc_price, tuc_status, sizes_colors_id, stuff_id = any_records
        if k < 0:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"less than zero")
            return 2
        if k > count:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"too many to return back")
            return 3
        will_be_issued = min(issued, count - k)
        if tuc_status:
            price = tuc_price
        else:
            price = not_tuc_price
        money_get = k * price

        fail = False
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE purchases SET count = count - ?, issued = ? WHERE id = ?", (k, will_be_issued,
                                                                                            purchase_id))
            cur.execute("UPDATE users SET money = money + ? WHERE tg_id = ?", (money_get, tg_id))
            if sizes_colors_id:
                cur.execute("UPDATE stuff_sizes_colors SET count = count + 1 WHERE id = ?", (sizes_colors_id,))
            else:
                cur.execute("UPDATE stuff SET count = count + 1 WHERE id = ?", (stuff_id,))
            self.con.commit()
        except (sqlite3.DatabaseError, sqlite3.InternalError, sqlite3.OperationalError) as e:
            print(e)
            self.con.rollback()
            fail = True
        cur.close()
        if fail:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"updating error")
            return 4
        else:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK.value, checker_tg_id, tg_id,
                                 None)
            return 0


if __name__ == '__main__':
    db = OrgDataBase("mmweek2023db.db")
