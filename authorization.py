from flask import request, jsonify
import functools
import hashlib


def ok_user_and_password(username, password):
    """Test whether the supplied username and password match."""
    salt = b'' # Get the salt you stored for *this* user
    key = b'' # Get this users key calculated

    # Use the exact same setup you used to generate the key, but this time put in the password to check
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'), # Convert the password to bytes
        salt, 
        100000
    )

    return new_key = key


def authenticate():
    """ Return a response indicating a failure to authenticate."""
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    return resp


def requires_authorization(f):
    """A python decorator which requires HTTP basic authentication."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not ok_user_and_password(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
