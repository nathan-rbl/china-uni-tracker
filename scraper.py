import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup

# Load API credentials from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Sends a notification directly to your Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  Telegram credentials missing. Skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"  Failed to send Telegram alert: {e}")

# 1. Load targets
with open("sites.json", "r", encoding="utf-8") as file:
    sites = json.load(file)

# 2. Load previous scan history state
history_file = "history.json"
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as file:
        history = json.load(file)
else:
    history = {}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=== Starting University Portal Scan ===\n")
updated_history = {}

for site in sites:
    name = site["university"]
    url = site["url"]
    print(f"Checking: {name}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts and style tags to isolate human-readable text
            for script in soup(["script", "style"]):
                script.decompose()
            text_content = soup.get_text(separator=" ", strip=True)
            
            # Generate a unique hash signature of the page content
            current_hash = hashlib.md5(text_content.encode("utf-8")).hexdigest()
            previous_hash = history.get(url)
            
            if previous_hash is None:
                print(f"  Status: INITIALIZED (First time recording state)")
            elif current_hash != previous_hash:
                print(f"  Status: UPDATE DETECTED!")
                alert_msg = f"🚨 *University Portal Update Detected!*\n\n*University:* {name}\n*Link:* {url}"
                send_telegram_alert(alert_msg)
            else:
                print(f"  Status: NO CHANGE")
                
            updated_history[url] = current_hash
        else:
            print(f"  Status: FAILED (Code {response.status_code})")
            updated_history[url] = history.get(url, "")
            
    except Exception as error:
        print(f"  Status: ERROR - {error}")
        updated_history[url] = history.get(url, "")

# 3. Save updated state back to history.json
with open(history_file, "w", encoding="utf-8") as file:
    json.dump(updated_history, file, indent=2)

print("\n=== Scan Complete ===")
