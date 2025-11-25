import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Yandex Tracker Configuration
YT_ORG_ID = os.getenv('YT_ORG_ID')
YT_TOKEN = os.getenv('YT_TOKEN')

# Yandex Cloud Service Account Configuration
YC_FOLDER_ID = os.getenv('YC_FOLDER_ID')
YC_SERVICE_ACCOUNT_ID = os.getenv('YC_SERVICE_ACCOUNT_ID')
YC_KEY_ID = os.getenv('YC_KEY_ID')
YC_PRIVATE_KEY = os.getenv('YC_PRIVATE_KEY')

# Database configuration (using Yandex Tracker fields to store data)
YT_PROJECT_ID = os.getenv('YT_PROJECT_ID', 'default_project')

# Default settings
DEFAULT_MESSAGE = "Добро пожаловать! Выберите действие из меню ниже."