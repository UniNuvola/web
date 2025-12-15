"""
Flask route handlers for the UniNuvola web application.

This module defines all HTTP route handlers for the application,
including the homepage with user/admin views, authentication endpoints,
and informational pages.

Routes
------
/ : Homepage with user request management
/login : OAuth login redirect to Vault
/auth : OAuth callback handler
/logout : Session logout and token revocation
/info : Information page
/docs : Documentation page
"""
from flask import url_for, session, request, render_template, redirect
from .app import app, dbms, oauth


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def homepage():
    """
    Handle the main homepage with user/admin views.

    For authenticated users, displays either the admin dashboard
    (if user has 'admin' group) or the user request interface.
    Handles POST requests for request creation/approval and
    DELETE requests for request removal.

    Returns
    -------
    str
        Rendered HTML template:
        - 'users/admin.html' for admin users
        - 'users/user.html' for regular users
        - 'users/unlogged.html' for unauthenticated visitors
    """
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
    """
    Redirect user to Vault OAuth login page.

    Initiates the OAuth authorization flow by redirecting the user
    to the HashiCorp Vault identity provider.

    Returns
    -------
    Response
        Redirect response to Vault's OAuth authorization endpoint.
    """
    app.logger.debug('Redirecting to Vault')
    redirect_uri = url_for('auth', _external=True, _scheme='https')

    app.logger.debug('ALLOWED REDIRECT URI: %s', redirect_uri)

    return oauth.vault.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    """
    Handle OAuth callback from Vault.

    Processes the OAuth authorization response, exchanges the
    authorization code for an access token, and stores the user
    information in the session.

    Returns
    -------
    Response
        Redirect to homepage on success or failure.
    """
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
    """
    Log out the current user.

    Revokes the OAuth token with Vault and clears the user's
    session data.

    Returns
    -------
    Response
        Redirect to homepage.
    """
    token = session.get('token')

    app.logger.debug(f'Logging out {token}')

    oauth.vault.post('auth/token/revoke-self', token=token)

    app.logger.debug('Cleaning session values')
    session.pop('user', None)
    session.pop('token', None)

    return redirect('/')

@app.route('/info')
def info():
    """
    Render the information page.

    Displays general information about the UniNuvola platform.

    Returns
    -------
    str
        Rendered 'info.html' template.
    """
    return render_template('info.html')

@app.route('/docs')
def docs():
    """
    Render the documentation page.

    Displays platform documentation and usage instructions.

    Returns
    -------
    str
        Rendered 'docs.html' template.
    """
    return render_template('docs.html')
