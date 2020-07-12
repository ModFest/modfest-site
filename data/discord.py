from typing import Optional
import config
import requests

API_ENDPOINT = 'https://discord.com/api/v6'
CLIENT_ID = config.discord_client
CLIENT_SECRET = config.discord_secret
REDIRECT_URI = config.discord_redirect
WEBHOOK_URI = config.discord_webhook


def exchange_code(code) -> Optional[dict]:
    dat = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=dat, headers=headers)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError:
        return None


def get_user(token: str):
    r = requests.get(
        API_ENDPOINT + "/users/@me",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    return r


def log(content: str):
    dat = {
        content: content
    }
    heads = {
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(WEBHOOK_URI, data=dat, headers=heads)
        r.raise_for_status()
    except requests.HTTPError:
        pass
