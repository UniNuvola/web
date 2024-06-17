import logging
import sys
from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth
from logging.config import dictConfig


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
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
})


app = Flask(__name__)

app.logger.debug("Setting secret key")
app.secret_key = '!secret'      # TODO: sceglierne una migliore !

app.logger.debug("Loading configs from envs")
app.config.from_object('config')

# TODO: nascondere in .env ?
app.logger.debug("Loading OAuth configs")
CONF_URL = 'http://127.0.0.1:8200/v1/identity/oidc/provider/default/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='vault',
    server_metadata_url=CONF_URL,
    api_base_url='http://localhost:8200/v1/',
    client_kwargs={
        'scope': 'openid default'
    }
)


@app.route('/')
def homepage():
    user = session.get('user')
    app.logger.debug(f"/ User value: {user}")

    return render_template('home.html', user=user)


@app.route('/login')
def login():
    app.logger.debug('Redirecting to Vault')
    redirect_uri = url_for('auth', _external=True)
    return oauth.vault.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.vault.authorize_access_token()

    app.logger.debug('Success user auth')
    app.logger.debug(f'Token: {token}')

    session['user'] = token['userinfo']
    session['token'] = token

    return redirect(url_for('homepage'))


# TODO: logut non funziona
@app.route('/logout')
def logout():
    token = session.get('token')

    app.logger.debug(f'Logging out {token}')

    oauth.vault.post('auth/token/revoke-self', token=token)

    app.logger.debug('Cleaning session values')
    session.pop('user', None)
    session.pop('token', None)

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True) 

