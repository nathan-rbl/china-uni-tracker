import json
import requests
from bs4 import BeautifulSoup

# 1. Load your target universities from sites.json
with open("sites.json", "r", encoding="utf-8") as file:
    sites = json.load(file)

# 2. Add browser headers so university servers accept the request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=== Starting University Portal Scan ===\n")

# 3. Loop through each target website
for site in sites:
    name = site["university"]
    url = site["url"]
    print(f"Checking: {name}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract page title
            page_title = soup.title.string.strip() if soup.title else "No Title Found"
            
            # Print success status and basic info
            print(f"  Status: SUCCESS (200)")
            print(f"  Page Title: {page_title}\n")
        else:
            print(f"  Status: FAILED (Code {response.status_code})\n")
            
    except Exception as error:
        print(f"  Status: ERROR - {error}\n")

print("=== Scan Complete ===")
