# app/utils.py
from functools import wraps
from flask import abort
from flask_login import current_user

def require_roles(*roles):
    """
    Decorator to restrict access to users whose current_user.role is in roles.
    Usage: @require_roles('admin') or @require_roles('admin','staff')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user or not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
