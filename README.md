# Web 🌎

## Setup

### Requirements

- Python > 3.10 
- Poetry

### Install dependencies

Install python dependencies with [Poetry](https://python-poetry.org/)

```bash
poetry install
```

### Web server

Create a `.env` file, inside the main folder, to store the Vault credentials

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

## Run

First of all, you need to have Vault already configured and started.
You need the `webconfig.env` generated during the Vault configuration process too.
Finally, start the web server:

```bash
./run.sh
```

Open your browser and visit `http://localhost:5000/` to access the initial page 🚀!
