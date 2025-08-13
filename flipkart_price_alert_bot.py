import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram_utils import send_telegram_message

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

CHECK_INTERVAL = config["check_interval"]

def get_prices(driver, products):
    results = []
    for product in products:
        name = product.get("name", "Unknown Product")
        url = product["url"]
        target_price = product["target_price"]

        print(f"\nChecking price for: {name}")
        print(f"Product link: {url}")

        try:
            driver.get(url)
            time.sleep(5)  # wait for page load

            price_element = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd")
            price_text = price_element.text.replace("₹", "").replace(",", "")
            price = int(price_text)
            print(f"Current price: ₹{price}")

            if price <= target_price:
                send_telegram_message(f"📢 Price Alert! {name} is now ₹{price}\n{url}")
                print("Alert sent to Telegram!")

        except Exception as e:
            print(f"Error fetching price for {name}: {e}")

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    while True:
        driver = webdriver.Chrome(options=chrome_options)  # open once per cycle
        get_prices(driver, config["products"])
        driver.quit()  # close after all products are checked

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
