"""
UniNuvola Web Application Package.

This package contains the Flask web application for UniNuvola,
a cloud computing platform. It provides authentication via HashiCorp Vault
OAuth, user request management through Redis, and an administrative interface.

Modules
-------
app : Flask application configuration and initialization
config : Environment variable configuration
db : SQLite database manager (deprecated)
db_redis : Redis database manager for user requests
routes : Flask route handlers for web endpoints
"""
import logging
from .app import app
from . import routes
