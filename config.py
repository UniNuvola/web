import os
from dotenv import load_dotenv

load_dotenv()

VAULT_CLIENT_ID = os.getenv('VAULT_CLIENT_ID')
VAULT_CLIENT_SECRET = os.getenv('VAULT_CLIENT_SECRET')

ADMIN_USERS = ['alice.alice@alice.it', 'prova@unipg.it', 'eliasforna@gmail.com']
