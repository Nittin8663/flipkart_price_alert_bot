from flask import Flask, render_template, request, redirect
import threading
import time
import json
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
PRODUCTS_FILE = "products.json"

# === UTILS ===
def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        r = requests.post(url, data=data, timeout=10)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram send error:", e)

def get_flipkart_price(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        price_tag = soup.find("div", {"class": re.compile(r"_30jeq3|_16Jk6d")})
        if price_tag:
            price_str = price_tag.get_text().replace("₹", "").replace(",", "").strip()
            return int(price_str)
    except Exception as e:
        print(f"Error fetching price for {url}: {e}")
    return None

# === PRICE CHECKER THREAD ===
def price_checker():
    while True:
        products = load_products()
        for p in products:
            if not p.get("enabled", True):
                continue
            current_price = get_flipkart_price(p["url"])
            if current_price is not None:
                print(f"Checking price for {p['name']} - ₹{current_price}")
                if current_price <= p["target_price"]:
                    send_telegram(f"Price alert! {p['name']} is ₹{current_price}\n{p['url']}")
        time.sleep(60)  # check every 60s

# === WEB ROUTES ===
@app.route("/")
def index():
    return render_template("index.html", products=load_products())

@app.route("/add", methods=["POST"])
def add_product():
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
def edit_product(index):
    products = load_products()
    products[index]["name"] = request.form["name"]
    products[index]["url"] = request.form["url"]
    products[index]["target_price"] = int(request.form["target_price"])
    save_products(products)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete_product(index):
    products = load_products()
    products.pop(index)
    save_products(products)
    return redirect("/")

@app.route("/toggle/<int:index>")
def toggle_product(index):
    products = load_products()
    products[index]["enabled"] = not products[index].get("enabled", True)
    save_products(products)
    return redirect("/")

# === START APP ===
if __name__ == "__main__":
    t = threading.Thread(target=price_checker, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
