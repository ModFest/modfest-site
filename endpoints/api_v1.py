from flask import Blueprint, Response
from data import data_classes as data
import json
import storage_manager as storage
from data.data_classes import Event

api = Blueprint('api_v1', __name__, template_folder='templates')


@api.route("/")
def api_index():
    resp: Response = Response()
    resp.headers.add_header("Content-Type", "application/json")
    resp.set_data(json.dumps({
        "name": "ModFest API",
        "version": "1"
    }))
    return resp


@api.route("/route_link/<string:code>", methods=["POST"])  # https://modfest.net/api/v1/link?code=aaaaaa
def api_auth_link(code: str):
    if code is not None:
        user: data.User = storage.get_user_by_code(code)
        if 'id' in user:
            user.update_code(clear=True)  # clear route_link code
            storage.update_user(user)
            return json.dumps(data.LinkResponse(success=True, message="valid code", user=user))
        else:
            return json.dumps(data.LinkResponse(message="invalid code"))
