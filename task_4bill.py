import configparser
import time
from collections import OrderedDict

import redis
from flask import Flask


flask_app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)


config = configparser.ConfigParser()
config.read('config.ini')
flask_app.config['AMOUNT_LIMITS_CONFIG'] = OrderedDict(eval(config['DEFAULT']['AMOUNT_LIMITS_CONFIG']))


def get_or_create_in_redis(key):
    if not r.get(key):
        r.set(key, 0)
    return r.get(key)


get_or_create_in_redis('total_amount')


@flask_app.route('/request/<int:amount>/')
def process_amount(amount):
    request_time = time.time()
    for limit_time, limit_amount in flask_app.config['AMOUNT_LIMITS_CONFIG'].items():

        redis_limit_amount = get_or_create_in_redis(f'amount_limit_{limit_amount}')
        redis_limit_time = get_or_create_in_redis(f'time_limit_{limit_time}_at')

        time_delta = request_time - float(redis_limit_time)
        if time_delta > limit_time:
            r.set(f'time_limit_{limit_time}_at', request_time)
            r.set(f'amount_limit_{limit_amount}', 0)
            redis_limit_amount = 0

        current_limit_amount = int(redis_limit_amount) + int(amount)
        if current_limit_amount > limit_amount:
            return {"error": f"amount limit exceeded ({limit_amount}/{limit_time}sec)"}

    else:
        for limit_time, limit_amount in flask_app.config['AMOUNT_LIMITS_CONFIG'].items():
            r.incr(f'amount_limit_{limit_amount}', amount)
    r.incr(f'total_amount', amount)
    return "OK"
