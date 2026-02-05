from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time

def main():
    driver = webdriver.Edge()
    driver.get("https://www.google.com")
    search = driver.find_element(By.CLASS_NAME, "gLFyf")
    search.send_keys("hello world")
    search.send_keys(Keys.RETURN)
    input()
    driver.quit()


if __name__ == "__main__":
    main()