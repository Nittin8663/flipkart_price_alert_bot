import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ====== CONFIG ======
FLIPKART_URL = "https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-128-gb/p/itmc8add40b88912?pid=MOBHYJ6QFUNQYFDH"
TARGET_PRICE = 47000  # Set your desired alert price

TELEGRAM_BOT_TOKEN = "8213851536:AAFXJenYJZrzKLWzCPx81DO2XrAdroGkjl0"
TELEGRAM_CHAT_ID = "6018830024"
CHECK_INTERVAL = 60  # seconds between checks
# =====================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_price():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(FLIPKART_URL)
    time.sleep(5)  # Wait for page to load fully

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd")
        price_text = price_element.text.replace("₹", "").replace(",", "")
        driver.quit()
        return int(price_text)
    except Exception as e:
        driver.quit()
        print("Error fetching price:", e)
        return None

def main():
    while True:
        print("Checking price...")
        price = get_price()
        if price:
            print(f"Current price: ₹{price}")
            if price <= TARGET_PRICE:
                send_telegram_message(f"Price Alert! Current price is ₹{price}\n{FLIPKART_URL}")
                print("Alert sent to Telegram!")
        else:
            print("Failed to fetch price.")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
