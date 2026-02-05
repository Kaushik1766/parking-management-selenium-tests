import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from tests.constants import WEBSITE_URL

@pytest.fixture(scope='module')
def driver():
    wd = webdriver.Firefox()
    wd.get(WEBSITE_URL)
    yield wd
    wd.quit()

@pytest.fixture(autouse=True)
def clear_credentials(driver: WebDriver):
    driver.execute_script("window.localStorage.clear();")
    driver.get(WEBSITE_URL)

@pytest.mark.parametrize(
    ("name", "email", "password", "expected_login_button"),
    [
        ("valid email", "kaushik@a.com", "123", True),
        ("invalid email", "kaushikacom", "123", False),
    ],
)
def test_login(driver: WebDriver, name: str, email: str, password: str, expected_login_button: bool):
    email_textbox = driver.find_element(By.ID, "email")
    email_textbox.send_keys(email)
    password_textbox = driver.find_element(By.ID, "password")
    password_textbox.send_keys(password)

    login_btn = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/main[1]/app-login[1]/div[1]/div[2]/div[1]/form[1]/p-button[1]/button[1]")

    # print(login_btn.is_enabled())
    assert login_btn.is_enabled() == expected_login_button

    if expected_login_button:
        login_btn.click()
        WebDriverWait(driver, 5).until(
            lambda d: d.current_url.startswith(f"{WEBSITE_URL}user")
        )
        print(driver.current_url)
        assert driver.current_url.startswith(f"{WEBSITE_URL}user") is True


def test_admin_login(driver: WebDriver):
    email_textbox = driver.find_element(By.ID, "email")
    email_textbox.send_keys("admin@a.com")

    password_textbox = driver.find_element(By.ID, "password")
    password_textbox.send_keys("123")

    login_btn = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/main[1]/app-login[1]/div[1]/div[2]/div[1]/form[1]/p-button[1]/button[1]")

    assert login_btn.is_enabled() is True

    login_btn.click()
    WebDriverWait(driver, 5).until(
        lambda d: d.current_url.startswith(f"{WEBSITE_URL}admin")
    )
    assert driver.current_url.startswith(f"{WEBSITE_URL}admin") is True
