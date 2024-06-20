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
> `VAULT_API_BASE_URL` should be similar to `<ip>/v1/`
> `VAULT_CONF_URL` should be similar to `<ip>/v1/identity/oidc/provider/<provider>/.well-known/openid-configuration`. The `<provider>` string should be `default`.
> **DON'T FORGET THE PROTOCOL (`http://` or `https://`) BEFORE THE `<ip>` STRING !!
> `SECRET_KEY` should be invented (not provided by Voult)
> `ADMIN_USERS` must be a list of users id. Something like this `ADMIN_USERS='["alice.alice@alice.it", "prova@unipg.it", "eliasforna@gmail.com"]'`.
> Replace email with usernames or whatever you want. Be carefull with `'` and `"`, the must be use exactly linke in the example

## Run

Activate the virtuan environment and run the web server with:

```bash
poetry shell
python main.py
```
