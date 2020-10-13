from flask import Flask
import endpoints
import config
import storage_manager as storage

storage.validate_storage()

web_app = Flask(__name__)
web_app.config["SECRET_KEY"] = config.flask_key
web_app.register_blueprint(endpoints.api_v1.api, url_prefix="/api/v1")
web_app.register_blueprint(endpoints.frontend.app)
web_app.use_reloader = False

if __name__ == "__main__":
    web_app.run()
