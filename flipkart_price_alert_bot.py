import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

# --- CONFIGURATION ---
FLIPKART_PRODUCT_URL = "https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-128-gb/p/itmc8add40b88912?pid=MOBHYJ6QFUNQYFDH&lid=LSTMOBHYJ6QFUNQYFDHVZACEH&marketplace=FLIPKART&q=s24&store=tyy%2F4io&srno=s_1_2&otracker=search&otracker1=search&fm=organic&iid=d4afac7f-f2f2-49fe-b92f-10c5966135f9.MOBHYJ6QFUNQYFDH.SEARCH&ppt=None&ppn=None&ssid=gtzu13tw8g0000001755064743419&qH=08eca8f85ffc96a4"  # Change to your product URL
PRICE_THRESHOLD = 1000  # Update to your desired price
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
CHECK_INTERVAL = 600  # seconds between checks

def get_price(driver):
    driver.get(FLIPKART_PRODUCT_URL)
    time.sleep(3)  # wait for page to load
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "._30jeq3._16Jk6d")
        price_text = price_element.text.replace("₹", "").replace(",", "").strip()
        price = int(price_text)
        return price
    except Exception as e:
        print("Error fetching price:", e)
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def main():
    driver = webdriver.Chrome()  # Ensure chromedriver is in PATH
    try:
        while True:
            price = get_price(driver)
            if price is not None:
                print(f"Current price: ₹{price}")
                if price < PRICE_THRESHOLD:
                    send_telegram_message(f"Flipkart Price Alert!\nPrice dropped to ₹{price}\n{FLIPKART_PRODUCT_URL}")
                    print("Telegram notification sent!")
                    break
            else:
                print("Could not fetch price. Retrying...")
            time.sleep(CHECK_INTERVAL)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
