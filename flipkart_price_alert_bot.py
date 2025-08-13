import time
import tempfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
PRODUCT_URL = "https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-128-gb/p/itmc8add40b88912?pid=MOBHYJ6QFUNQYFDH"
TARGET_PRICE = 45999  # Your desired price
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your bot token
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your chat ID

# --- SEND TELEGRAM ALERT ---
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# --- SELENIUM SETUP ---
chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # Uncomment for headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# ✅ Use a unique temporary Chrome profile to avoid "already in use" errors
chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(PRODUCT_URL)
    time.sleep(2)

    # Close login popup if it appears
    try:
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
    except:
        pass

    # Wait for price element to be visible
    wait = WebDriverWait(driver, 15)
    price_element = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div._30jeq3._16Jk6d"))
    )

    price_text = price_element.text.replace("₹", "").replace(",", "").strip()
    current_price = int(price_text)
    print(f"Current price: ₹{current_price}")

    # Check price threshold
    if current_price <= TARGET_PRICE:
        send_telegram_message(f"🎉 Price Alert! Samsung S24 is now ₹{current_price}.\n{PRODUCT_URL}")
    else:
        print("No price drop yet.")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
