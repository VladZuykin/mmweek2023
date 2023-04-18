import datetime as dt

WEEKDAYS = {0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
            }

def get_weekday_str(datetime: dt.datetime):
    num = dt.datetime.weekday(datetime)
    return WEEKDAYS[num]
