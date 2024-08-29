from logging.config import dictConfig
from authlib.integrations.flask_client import OAuth
from flask import Flask
from .db import DBManager

# Logging Settings
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s - %(levelname)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'},
        # 'screen': {
        #     # 'level': 'INFO',
        #     'formatter': 'default',
        #     'class': 'logging.StreamHandler',
        #     'stream': 'ext://sys.stdout',},
        'file': {
            # 'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.FileHandler',
            'filename': 'loggs.log',
            'mode': 'a',
        }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})


app = Flask(__name__)

dbms = DBManager(app)

app.logger.debug("Loading configs from envs")
app.config.from_object('src.config')

app.logger.debug(f"Setting secret key: {app.config['SECRET_KEY']}")
app.secret_key = app.config['SECRET_KEY']

app.logger.debug("Setting REDIS ip and password: %s %s", app.config['REDIS_IP'], app.config['REDIS_PASSWORD'])
app.redis_ip = app.config['REDIS_IP']
app.redis_password = app.config['REDIS_PASSWORD']

app.logger.debug(f"ADMIN USERS: {app.config['ADMIN_USERS']}")

app.logger.debug("Loading OAuth configs")
oauth = OAuth(app)
oauth.register(
    name='vault',
    server_metadata_url=app.config['VAULT_CONF_URL'],
    api_base_url='http://localhost:8200/v1/',
    client_kwargs={
        'scope': 'openid web'
    }
)