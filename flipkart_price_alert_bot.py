import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
PRODUCT_URL = "https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-128-gb/p/itmc8add40b88912?pid=MOBHYJ6QFUNQYFDH&lid=LSTMOBHYJ6QFUNQYFDHVZACEH&marketplace=FLIPKART&q=s24&store=tyy%2F4io&srno=s_1_2&otracker=search&otracker1=search&fm=organic&iid=d4afac7f-f2f2-49fe-b92f-10c5966135f9.MOBHYJ6QFUNQYFDH.SEARCH&ppt=None&ppn=None&ssid=gtzu13tw8g0000001755064743419&qH=08eca8f85ffc96a4"  # change to your product URL
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
