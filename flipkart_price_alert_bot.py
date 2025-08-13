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
alert_sent = {}

def get_price(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd")
        price_text = price_element.text.replace("₹", "").replace(",", "")
        driver.quit()
        return int(price_text)
    except Exception as e:
        driver.quit()
        print(f"Error fetching price for {url}: {e}")
        return None

def main():
    while True:
        for product in config["products"]:
            url = product["url"]
            target_price = product["target_price"]

            if url not in alert_sent:
                alert_sent[url] = False

            print(f"Checking price for: {url}")
            price = get_price(url)

            if price:
                print(f"Current price: ₹{price}")
                if price <= target_price and not alert_sent[url]:
                    send_telegram_message(f"Price Alert! ₹{price}\n{url}")
                    alert_sent[url] = True
                    print("Alert sent to Telegram!")
            else:
                print("Failed to fetch price.")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
