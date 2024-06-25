import hvac
import click
import json

client = hvac.Client(url='http://localhost:8200')

print(f"Client Authenticated: {client.is_authenticated()}")
print(f"Client Inizialized: {client.sys.is_initialized()}")


USERS = [
    {'name':'alice', 'email':'alice.alice@unipg.it', 'username':'al980001'},
    {'name':'bob', 'email':'bob.bob@studenti.unipg.it', 'username':'bb980001'},
]


def auth():
    print("Loading secrets ...")
    with open(".env", "r") as fp:
        secrets = json.load(fp) 

    root_token = secrets['root_token']
    keys = secrets['keys']

    client.token = root_token

    return root_token, keys


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        test(ctx)

@cli.command()
@click.option('--shares', default=5,)
@click.option('--threshold', default=3,)
def init(shares, threshold):
    result = client.sys.initialize(shares, threshold)

    root_token = result['root_token']
    keys = result['keys']

    print(f"Client Inizialized: {client.sys.is_initialized()}")

    with open(".env", "w") as fp:
        json.dump(result , fp) 

@cli.command()
def unseal():
    root_token, keys = auth()

    print(f"Client Sealed: {client.sys.is_sealed()}")

    # Unseal a Vault cluster with individual keys
    unseal_response1 = client.sys.submit_unseal_key(keys[0])
    unseal_response2 = client.sys.submit_unseal_key(keys[1])
    unseal_response3 = client.sys.submit_unseal_key(keys[2])

    print(f"Client Sealed: {client.sys.is_sealed()}")

@cli.command()
def create_entity():
    _ = auth()
    
    accessor = client.sys.list_auth_methods()['userpass/']['accessor']

    for user in USERS:
        create_response = client.secrets.identity.create_or_update_entity(
                    name=user['name'],
                    metadata=dict(email=user['email'], username=user['username']),
            )

        entity_id = create_response['data']['id']
        print(f"Entity ID for {user['name']} is: {entity_id}")

        create_response = client.secrets.identity.create_or_update_entity_alias(
                name=user['name'],
                canonical_id=entity_id,
                mount_accessor=accessor,
        )
        alias_id = create_response['data']['id']
        print(f"Alias ID for {user['name']} is: {alias_id}")

@cli.command()
def enable_userpass():
    _ = auth()

    client.sys.enable_auth_method('userpass')

@cli.command()
def set_users():
    _ = auth()

    for user in USERS:
        create_response = client.auth.userpass.create_or_update_user(username=user['name'], password=user['name'])

# @cli.command()
# def oidc():
#     _ = auth()
#
#     client.auth.oidc.create_role(
#         name='Web',
#         user_claim="True",
#         allowed_redirect_uris="http://localhost:5000/auth",
#     )
#     client.sys.enable_auth_method(
#         method_type='oidc',
#     )

@cli.command()
def create_group():
    _ = auth()

    create_response = client.secrets.identity.create_or_update_group(
            name='default',
            # metadata=dict(extra_data='we gots em'),
    )

    group_id = create_response['data']['id']
    print('Group ID for "default" is: {id}'.format(id=group_id))

def test(ctx):
    ctx.invoke(init)
    ctx.invoke(unseal)
    ctx.invoke(enable_userpass)
    ctx.invoke(create_entity)
    ctx.invoke(set_users)
    ctx.invoke(create_group)


if __name__ == "__main__":
    cli()

