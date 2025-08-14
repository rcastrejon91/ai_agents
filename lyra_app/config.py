import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASS = os.getenv("GMAIL_PASS", "")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")
OWNER_NAME = os.getenv("OWNER_NAME", "")
