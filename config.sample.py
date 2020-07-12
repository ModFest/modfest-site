#  Fill out these fields and rename this file to config.py to run.

flask_key: str = ""  # secret key used by flask
flask_port: int = 5000  # port the run flask on (5000 for dev, 80 for prod)
discord_client: str = ""  # discord application client id - used for oauth2
discord_secret: str = ""  # discord application client secret - used for oauth2
discord_redirect: str = ""  # discord application redirect uri - used for oauth2
discord_webhook: str = ""  # discord webhook url - used for logging
