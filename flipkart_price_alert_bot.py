from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

# --- CONFIG ---
PRODUCT_URL = "https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-128-gb/p/itmc8add40b88912?pid=MOBHYJ6QFUNQYFDH&lid=LSTMOBHYJ6QFUNQYFDHVZACEH&marketplace=FLIPKART&q=s24&store=tyy%2F4io&srno=s_1_2&otracker=search&otracker1=search&fm=organic&iid=d4afac7f-f2f2-49fe-b92f-10c5966135f9.MOBHYJ6QFUNQYFDH.SEARCH&ssid=gtzu13tw8g0000001755064743419&qH=08eca8f85ffc96a4"
TARGET_PRICE = 45999
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# --- TELEGRAM FUNCTION ---
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# --- SELENIUM SETUP ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # remove this line if you want to see the browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(PRODUCT_URL)

    # Wait for page load
    time.sleep(3)

    # Try to close the login popup by sending ESC
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(1)

    # Wait for the price element to appear
    wait = WebDriverWait(driver, 10)
    price_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div._30jeq3._16Jk6d"))
    )

    price_text = price_element.text.replace("₹", "").replace(",", "").strip()
    current_price = int(price_text)

    print(f"Current price: ₹{current_price}")
    if current_price <= TARGET_PRICE:
        send_telegram_message(f"🎉 Price Alert! Samsung S24 is now ₹{current_price}.\n{PRODUCT_URL}")
    else:
        print("No price drop yet.")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
