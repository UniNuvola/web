import hvac
import click
import json
import logging
import secrets


# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
)


client = hvac.Client(url='http://localhost:8200')


USERS = [
    {'name':'alice', 'email':'alice.alice@unipg.it', 'username':'al980001'},
    {'name':'bob', 'email':'bob.bob@studenti.unipg.it', 'username':'bb980001'},
]


def auth():
    """Authenticate client using saved secrets.
    """

    logging.info(f"Client Authenticated: {client.is_authenticated()}")
    logging.info(f"Client Inizialized: {client.sys.is_initialized()}")

    logging.info("Loading secrets ...")
    with open(".env", "r") as fp:
        secrets = json.load(fp) 

    root_token = secrets['root_token']
    keys = secrets['keys']

    logging.debug(f"root_token: {root_token}, keys: {keys}")
    logging.info("Authenticating ...")

    client.token = root_token

    return root_token, keys


@click.group()
@click.option('--verbose', type=click.Choice(['info', 'debug']), default='info', help="Logging level")
@click.pass_context
def cli(ctx, verbose):
    """Vault CLI tools to auto-deploy a new Vault container.
    """

    # update logging level
    logging.getLogger().setLevel(logging.INFO if verbose == 'info' else logging.DEBUG)


@cli.command()
@click.option('--shares', default=5,)
@click.option('--threshold', default=3,)
def init(shares, threshold):
    """Initialize Vault when first created.

    Initialize the Vault container and save the resulting secrets (in json format)
    in .env file.
    """

    logging.info("Running init procedure")
    logging.debug(f"shares: {shares}, threshold: {threshold}")

    result = client.sys.initialize(shares, threshold)

    root_token = result['root_token']
    keys = result['keys']

    logging.debug(f"root_token: {root_token}, keys: {keys}")
    logging.info(f"Client Inizialized: {client.sys.is_initialized()}")

    logging.info("Saving secrets")
    with open(".env", "w") as fp:
        json.dump(result , fp) 

@cli.command()
def unseal():
    """Unseal the Vault.

    Unseal the Vault by using 3 keys (secrets) generated during the init phase.
    """

    root_token, keys = auth()

    logging.info("Running Useal procedure")
    logging.info(f"Client Sealed: {client.sys.is_sealed()}")

    # Unseal a Vault cluster with individual keys
    unseal_response1 = client.sys.submit_unseal_key(keys[0])
    unseal_response2 = client.sys.submit_unseal_key(keys[1])
    unseal_response3 = client.sys.submit_unseal_key(keys[2])

    logging.debug(f"Unseal Response 1: {unseal_response1}")
    logging.debug(f"Unseal Response 2: {unseal_response2}")
    logging.debug(f"Unseal Response 3: {unseal_response3}")

    logging.info(f"Client Sealed: {client.sys.is_sealed()}")

@cli.command()
def create_entity():
    """Creates entities.
    
    Creates 2 test entities (alice and bob) with respective aliases.
    Entity and Alias are needed for userpass/ auth method.
    """

    _ = auth()
    
    logging.info("Creating entities")

    accessor = client.sys.list_auth_methods()['userpass/']['accessor']
    logging.debug(f"userpass/ accessor: {accessor}")

    for user in USERS:
        create_response = client.secrets.identity.create_or_update_entity(
            name=user['name'],
            metadata=dict(email=user['email'], username=user['username']),
        )
        entity_id = create_response['data']['id']
        logging.info(f"Entity ID for {user['name']} is: {entity_id}")

        create_response = client.secrets.identity.create_or_update_entity_alias(
                name=user['name'],
                canonical_id=entity_id,
                mount_accessor=accessor,
        )
        alias_id = create_response['data']['id']
        logging.info(f"Alias ID for {user['name']} is: {alias_id}")

@cli.command()
def enable_userpass():
    """Enable userpass/ auth method.
    """

    _ = auth()

    logging.info("Enabling userpass/")
    client.sys.enable_auth_method('userpass')

@cli.command()
def set_users():
    """Set userpass/ users.

    Creates 2 users (alice and bob) inside the userpass/ auth methods and sets the passowrds.
    Users' names are the same of entity names, this put in a relation entity and userpass/ users preventing to generate
    new entities.
    """

    _ = auth()

    logging.info("Setting users for userpass/")

    for user in USERS:
        create_response = client.auth.userpass.create_or_update_user(username=user['name'], password=user['name'])
        logging.debug(f"{user['name']} response: {create_response}")

