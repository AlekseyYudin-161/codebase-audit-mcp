"""
Application settings and secrets.

WARNING: This file contains hardcoded credentials for demo purposes.
In production, all secrets must be loaded from environment variables
or a secrets manager (e.g. AWS Secrets Manager, HashiCorp Vault).
"""

# FIXME: all secrets below must be moved to .env before any deployment

# Database
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "appdb"
DB_USER = "admin"
DB_PASSWORD = "supersecret123"

# External API
STRIPE_API_KEY = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
SENDGRID_API_KEY = "SG.abcdefghijklmnop.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# AWS credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "us-east-1"

# Application secrets
SECRET_KEY = "django-insecure-^q1w2e3r4t5y6u7i8o9p0"
JWT_SECRET = "jwt_super_secret_token_never_share"

# OAuth
GITHUB_CLIENT_SECRET = "github_secret_abc123xyz"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz"

# TODO: replace all above with os.environ.get() calls
# Example:
# DB_PASSWORD = os.environ.get("DB_PASSWORD")
# if not DB_PASSWORD:
#     raise RuntimeError("DB_PASSWORD environment variable is not set")
