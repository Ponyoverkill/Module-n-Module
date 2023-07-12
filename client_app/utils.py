import datetime

from redis import Redis
from redis.exceptions import ConnectionError

from config import REDIS_HOST, REDIS_PORT

REDIS_BD = Redis(host=REDIS_HOST, port=REDIS_PORT)




# def counter(func):
#     time = datetime.datetime.now()
#
#     def inner(*args, **kwargs):
#         pass


async def generate_key(**kwargs):
    name = 'cache&'
    for key, value in kwargs.items():
        name += f'{key}:{value}&'
    return name


async def redis_check(**kwargs):
    key = await generate_key(**kwargs)
    try:
        data = REDIS_BD.get(key)
    except ConnectionError:
        return False
    if not data:
        return False
    else:
        return data


async def redis_cache(value, expire, **kwargs):
    key = await generate_key(**kwargs)
    try:
        REDIS_BD.set(key, value, ex=expire)
    except ConnectionError:
        pass