@cli.command()
@click.option('--appname', default='Web', help="OIDC Application name")
@click.option('--scopename', default='default', help="OIDC Application Scope name")
@click.option('--providername', default='default', help="OIDC Application Provider name")
def oidc(appname, scopename, providername):
    """Configure Vault as an OIDC Provider

    \b
    - Creates the Application with the redirect uris,
    - Creates the default Scope
    - Set the default provider configs
    """
    _ = auth()

    # Create application
    app_config = {
        "access_token_ttl": "24h",
        "assignments": [
            "allow_all "
        ],
        "client_type": "confidential",
        "id_token_ttl": "24h",
        "key": "default",
        "redirect_uris": [
            "http://localhost:5000/auth"    # TODO: put in .env file ?
        ]
    }

    logging.info(f"Creating application: {appname}")
    logging.debug(app_config)

    client.write_data(
        path=f"/identity/oidc/client/{appname}",
        data=app_config
    )

    # Create scope
    scope_config = {
        "description": "",
        "template": """
        {
            "contact": {
                "email": {{identity.entity.metadata.email}},
                "username": {{identity.entity.metadata.username}}
            }
        }
        """
    }

    logging.info(f"Creating application scope: {appname}")
    logging.debug(scope_config)

    client.write_data(
        path=f"/identity/oidc/scope/{scopename}",
        data=scope_config
    )

    # Update Provider
    provider_config = {
        "issuer": "http://localhost:8200",
        "scopes_supported": [
            scopename
        ]
    }

    logging.info(f"Creating application provider: {providername}")
    logging.debug(provider_config)

    client.write_data(
        path=f"/identity/oidc/provider/{providername}",
        data=provider_config
    )

@cli.command()
def create_group():
    """Create the default group.
    """

    _ = auth()

    logging.info("Creating default group")

    create_response = client.secrets.identity.create_or_update_group(
            name='default',
            # metadata=dict(extra_data='we gots em'),
    )

    group_id = create_response['data']['id']
    logging.info('Group ID for "default" is: {id}'.format(id=group_id))

@cli.command()
@click.option('--appname', default='Web', help="OIDC Application name")
@click.option('--secretlen', default=16, help="Secret key lenght")
def get_webconfig(appname, secretlen):
    """Generate config for the WepApp

    \b
    Generates a .env file with the required settings:
        - OIDC Client ID
        - OIDC Client Secret
        - OIDC Conf URL
        - A Secret Key
        - Admin users
    """
    _ = auth()

    env_data = {}

    logging.info(f"Generating Web config for Application {appname}")

    respone = client.read(f"/identity/oidc/client/{appname}")
    logging.debug(respone)

    env_data['client_id'] = respone['data']['client_id']
    env_data['client_secret'] = respone['data']['client_secret']
    env_data['conf_url'] = "http://127.0.0.1:8200/v1/identity/oidc/provider/default/.well-known/openid-configuration" # TODO: automatico ?
    env_data['secret_key'] = secrets.token_urlsafe(secretlen)
    env_data['admin_users'] = "\'[\"alice.alice@unipg.it\", \"prova@unipg.it\", \"eliasforna@gmail.com\"]\'"

    logging.debug(env_data)
    logging.info("Writing ../.env data")

    with open('../.env', 'w') as f:
        f.write(f"VAULT_CLIENT_ID={env_data['client_id']}\n")
        f.write(f"VAULT_CLIENT_SECRET={env_data['client_secret']}\n")
        f.write(f"VAULT_CONF_URL={env_data['conf_url']}\n")
        f.write(f"SECRET_KEY={env_data['secret_key']}\n")
        f.write(f"ADMIN_USERS={env_data['admin_users']}\n")

@cli.command()
@click.pass_context
def deploy(ctx):
    """Deploy procedure.

    Runs every CLI commands needed for auto-deploy a new Vault container.
    """

    ctx.invoke(init)
    ctx.invoke(unseal)
    ctx.invoke(enable_userpass)
    ctx.invoke(create_entity)
    ctx.invoke(set_users)
    ctx.invoke(create_group)
    ctx.invoke(oidc)
    ctx.invoke(get_webconfig)


if __name__ == "__main__":
    cli()

