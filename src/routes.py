from flask import url_for, session, request, render_template, redirect
from .app import app, dbms, oauth


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def homepage():
    user = session.get('user')

    app.logger.debug(f"/ User value: {user}")

    if user:
        _username = user['metadata']['name']
        _groups = dbms.get_request_data(_username).get('groups', [])
        _infos = dbms.get_user_infos(_username)
        user['username'] = _username
        user['groups'] = _groups
        user['infos'] = _infos
        user['uninuvolaurl'] = 'https://compute.uninuvola.unipg.it/hub/oauth_login?next='

        # ADMIN ROLE
        if 'admin' in _groups:
            app.logger.debug("User %s is ADMIN", _username)
            user['admin'] = True

            if request.method == 'POST':
                user_to_update = request.form['id']
                app.logger.debug(f"UPDATING USER {user_to_update} REQUEST")

                dbms.update_request_status(user_to_update)

            user['request_data'] = dbms.get_all_request_data()
            app.logger.debug(f"ADMIN REQUEST DATA: {user['request_data']}")

            return render_template('users/admin.html', user=user)

        # USER ROLE
        user['admin'] = False

        match request.method:
            case 'POST':
                dbms.add_request(_username)
            case 'DELETE':
                dbms.delete_request(_username)
            case _:
                print(request.method)

        user['request_data'] = dbms.get_request_data(_username)
        app.logger.debug(f"USER REQUEST DATA: {user['request_data']}")

        return render_template('users/user.html', user=user)

    return render_template('users/unlogged.html', user=user)


@app.route('/login')
def login():
    app.logger.debug('Redirecting to Vault')
    redirect_uri = url_for('auth', _external=True, _scheme='https')

    app.logger.debug('ALLOWED REDIRECT URI: %s', redirect_uri)

    return oauth.vault.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    try:
        token = oauth.vault.authorize_access_token()

    except Exception as e: # TODO: choose better Exception
        app.logger.error("Error while autorizing access token, %s", e)

        return redirect(url_for('homepage'))

    app.logger.debug('Success user auth')
    app.logger.debug(f'Token: {token}')

    session['user'] = token['userinfo']
    session['token'] = token

    return redirect(url_for('homepage'))

@app.route('/logout')
def logout():
    token = session.get('token')

    app.logger.debug(f'Logging out {token}')

    oauth.vault.post('auth/token/revoke-self', token=token)

    app.logger.debug('Cleaning session values')
    session.pop('user', None)
    session.pop('token', None)

    return redirect('/')

@app.route('/info')
def info():
    return render_template('info.html')
