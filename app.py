import json
import threading
import time
import requests
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# JSON Storage
PRODUCTS_FILE = "products.json"

app = Flask(__name__)

# ------------------ Helper Functions ------------------ #
def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
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
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Try Flipkart's common price selectors
    price_tag = soup.select_one("._30jeq3._16Jk6d")
    if price_tag:
        return int(price_tag.text.replace("₹", "").replace(",", "").strip())
    return None

# ------------------ Price Checker ------------------ #
def price_checker():
    while True:
        products = load_products()
        updated = False

        for p in products:
            if not p.get("enabled", True):
                continue

            print(f"Checking price for: {p['name']}")
            price = get_price(p["url"])
            p["current_price"] = price

            if price is not None:
                print(f"Current price: ₹{price}")
                if price <= p["target_price"]:
                    send_telegram_message(
                        f"Price Alert! {p['name']} is now ₹{price}\n{p['url']}"
                    )

            updated = True

        if updated:
            save_products(products)

        time.sleep(60)

# ------------------ Flask Routes ------------------ #
@app.route("/")
def index():
    products = load_products()
    for p in products:
        if "current_price" not in p:
            p["current_price"] = get_price(p["url"])
    return render_template("index.html", products=products)

@app.route("/add", methods=["POST"])
def add():
    products = load_products()
    products.append({
        "name": request.form["name"],
        "url": request.form["url"],
        "target_price": int(request.form["target_price"]),
        "enabled": True
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
