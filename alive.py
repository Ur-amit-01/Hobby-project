import threading
import requests
import time

# Function to ping the bot's own web server
def ping_self():
    while True:
        try:
            # Replace with your bot's actual URL
            response = requests.get("https://your-bot-url.koyeb.app/")
            print(f"Pinged self: {response.status_code}")
        except Exception as e:
            print(f"Failed to ping self: {e}")
        time.sleep(300)  # Ping every 5 minutes (300 seconds)

# Start the self-pinging thread
def start_pinging():
    t = threading.Thread(target=ping_self)
    t.daemon = True  # Daemonize thread to exit when the main program exits
    t.start()

# Call this function in your bot's startup code
start_pinging()
