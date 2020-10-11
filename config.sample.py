#  Fill out these fields and rename this file to config.py to run.

flask_key: str = ""  # secret key used by flask
flask_port: int = 5000  # port the run flask on (5000 for dev, 80 for prod)
discord_client: str = ""  # bot application client id - used for oauth2
discord_secret: str = ""  # bot application client secret - used for oauth2
discord_redirect: str = ""  # bot application redirect uri - used for oauth2
discord_webhook: str = ""  # bot webhook url - used for logging

# bot bot config
bot_token: str = ""  # bot bot token
admin_role: str = ""  # bot admin role
guild_id: str = ""  # bot guild

# database config
db_user: str = ""
db_pass: str = ""
db_host: str = ""
db_port: str = ""
db_name: str = ""
