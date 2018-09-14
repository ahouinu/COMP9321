from functools import wraps

from flask import request
from flask_restful import abort
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)

SECRET_KEY = "A RANDOM KEY"
CURRENT_USER = None


def authenticate_by_token(token, users):
    if token is None:
        return False
    s = Serializer(SECRET_KEY)
    try:
        username = s.loads(token.encode())
        if username in users:
            CURRENT_USER = username
            return True
    except:
        return False

    return False


def admin_required(f, message="You are not admin!"):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        if authenticate_by_token(token, users=['admin']):
            return f(*args, **kwargs)

        abort(401, message=message)

    return decorated_function


def login_required(f, message="You are not authorized!"):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        if authenticate_by_token(token, users=['admin', 'guest']):
            return f(*args, **kwargs)

        abort(401, message=message)

    return decorated_function
