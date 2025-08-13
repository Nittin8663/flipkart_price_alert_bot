from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile

options = Options()
options.add_argument("--headless=new")  # Try headless mode for servers
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
user_data_dir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")
print("Title:", driver.title)
driver.quit()
