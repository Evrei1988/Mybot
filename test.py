from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Запуск Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 1. Открываем Google и входим в аккаунт
driver.get("https://accounts.google.com/signin")
time.sleep(3)

email_input = driver.find_element(By.XPATH, "//input[@type='email']")
email_input.send_keys("your-email@gmail.com")
email_input.send_keys(Keys.ENTER)
time.sleep(3)

password_input = driver.find_element(By.XPATH, "//input[@type='password']")
password_input.send_keys("your-password")
password_input.send_keys(Keys.ENTER)
time.sleep(5)

# 2. Переходим к форме
driver.get("https://docs.google.com/forms/d/e/your-form-ID/viewform")
time.sleep(3)

# 3. Заполняем форму
input_field = driver.find_element(By.XPATH, "//input[@aria-label='Name']")
input_field.send_keys("Sergei Posysoev")

submit_button = driver.find_element(By.XPATH, "//span[text()='Submit']")
submit_button.click()

print("✅ Форма отправлена!")
time.sleep(5)
driver.quit()

