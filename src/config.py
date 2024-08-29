import os
import json
from dotenv import load_dotenv

load_dotenv()

VAULT_CLIENT_ID = os.getenv('VAULT_CLIENT_ID')
VAULT_CLIENT_SECRET = os.getenv('VAULT_CLIENT_SECRET')
VAULT_CONF_URL = os.getenv('VAULT_CONF_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
ADMIN_USERS = json.loads(os.getenv('ADMIN_USERS'))
REDIS_IP = os.getenv('REDIS_IP')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
