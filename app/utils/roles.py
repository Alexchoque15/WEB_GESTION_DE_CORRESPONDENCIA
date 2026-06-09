from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for

from flask_login import current_user


def rol_requerido(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if current_user.rol not in roles:

                flash(
                    'No tiene permisos para acceder.',
                    'danger'
                )

                return redirect(
                    url_for('dashboard.home')
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator