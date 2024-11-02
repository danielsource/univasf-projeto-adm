from functools import wraps
from datetime import datetime

from flask import redirect, url_for, flash
from flask_babel import _
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def requires_role(*roles):
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.allowed(*roles):
                flash(_('You do not have permission to access that page.'), 'error')
                return redirect(url_for('index.start_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def in_business_hours():
    now = datetime.now().time()
    return Config.BUSINESS_START_HOUR <= now <= Config.BUSINESS_END_HOUR
