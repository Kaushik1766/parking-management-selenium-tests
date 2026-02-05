import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from tests.constants import WEBSITE_URL


@pytest.fixture(scope='module')
def driver():
    wd = webdriver.Firefox()
    wd.get(f"{WEBSITE_URL}signup")
    yield wd
    wd.quit()


@pytest.fixture(autouse=True)
def clear_credentials(driver: WebDriver):
    driver.execute_script("window.localStorage.clear();")
    driver.get(f"{WEBSITE_URL}signup")


def _select_office(driver: WebDriver, office_text: str) -> None:
    dropdown = driver.find_element(By.CSS_SELECTOR, "[role='combobox'], [id^='pn_id_']")
    dropdown.click()

    option = WebDriverWait(driver, 5).until(
        lambda d: next(
            (el for el in d.find_elements(By.CSS_SELECTOR, "[role='option']") if el.text.strip() == office_text),
            None,
        )
    )
    if option is None:
        raise ValueError(f"Office option '{office_text}' not found in dropdown.")
    option.click()

    # Wait for the dropdown panel to close so it does not obscure the submit button
    WebDriverWait(driver, 5).until(
        lambda d: not any(el.is_displayed() for el in d.find_elements(By.CSS_SELECTOR, "[role='option']"))
    )


@pytest.mark.parametrize(
    ("name", "email", "user_name", "password", "office_option", "expected_submit_enabled"),
    [
        ("valid signup", f"testemail{int(time.time())}@example.com", "user1", "Password123!", "Samsung", True),
        ("invalid email", "userexample.com", "user1", "Password123!", "Samsung", False),
        ("missing office", "user@example.com", "user1", "Password123!", None, False),
    ],
)
def test_signup(driver: WebDriver, name: str, email: str, user_name: str, password: str, office_option: str | None, expected_submit_enabled: bool):
    email_textbox = driver.find_element(By.ID, "email")
    email_textbox.send_keys(email)

    username_textbox = driver.find_element(By.ID, "userName")
    username_textbox.send_keys(user_name)

    password_textbox = driver.find_element(By.ID, "password")
    password_textbox.send_keys(password)

    if office_option:
        _select_office(driver, office_option)

    submit_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Submit']")

    assert submit_btn.is_enabled() == expected_submit_enabled

    if expected_submit_enabled:
        submit_btn.click()
        WebDriverWait(driver, 5).until(
            lambda d: d.current_url != f"{WEBSITE_URL}signup" or d.find_elements(By.CLASS_NAME, "p-toast-message")
        )


