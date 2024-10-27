from dotenv import load_dotenv
import os

load_dotenv()

WEBHOOK_KEY = os.environ.get('WEBHOOK_KEY')
APPLICATION_TOKEN = os.environ.get('APPLICATION_TOKEN')

BOT_ID = os.getenv("BOT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")


C_REST_CLIENT_ID = os.getenv('C_REST_CLIENT_ID')
C_REST_CLIENT_SECRET = os.getenv('C_REST_CLIENT_SECRET')
C_REST_WEB_HOOK_URL = os.getenv('C_REST_WEB_HOOK_URL')
C_REST_CURRENT_ENCODING = os.getenv('C_REST_CURRENT_ENCODING')