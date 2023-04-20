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

    def get_id_with_code(self, enter_code):
        res = self.execute("SELECT tg_id FROM users WHERE enter_code = ?", enter_code, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_event_id(self, tg_id):
        res = self.execute("SELECT event_id FROM admins WHERE tg_id = ?", tg_id, fetch="ONE")
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
            return False
        return res[0]

    def get_events_visited(self, tg_id):
        res = self.execute("SELECT event_id FROM visits WHERE tg_id = ?", tg_id, fetch=True)
        if not res or not res[0]:
            return False
        return res[0]

    def update_event_visits(self, tg_id, event_id):
        self.execute("INSERT INTO visits (event_id, tg_id) VALUES (?, ?)", event_id, tg_id, commit=True)

    def add_money(self, tg_id, money_value):
        self.execute("UPDATE users SET money = money + ? WHERE tg_id = ?", money_value, tg_id, commit=True)

    def add_promo(self, name, money, can_use, time_registered, time_ends):
        self.execute("INSERT INTO promo (name, money, can_use, time_registered, time_ends) VALUES (?, ?, ?, ?, ?)",
                     name, money, can_use, time_registered, time_ends, commit=True)

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
