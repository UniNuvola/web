# Web 🌎

## Setup

Install python dependencies with [Poetry](https://python-poetry.org/)

```bash
poetry install
```

Then create a `.env` file to store the Vault credentials

```
VAULT_CLIENT_ID=
VAULT_CLIENT_SECRET=
VAULT_API_BASE_URL=
VAULT_CONF_URL=
SECRET_KEY=
ADMIN_USERS=
```

> [!NOTE]
> - `VAULT_API_BASE_URL` should be similar to `<ip>/v1/`.
> - `VAULT_CONF_URL` should be similar to `<ip>/v1/identity/oidc/provider/<provider>/.well-known/openid-configuration`. The `<provider>` string should be `default`.
> - **DON'T FORGET THE PROTOCOL (`http://` or `https://`) BEFORE THE `<ip>` STRING !!**
> - `SECRET_KEY` should be invented (not provided by Voult).
> - `ADMIN_USERS` must be a list of users id. Something like this `ADMIN_USERS='["alice.alice@alice.it", "prova@unipg.it", "eliasforna@gmail.com"]'`.
> - Replace email with usernames or whatever you want. Be careful with `'` and `"`, these must be used exactly as in the example.

One example of a configuration is shown below:

```
VAULT_CLIENT_ID=QHGdesC2wLwmCjsmvl7uOJ4o4SbmHyCE
VAULT_CLIENT_SECRET=hvo_secret_TcKGRPh3sjC1WE4PrS2GV3XYpY2AkL0FEgYWRNQUPw7rLTYSS3Psei1oCfQFOeZg
VAULT_API_BASE_URL=http://localhost:8200/v1/
VAULT_CONF_URL=http://127.0.0.1:8200/v1/identity/oidc/provider/default/.well-known/openid-configuration
SECRET_KEY=!secret
ADMIN_USERS='["alice.alice@unipg.it", "prova@unipg.it", "eliasforna@gmail.com"]'
```

### Vault as OIDC Provider

Currently, the scripts that manage the automatic deployment of Vault do not handle the creation and configuration of Vault
as an OIDC Provider, so this procedure must be performed manually.
Follow in order the following points to complete the configuration successfully:

1. Go to: "Access" and then "OIDC Provider"
1. Click on the button "Create your first app"
1. Fill the following fields
    ```
    Application name: Web
    Redirect URIs: http://localhost:5000/auth
    ```
    If not specified use the default values
1. Create !
1. Open the **Scope** section, and "Create scope"
1. Fill the following fields
    ```
    Name: default
    Description:
    JSON template: 
    {
        "contact": {
            "email": {{identity.entity.metadata.email}},
            "username": {{identity.entity.metadata.username}}
        }
    }
    ```
1. Go back to **Provider** section and then on "default" and "Edit provider"
1. Set "default" in "Supported scopes"
1. DONE !

## Run

Activate the virtual environment and run the web server with:

```bash
poetry shell
python main.py
```
