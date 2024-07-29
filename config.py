from dotenv import load_dotenv
import os

load_dotenv()

WEBHOOK_KEY = os.environ.get('WEBHOOK_KEY')
APPLICATION_TOKEN = os.environ.get('APPLICATION_TOKEN')

