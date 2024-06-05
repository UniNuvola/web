from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')

# TODO: nascondere in .env ?
CONF_URL = 'http://127.0.0.1:8200/v1/identity/oidc/provider/default/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='vault',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid default'
    }
)


@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.vault.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.vault.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == "__main__":
   app.run(debug=True) 
