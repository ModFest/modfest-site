from flask import Flask
import endpoints
import config
import storage_manager as storage

storage.validate_storage()

app = Flask(__name__)
app.config["SECRET_KEY"] = config.flask_key
app.register_blueprint(endpoints.api_v1.api, url_prefix="/api/v1")
app.register_blueprint(endpoints.frontend.app)
app.register_blueprint(endpoints.admin.app, url_prefix="/admin")

if __name__ == '__main__':
    app.run(port=config.flask_port)
