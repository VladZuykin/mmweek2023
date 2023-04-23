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


if __name__ == '__main__':
    db = OrgDataBase("mmweek2023db.db")
