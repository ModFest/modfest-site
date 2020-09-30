from flask import Flask
import endpoints
import config
import storage_manager as storage
import threading
import asyncio
from bot import discord_bot

storage.validate_storage()


def run_webapp():
    web_app = Flask(__name__)
    web_app.config["SECRET_KEY"] = config.flask_key
    web_app.register_blueprint(endpoints.api_v1.api, url_prefix="/api/v1")
    web_app.register_blueprint(endpoints.frontend.app)
    web_app.use_reloader = False
    web_app.run(port=config.flask_port)


thread2 = threading.Thread(target=run_webapp, daemon=True)
thread2.start()
a_loop = asyncio.get_event_loop()
a_loop.create_task(discord_bot.start())
thread = threading.Thread(target=a_loop.run_forever(), daemon=True)

thread.start()
