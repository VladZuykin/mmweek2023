import datetime

def dt_to_dtdict(delta: datetime.timedelta) -> dict:
    """
    Перевод date.timedelta объекта  >= 0 в {"days": ..., "hours": ..., "minutes" : ..., "seconds": ...}
    :param delta:
    :return:
    """
    if delta < datetime.timedelta(seconds=0):
        raise ValueError("delta должен быть неотрицательным.")

    units = {"days": delta.days}
    delta -= datetime.timedelta(days=units["days"])
    units["hours"] = delta.seconds // 3600
    delta -= datetime.timedelta(hours=units["hours"])
    units["minutes"] = delta.seconds // 60
    delta -= datetime.timedelta(minutes=units["minutes"])
    units["seconds"] = delta.seconds

    return units


NOMINATIVE_TIME_UNITS_FORMS = {
    "seconds": ["секунд", "секунда", "секунды"],
    "minutes": ["минут", "минута", "минуты"],
    "hours": ["часов", "час", "часа"],
    "days": ["дней", "день", "дня"]
}

ACCUSATIVE_TIME_UNITS_FORMS = {
    "seconds": ["секунд", "секунду", "секунды"],
    "minutes": ["минут", "минуту", "минуты"],
    "hours": ["часов", "час", "часа"],
    "days": ["дней", "день", "дня"]
}

def dtdict_to_str(units: dict, time_units_forms=None) -> str:
    """
    Перевод {"days": ..., "hours": ..., "minutes" : ..., "seconds": ...} объекта  >= 0 в читаемый на русском языке текст
    :param units:
    :param time_units_forms:
    :return:
    """

    if time_units_forms is None:
        time_units_forms = NOMINATIVE_TIME_UNITS_FORMS
    phrases = []
    for key, value in units.items():
        if value != 0:
            if value % 100 in (11, 12, 13, 14) or value % 10 in (0, 5, 6, 7, 8, 9):
                word = time_units_forms[key][0]
            elif value % 10 in (1,):
                word = time_units_forms[key][1]
            elif value % 10 in (2, 3, 4):
                word = time_units_forms[key][2]
            phrases.append(f"{value} {word}")
    return " ".join(phrases)
