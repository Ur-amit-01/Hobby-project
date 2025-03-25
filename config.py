import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
KOYEB_URL = os.getenv("KOYEB_URL", "https://squealing-diahann-restrictedsaver-bea22cab.koyeb.app/")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

DB_NAME = os.environ.get("DB_NAME","Z900")     
DB_URL = os.environ.get("DB_URL","")

ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6803505727').split()]
PORT = os.environ.get("PORT", "8080")

RENAME_MODE = bool(environ.get('RENAME_MODE', True)) # Set True or False
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', False)) # Set True or False
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False)) # Set True or False
SESSION_STRING = os.environ.get("SESSION_STRING", "")

START_PIC = os.environ.get("START_PIC", "https://raw.githubusercontent.com/Ur-amit-01/minimalistic-wallpaper-collection/main/images/OGARart-eagle-mountain-sunset-minimalist.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://envs.sh/nrg.jpg")
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '').split()] #Ex : ('-10073828 -102782829 -1007282828')
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002027394591"))

REACTIONS = ["🤝", "😇", "🤗", "😍", "🎅", "🥰", "🤩", "😘", "😛", "😈", "🎉", "🫡", "😎", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions

