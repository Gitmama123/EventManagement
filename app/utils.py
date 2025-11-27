# app/utils.py
from flask import abort
from flask_login import current_user
from functools import wraps

def require_roles(*roles):
    """
    Decorator to require that current_user.role is one of roles.
    Example:
        @require_roles('admin', 'staff')
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Let login_required handle redirects; here we simply abort
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
