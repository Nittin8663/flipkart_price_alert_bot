import json
import time
import threading
import requests
from flask import Flask, render_template, request, redirect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ====== CONFIG ======
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
CHECK_INTERVAL = 3600  # seconds between checks
PRODUCTS_FILE = "products.json"
# ====================

app = Flask(__name__)

# ====== Helper Functions ======
def load_products():
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd")
        price_text = price_element.text.replace("₹", "").replace(",", "")
        driver.quit()
        return int(price_text)
    except:
        driver.quit()
        return None

# ====== Price Checker Thread ======
def price_checker():
    while True:
        products = load_products()
        for product in products:
            print(f"Checking price for: {product['name']}")
            price = get_price(product['url'])
            if price:
                print(f"Current price: ₹{price}")
                if price <= product['target_price']:
                    send_telegram_message(f"Price Alert! {product['name']} is ₹{price}\n{product['url']}")
                    print("Alert sent to Telegram!")
        time.sleep(CHECK_INTERVAL)

# ====== Flask Routes ======
@app.route("/")
def index():
    products = load_products()
    return render_template("index.html", products=products)

@app.route("/add", methods=["POST"])
def add_product():
    name = request.form["name"]
    url = request.form["url"]
    target_price = int(request.form["target_price"])
    products = load_products()
    products.append({"name": name, "url": url, "target_price": target_price})
    save_products(products)
    return redirect("/")

@app.route("/delete/<int:product_index>")
def delete_product(product_index):
    products = load_products()
    if 0 <= product_index < len(products):
        products.pop(product_index)
        save_products(products)
    return redirect("/")

@app.route("/edit/<int:product_index>", methods=["POST"])
def edit_product(product_index):
    products = load_products()
    if 0 <= product_index < len(products):
        products[product_index]["target_price"] = int(request.form["target_price"])
        save_products(products)
    return redirect("/")

# ====== Run Price Checker in Background ======
checker_thread = threading.Thread(target=price_checker, daemon=True)
checker_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
