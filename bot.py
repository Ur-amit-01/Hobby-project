import logging
import logging.config
from pyrogram import Client 
from config import *
from aiohttp import web
from plugins.web_support import web_server
import threading  # ======= Added for self-pinging
import requests   # ======= Added for self-pinging
import time       # ======= Added for self-pinging

# ======= Self-Pinging Functions =======
def ping_self():
    while True:
        try:
            response = requests.get(KOYEB_URL)
            logging.info(f"Pinged self: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to ping self: {e}")
        time.sleep(210)  # Ping every 3.5 minutes

def start_pinging():
    t = threading.Thread(target=ping_self)
    t.daemon = True  # Daemonize thread to exit when the main program exits
    t.start()
# ======= End of Self-Pinging Functions =======

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        
        # ======= Start the self-pinging mechanism =======
        start_pinging()
        logging.info("Self-pinging mechanism started.")
        # ======= End of self-pinging mechanism =======

        # Start the web server
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        
        logging.info(
            "\n╭━━━╮╱╱╱╭╮╱╱╱╱╱╱╱╱╱╱╱╭╮\n"
            "┃╭━╮┃╱╱╭╯╰╮╱╱╱╱╱╱╱╱╱╱┃┃\n"
            "┃┃╱┃┣╮╭╋╮╭╯╭━━┳┳━╮╭━━┫╰━╮\n"
            "┃╰━╯┃╰╯┣┫┃╱┃━━╋┫╭╮┫╭╮┃╭╮┃\n"
            "┃╭━╮┃┃┃┃┃╰╮┣━━┃┃┃┃┃╰╯┃┃┃┃\n"
            "╰╯╱╰┻┻┻┻┻━╯╰━━┻┻╯╰┻━╮┣╯╰╯\n"
            "╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━╯┃\n"
            "╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━━╯\n"
            f"{me.first_name} ✅✅ BOT started successfully ✅✅"
        )

    async def stop(self, *args):
        await super().stop()      
        logging.info("Bot Stopped 🙄")
        
bot = Bot()
bot.run()
