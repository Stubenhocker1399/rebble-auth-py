from functools import wraps
import os
import random
import time
from uuid import getnode

from flask import request, abort, redirect, url_for
from flask_login import current_user
from ..models import db


# This generates a MongoDB-style ObjectID, which is what all Pebble identifiers are.
class ObjectIdGenerator:
    def __init__(self):
        self.counter = random.randint(0, 0xFFFFFF)
        self.node_id = getnode() % 0xFFFFFF
        self.pid = os.getpid() % 0xFFFF

    def generate(self):
        self.counter = (self.counter + 1) % 0xFFFFFF
        return f'{(int(time.time()) % 0xFFFFFFFF):08x}{self.node_id:06x}{self.pid:04x}{self.counter:06x}'


id_generator = ObjectIdGenerator()


def api_ensure_pebble(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = request.oauth.user
        if user.pebble_auth_uid is None or user.pebble_dev_portal_uid is None:
            return abort(401)
        else:
            return fn(*args, **kwargs)
    return wrapper


def ensure_pebble(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user
        if user.pebble_auth_uid is None or user.pebble_dev_portal_uid is None:
            return redirect(url_for('login.demand_pebble'))
        else:
            return fn(*args, **kwargs)
    return wrapper
