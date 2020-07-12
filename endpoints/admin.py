from flask import Blueprint, session, url_for, redirect

from wrappers import require_admin
import storage_manager as storage

app = Blueprint('admin', __name__, template_folder='templates')


@app.route("/")
@require_admin
def route_index():
    if 'd-id' not in session or storage.get_user_by_id(session['d-id']).admin == 0:
        return redirect(url_for('frontend.route_index'))
    return "admin"
