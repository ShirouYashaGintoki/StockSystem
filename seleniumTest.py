from selenium import webdriver

DRIVER = 'chromedriver'
driver = webdriver.Chrome(DRIVER)
driver.get('https://www.tradingview.com/chart/?symbol=AMZN')
screenshot = driver.save_screenshot('my_screenshot.png')
driver.quit()