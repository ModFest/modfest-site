from typing import Optional, List

from flask import Blueprint, request, render_template, session, redirect, url_for
import storage_manager as storage
from data.data_classes import User, Event, Entry, Badge, Settings
from data import discord

app = Blueprint('frontend', __name__, template_folder='templates')


@app.route('/')
def route_index():
    e: Event = storage.get_latest_event()
    return redirect(url_for('frontend.route_event', event=e.name))


@app.route("/link")  # https://modfest.net/link
def route_link():
    if 'd-id' not in session:
        return redirect(url_for('frontend.route_index'))
    user: User = storage.get_user_by_id(session['d-id'])
    user.update_code()
    storage.update_user(user)
    return str(user.code)


@app.route("/auth")  # https://modfest.net/auth
def route_auth():
    code = request.args.get("code")
    if code is None:
        return redirect(url_for('frontend.route_index'))

    response = discord.exchange_code(code)
    if response is None:
        return redirect(url_for('frontend.route_index'))

    r = discord.get_user(response['access_token'])

    avatar: str = "https://cdn.discordapp.com/"
    if r.json()['avatar']:
        avatar += f"avatars/{r.json()['id']}/{r.json()['avatar']}.png"
    else:
        avatar += f"embed/avatars/{r.json()['discriminator'] % 5}.png"

    session['d-username'] = r.json()['username']
    session['d-discriminator'] = r.json()['discriminator']
    session['d-avatar'] = avatar
    session['d-id'] = r.json()['id']

    storage.update_user(User(r.json()['id'], r.json()['username'], r.json()['discriminator'], avatar))
    return redirect(url_for('frontend.route_index'))


@app.route("/logout")  # https://modfest.net/logout
def route_logout():
    if 'd-id' in session:
        session.clear()
    return redirect(url_for('frontend.route_index'))


@app.route("/<string:event>")  # https://modfest.net/1.16
def route_event(event: str):
    if event == "favicon.ico":
        return url_for('static', filename=storage.get_latest_event().name + '/favicon.ico')
    e: Event = storage.get_event(event)
    if e is None:
        return redirect(url_for('frontend.route_index'))
    if 'd-id' not in session:
        return render_template("events/" + e.name + ".html", event=e)
    return render_template("events/" + e.name + ".html", event=e)


@app.route("/<string:event>/entries")
def route_entries(event: str):
    e: Optional[Event] = storage.get_event(event)
    entries: List[Entry] = storage.get_entries(event)
    if e is not None:
        return render_template('entries.html', entries=entries, event=e)
    else:
        return redirect(url_for('frontend.route_index'))


@app.route("/<string:event>/entries/new", methods=["POST", "GET"])
def route_new_entries(event: str):
    if request.method == "POST":
        discord.log("log from site")
        return {"gamer": "time"}
    e: Optional[Event] = storage.get_event(event)
    entries: List[Entry] = storage.get_entries(event)
    if e is not None:
        return render_template('entries.html', entries=entries, event=e)
    else:
        return redirect(url_for('frontend.route_index'))


@app.route("/participant/<int:participant>")
def route_participant(participant: int):
    p: User = storage.get_user_by_id(participant)
    entries: List[Entry] = storage.get_entries_for_user(p)
    badges: List[Badge] = storage.get_user_badges(p)

    if p is not None:
        return render_template('participant.html', user=p, event=storage.get_latest_event(), entries=entries,
                               badges=badges)
    else:
        return redirect(url_for('frontend.route_index'))
