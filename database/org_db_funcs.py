from database.db_funcs import DataBase


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


if __name__ == '__main__':
    db = OrgDataBase("mmweek2023db.db")
