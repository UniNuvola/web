"""
Configuration module for the UniNuvola web application.

This module loads environment variables from a .env file and exposes them
as module-level constants for use throughout the application.

Environment Variables
---------------------
VAULT_CLIENT_ID : str
    OAuth client ID for HashiCorp Vault authentication.
VAULT_CLIENT_SECRET : str
    OAuth client secret for HashiCorp Vault authentication.
VAULT_CONF_URL : str
    URL to Vault's OpenID Connect configuration endpoint.
WEB_PUBLIC_URL : str
    Public URL of the web application (used as SERVER_NAME).
SECRET_KEY : str
    Secret key for Flask session encryption.
REDIS_IP : str
    IP address of the Redis server.
REDIS_PASSWORD : str
    Password for Redis authentication.
LDAPSYNC_IP : str
    IP address of the LDAP sync service.
LDAPSYNC_PORT : str
    Port number of the LDAP sync service.
"""
import os
from dotenv import load_dotenv

load_dotenv()

VAULT_CLIENT_ID = os.getenv('VAULT_CLIENT_ID')
VAULT_CLIENT_SECRET = os.getenv('VAULT_CLIENT_SECRET')
VAULT_CONF_URL = os.getenv('VAULT_CONF_URL')
SERVER_NAME = os.getenv('WEB_PUBLIC_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
REDIS_IP = os.getenv('REDIS_IP')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
LDAPSYNC_IP = os.getenv('LDAPSYNC_IP')
LDAPSYNC_PORT = os.getenv('LDAPSYNC_PORT')
