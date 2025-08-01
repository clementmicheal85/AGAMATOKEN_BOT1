import os
import requests
import time
import threading
import gunicorn
from flask import Flask

app = Flask(__name__)

# Configuration
QUICKNODE_URL = os.getenv('QUICKNODE_URL')
TELEGRAM_TOKEN = "8322021979:AAEVQjYXO4Yutqil1c6tDeQYLa97U-mnYFM"
GROUP_ID = "1002718015353"
TOKEN_CONTRACT = "0x2119de8f257d27662991198389E15Bf8d1F4aB24"
MIN_BNB = 0.025
LOGO_URL = "https://www.agamacoin.com/agama-logo-new.png"
BSC_LINK = "https://bscscan.com/token/0x2119de8f257d27662991198389E15Bf8d1F4aB24"

# Global variables
last_checked_block = None
app_started = False

def get_current_block():
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    response = requests.post(QUICKNODE_URL, json=payload).json()
    return int(response['result'], 16)

def get_transactions():
    global last_checked_block
    current_block = get_current_block()
    
    if last_checked_block is None:
        last_checked_block = current_block - 100
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": hex(last_checked_block),
            "toBlock": hex(current_block),
            "address": TOKEN_CONTRACT,
            "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]
        }],
        "id": 1
    }
    
    response = requests.post(QUICKNODE_URL, json=payload).json()
    last_checked_block = current_block
    return response.get('result', [])

def get_tx_details(tx_hash):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1
    }
    response = requests.post(QUICKNODE_URL, json=payload).json()
    return response.get('result', {})

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    caption = f"<b>{message}</b>\n\n🔹 <a href='{BSC_LINK}'>View Contract on BscScan</a>"
    
    payload = {
        "chat_id": GROUP_ID,
        "photo": LOGO_URL,
        "caption": caption,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def monitor_transactions():
    while True:
        try:
            logs = get_transactions()
            for log in logs:
                tx_hash = log['transactionHash']
                tx = get_tx_details(tx_hash)
                
                if tx and 'value' in tx:
                    bnb_value = int(tx['value'], 16) / 10**18
                    if bnb_value >= MIN_BNB:
                        message = (
                            "🚀 NEW BUY ALERT! 🚀\n\n"
                            f"🔥 {bnb_value:.3f} BNB purchase detected!\n\n"
                            "A new investor has joined the Agama revolution! "
                            "Secure your position in the next-generation DeFi ecosystem."
                        )
                        send_telegram_alert(message)
            time.sleep(180)  # Check every 3 minutes
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(60)

def send_reminder():
    while True:
        message = (
            "⏰ REMINDER: LIMITED-TIME OPPORTUNITY ⏰\n\n"
            "💰 Buy Agama Coin NOW and become an early holder!\n\n"
            "Don't miss your chance to be part of the future of "
            "decentralized finance at ground-floor prices."
        )
        send_telegram_alert(message)
        time.sleep(1800)  # 30 minutes

@app.before_first_request
def start_background_tasks():
    global app_started
    if not app_started:
        threading.Thread(target=monitor_transactions, daemon=True).start()
        threading.Thread(target=send_reminder, daemon=True).start()
        app_started = True
        print("Background tasks started")

@app.route('/')
def home():
    return "Agama Price Alert Bot is Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
