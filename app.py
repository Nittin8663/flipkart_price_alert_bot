import json
import threading
import time
import requests
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup

# ------------------ CONFIG ------------------ #
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
PRODUCTS_FILE = "products.json"
CHECK_INTERVAL = 60  # seconds

app = Flask(__name__)

# ------------------ Helper Functions ------------------ #
def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def get_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Try multiple selectors in case Flipkart changes class
        price_tag = soup.select_one("._30jeq3._16Jk6d") or soup.select_one("div._30jeq3")
        if price_tag:
            price_text = price_tag.text.replace("₹", "").replace(",", "").strip()
            return int(price_text)
    except Exception as e:
        print(f"Error fetching price for {url}: {e}")
    return None

# ------------------ Price Checker ------------------ #
def price_checker():
    while True:
        products = load_products()
        for p in products:
            if not p.get("enabled", True):
                continue

            price = get_price(p["url"])
            p["current_price"] = price

            if price is not None:
                print(f"Checking price for: {p['name']}")
                print(f"Current price: ₹{price}")
                if price <= p["target_price"] and not p.get("alert_sent", False):
                    send_telegram_message(
                        f"Price Alert! {p['name']} is now ₹{price}\n{p['url']}"
                    )
                    p["alert_sent"] = True  # Prevent repeated messages

        save_products(products)
        time.sleep(CHECK_INTERVAL)

# ------------------ Flask Routes ------------------ #
@app.route("/")
def index():
    products = load_products()
    for p in products:
        try:
            p["current_price"] = get_price(p["url"])
        except:
            p["current_price"] = None
    save_products(products)
    return render_template("index.html", products=products)

@app.route("/add", methods=["POST"])
def add():
    products = load_products()
    products.append({
        "name": request.form["name"],
        "url": request.form["url"],
        "target_price": int(request.form["target_price"]),
        "enabled": True,
        "current_price": None,
        "alert_sent": False
    })
    save_products(products)
    return redirect("/")

@app.route("/edit/<int:index>", methods=["POST"])
def edit(index):
    products = load_products()
    if 0 <= index < len(products):
        products[index]["name"] = request.form["name"]
        products[index]["url"] = request.form["url"]
        products[index]["target_price"] = int(request.form["target_price"])
        products[index]["alert_sent"] = False  # reset alert
    save_products(products)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    products = load_products()
    if 0 <= index < len(products):
        products.pop(index)
    save_products(products)
    return redirect("/")

@app.route("/toggle/<int:index>")
def toggle(index):
    products = load_products()
    if 0 <= index < len(products):
        products[index]["enabled"] = not products[index].get("enabled", True)
    save_products(products)
    return redirect("/")

# ------------------ Main ------------------ #
if __name__ == "__main__":
    threading.Thread(target=price_checker, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
