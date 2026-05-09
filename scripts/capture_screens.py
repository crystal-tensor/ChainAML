import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE = os.path.dirname(os.path.dirname(__file__))
OUT = os.path.join(BASE, 'static', 'screenshots')
os.makedirs(OUT, exist_ok=True)

def setup_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1440,900')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def main():
    driver = setup_driver()
    try:
        # 首页流程（index.html）
        driver.get('http://localhost:6922/')
        time.sleep(1.5)
        # 触发流程
        try:
            btn = driver.find_element('css selector', 'button.btn.btn-primary')
            btn.click()
        except Exception:
            pass
        # 分阶段等待与截图
        time.sleep(1.2)
        driver.save_screenshot(os.path.join(OUT, 'step1.png'))
        time.sleep(1.2)
        driver.save_screenshot(os.path.join(OUT, 'step2.png'))
        time.sleep(1.2)
        driver.save_screenshot(os.path.join(OUT, 'step3.png'))
        time.sleep(1.2)
        driver.save_screenshot(os.path.join(OUT, 'step4_ring.png'))

        # 分类列表页
        driver.get('http://localhost:6922/classification/spray')
        time.sleep(1.0)
        driver.save_screenshot(os.path.join(OUT, 'classification_list.png'))
    finally:
        driver.quit()

if __name__ == '__main__':
    main()

