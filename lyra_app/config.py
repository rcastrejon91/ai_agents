import os

# Flask secret key
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

# Admin login password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# Email credentials
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

# Owner info
OWNER_NAME = "Ricky"
OWNER_EMAIL = "ricardomcastrejon@gmail.com"
