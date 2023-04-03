from typing import Union

import requests_async
import io
import os
from random import choice


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


def get_cat_from_files(path="misc/cats"):
    names = os.listdir(path)
    with open(path + "/" if not path.endswith("/") else "" + choice(names), "rb") as f:
        img_bytes = f.read()
    return io.BytesIO(img_bytes)
