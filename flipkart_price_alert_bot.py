import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
PRODUCT_URL = "https://www.flipkart.com/apple-iphone-15-pro-max-blue-titanium-256-gb/p/itm6e1c11f5b6f0e"  # change to your product URL
TARGET_PRICE = 150000  # change to your desired price
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# --- FUNCTIONS ---
def get_price():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139 Safari/537.36"
    }
    resp = requests.get(PRODUCT_URL, headers=headers)
    soup = BeautifulSoup(resp.text, "lxml")

    price_tag = soup.find("div", class_="_30jeq3 _16Jk6d")
    if not price_tag:
        raise Exception("Price element not found! The page structure might have changed.")

    price = int(price_tag.text.replace("₹", "").replace(",", "").strip())
    return price

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# --- MAIN ---
if __name__ == "__main__":
    try:
        current_price = get_price()
        print(f"Current price: ₹{current_price}")

        if current_price <= TARGET_PRICE:
            send_telegram_message(f"🎉 Price Alert! The product is now ₹{current_price}.\n{PRODUCT_URL}")
        else:
            print("No price drop yet.")
    except Exception as e:
        print(f"Error: {e}")
