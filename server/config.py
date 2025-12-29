HOST = "192.168.0.106"
PORT = 9063

OVERRIDE_HOST = None  # e.g., "https://mydomain.com/"

WSS_HOST = "192.168.0.106"
WSS_PORT = 9064

PACK_ICON_ATLAS_FILENAME = ""
LOCALIZATION_ENTRY_FILENAME = ""

UNLOCK_ALL = True

# Auth mode:
# 0 - No auth, email can be arbitrary but unique, and verification code is sent to client UI
# 1 - Email auth. Email must be valid and verification code is sent to the email address
# 2 - Discord auth. Email can be arbitrary but unique, and a binding process with Discord bot is required, which will provide the verification code

AUTH_MODE = 0

# For auth mode 1
SMTP_HOST = "smtp.test.com"
SMTP_PORT = 465
SMTP_USER = "test@test.com"
SMTP_PASSWORD = "test"

# For auth mode 2

DISCORD_BOT_SECRET = "test"
DISCORD_BOT_API_KEY = "test"

#SSL_CERT = 'localhost.crt'  # Path to SSL certificate file
#SSL_KEY = 'localhost.key'  # Path to SSL key file

SSL_CERT = None
SSL_KEY = None

DEBUG = True