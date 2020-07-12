from functools import wraps

from flask import session, url_for, redirect
import storage_manager as storage


def require_auth(func):
    @wraps(func)
    def validate(*args, **kwargs):
        if 'd-id' not in session:
            return redirect(url_for('frontend.route_index'))

        return func(*args, **kwargs)

    return validate


def require_admin(func):
    @wraps(func)
    def validate(*args, **kwargs):
        if 'd-id' not in session:
            return redirect(url_for('frontend.route_index'))
        if storage.get_user_by_id(session['d-id']).admin == 0:
            return redirect(url_for('frontend.route_index'))
        return func(*args, **kwargs)

    return validate
