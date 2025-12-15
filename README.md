# UniNuvola Web 🌎

A Flask-based web application for managing user access requests to the UniNuvola cloud computing platform. The application provides OAuth authentication via HashiCorp Vault and user request management through Redis.

## Features

- **OAuth Authentication**: Secure login via HashiCorp Vault identity provider
- **User Request Management**: Users can submit and track access requests
- **Admin Dashboard**: Administrators can approve or manage user requests
- **LDAP Synchronization**: Automatic notification to LDAP sync service for user provisioning
- **Redis Backend**: Fast and scalable request storage

## Architecture

```
src/
├── __init__.py      # Package initialization
├── app.py           # Flask app configuration and OAuth setup
├── config.py        # Environment variable configuration
├── db_redis.py      # Redis database manager for requests
├── db.py            # SQLite database manager (deprecated)
├── routes.py        # HTTP route handlers
├── static/          # Static assets (images, CSS)
└── templates/       # Jinja2 HTML templates
```

## Setup

### Requirements

- Python >= 3.12
- Poetry (Python dependency manager)
- Redis server
- HashiCorp Vault (configured with OIDC provider)

### Install Dependencies

Install Python dependencies with [Poetry](https://python-poetry.org/):

```bash
poetry install
```

### Configuration

Create a `.env` file in the project root with the following variables:

```env
# Vault OAuth Configuration
VAULT_CLIENT_ID=<your-vault-client-id>
VAULT_CLIENT_SECRET=<your-vault-client-secret>
VAULT_CONF_URL=<vault-oidc-config-url>

# Application Configuration
WEB_PUBLIC_URL=<public-url-of-web-app>
SECRET_KEY=<flask-secret-key>

# Redis Configuration
REDIS_IP=<redis-server-ip>
REDIS_PASSWORD=<redis-password>

# LDAP Sync Service
LDAPSYNC_IP=<ldapsync-service-ip>
LDAPSYNC_PORT=<ldapsync-service-port>
```

#### Environment Variable Details

| Variable | Description | Example |
|----------|-------------|---------|
| `VAULT_CLIENT_ID` | OAuth client ID from Vault | `QHGdesC2wLwmCjsmvl7uOJ4o4SbmHyCE` |
| `VAULT_CLIENT_SECRET` | OAuth client secret from Vault | `hvo_secret_...` |
| `VAULT_CONF_URL` | Vault OIDC discovery URL | `http://127.0.0.1:8200/v1/identity/oidc/provider/default/.well-known/openid-configuration` |
| `WEB_PUBLIC_URL` | Public URL for OAuth callbacks | `https://web.example.com` |
| `SECRET_KEY` | Flask session encryption key | Any secure random string |
| `REDIS_IP` | Redis server hostname/IP | `localhost` |
| `REDIS_PASSWORD` | Redis authentication password | Your Redis password |
| `LDAPSYNC_IP` | LDAP sync service IP | `localhost` |
| `LDAPSYNC_PORT` | LDAP sync service port | `8080` |

> [!NOTE]
> - The `VAULT_CONF_URL` should be the full path to the OIDC discovery endpoint
> - **Always include the protocol (`http://` or `https://`) in URLs**
> - `SECRET_KEY` should be a secure random string (not provided by Vault)

## Running the Application

### Prerequisites

1. Ensure HashiCorp Vault is configured and running with OIDC provider
2. Ensure Redis server is running and accessible
3. Load the `webconfig.env` generated during Vault configuration (if applicable)

### Start the Web Server

```bash
./run.sh
```

Or run directly with Flask:

```bash
poetry run flask --app src run --host 0.0.0.0 --port 5000
```

Open your browser and visit `http://localhost:5000/` to access the application 🚀

## API Routes

| Route | Methods | Description |
|-------|---------|-------------|
| `/` | GET, POST, DELETE | Homepage with user/admin interface |
| `/login` | GET | Initiates OAuth login flow |
| `/auth` | GET | OAuth callback handler |
| `/logout` | GET | Logs out user and revokes token |
| `/info` | GET | Information page |
| `/docs` | GET | Documentation page |

## Development

### Linting

Run pylint on all Python files:

```bash
make lint
```

Or directly:

```bash
poetry run pylint $(git ls-files '*.py')
```

### Testing

Run the Redis database tests:

```bash
poetry run python tests.py
```

## Docker

Docker configuration is available in the `docker/` directory for containerized deployment.

## License

See the repository license for details.
