from functools import wraps
from flask import session, redirect, url_for, abort, request
import secrets
import hmac

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def verify_csrf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.form.get('csrf_token')
        if not token or not hmac.compare_digest(token, session.get('csrf_token', '')):
            abort(403)
        return f(*args, **kwargs)
    return decorated