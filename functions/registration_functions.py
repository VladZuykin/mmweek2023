import sqlite3
from typing import Union

import requests_async
import io
import os
from random import choice


# Получение картинки из API
async def get_random_cat_from_web() -> Union[io.BytesIO, bool]:
    try:
        content = await requests_async.get('https://api.thecatapi.com/v1/images/search')
        if content.ok:
            img_response = await requests_async.get(content.json()[0]["url"])
            if img_response.ok:
                img_io = io.BytesIO(await img_response.read())
                return img_io
    except Exception as e:
        print("Картинку не удалось отправить:", e)
    return False

# Получение картинки из папки
def get_cat_from_files(path="misc/cats"):
    names = os.listdir(path)
    with open(path + ("/" if not path.endswith("/") else "") + choice(names), "rb") as f:
        img_bytes = f.read()
    return io.BytesIO(img_bytes)


def get_capitalised_words(sentence: str) -> set:
    return set(word.capitalize() for word in sentence.split())


def get_capitalised_sentence(sentence: str):
    return " ".join(word.capitalize() for word in sentence.split())


# Правда ли, что фразы (без знаков препинания) имеют одинаковые слова без учёта порядка и регистра
def are_different_content_sentences(sentence1: str, sentence2: str):
    if get_capitalised_words(sentence1) == get_capitalised_words(sentence2):
        return False
    return True

def reward_previous_bot(username, previous_db_path="database/previous_db.sqlite"):
    con = sqlite3.connect(previous_db_path)
    cur = con.cursor()

    first_response = cur.execute("SELECT coins FROM Users where tg_id = ?",
                                 (username,)).fetchone()
    if first_response and first_response[0]:
        return True

    second_response = cur.execute(f"SELECT {', '.join([str(num) for num in range(1, 41)])} "
                                  f"FROM purchases "
                                  f"WHERE user_id = ?", (username, )).fetchone()
    if second_response and sum(second_response):
        return True
    return False
