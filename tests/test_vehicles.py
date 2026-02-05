import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from tests.constants import WEBSITE_URL


@pytest.fixture(scope='module')
def driver():
    wd = webdriver.Firefox()
    wd.get(WEBSITE_URL)
    yield wd
    wd.quit()


@pytest.fixture(autouse=True)
def login_user(driver: WebDriver):
    driver.execute_script("window.localStorage.clear();")
    driver.get(WEBSITE_URL)

    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys("kaushik@a.com")

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("123")

    login_btn = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/main[1]/app-login[1]/div[1]/div[2]/div[1]/form[1]/p-button[1]/button[1]")
    login_btn.click()

    WebDriverWait(driver, 5).until(
        lambda d: d.current_url.startswith(f"{WEBSITE_URL}user/vehicles")
    )

    _wait_for_loading_overlay(driver)
    WebDriverWait(driver, 10).until(lambda d: d.find_element(By.ID, "numberplate"))


def _wait_for_loading_overlay(driver: WebDriver) -> None:
    WebDriverWait(driver, 10).until(
        lambda d: not any(el.is_displayed() for el in d.find_elements(By.CSS_SELECTOR, ".loading-overlay"))
    )


def _select_vehicle_type(driver: WebDriver, vehicle_type: str) -> None:
    _wait_for_loading_overlay(driver)

    dropdown = WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "[role='combobox'], [id^='pn_id_']")
    )
    dropdown.click()

    option = WebDriverWait(driver, 10).until(
        lambda d: next(
            (el for el in d.find_elements(By.CSS_SELECTOR, "[role='option']") if el.is_displayed() and el.text.strip() == vehicle_type),
            None,
        )
    )
    if option is None:
        raise ValueError(f"Vehicle type '{vehicle_type}' not found in dropdown.")
    driver.execute_script("arguments[0].click();", option)

    WebDriverWait(driver, 10).until(
        lambda d: not any(el.is_displayed() for el in d.find_elements(By.CSS_SELECTOR, "[role='option']"))
    )


def _register_button(driver: WebDriver):
    return driver.find_element(By.XPATH, "//button[normalize-space()='Register Vehicle']")


def _park_button(driver: WebDriver, plate: str):
    return driver.find_elements(By.XPATH, f"//h3[normalize-space()='{plate}']/ancestor::div[contains(@class,'card')]//button[normalize-space()='Park']")


def _unpark_button(driver: WebDriver, plate: str):
    return driver.find_elements(By.XPATH, f"//h3[normalize-space()='{plate}']/ancestor::div[contains(@class,'card')]//button[normalize-space()='Unpark']")


def _wait_register_enabled(driver: WebDriver, timeout: int = 10) -> bool:
    try:
        _wait_for_loading_overlay(driver)
        WebDriverWait(driver, timeout).until(lambda d: _register_button(d).is_enabled())
        return True
    except Exception:
        return False


def _wait_for_vehicle_card(driver: WebDriver, plate: str):
    return WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.XPATH, f"//h3[normalize-space()='{plate}']")
    )


def _delete_vehicle(driver: WebDriver, plate: str) -> None:
    delete_btn = WebDriverWait(driver, 5).until(
        lambda d: d.find_element(
            By.XPATH,
            f"//h3[normalize-space()='{plate}']/ancestor::div[contains(@class,'card')]//button[contains(@class,'p-button-danger')]",
        )
    )
    delete_btn.click()

    confirm_btn = WebDriverWait(driver, 5).until(
        lambda d: next(
            (b for b in d.find_elements(By.XPATH, "//button[normalize-space()='Delete']") if b.is_displayed()),
            None,
        )
    )
    driver.execute_script("arguments[0].click();", confirm_btn)

    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.XPATH, f"//h3[normalize-space()='{plate}']")) == 0
    )


def test_numberplate_length_validation(driver: WebDriver):
    plate_input = driver.find_element(By.ID, "numberplate")
    plate_input.clear()
    plate_input.send_keys("SHORT123")

    _select_vehicle_type(driver, "TwoWheeler")
    assert _wait_register_enabled(driver, timeout=5) is False

    plate_input.clear()
    plate_input.send_keys("KA01AB1234")
    _select_vehicle_type(driver, "TwoWheeler")
    assert _wait_register_enabled(driver)


def test_add_and_delete_vehicle(driver: WebDriver):
    unique_plate = f"KA{int(time.time()) % 100000000:08d}"

    plate_input = driver.find_element(By.ID, "numberplate")
    plate_input.clear()
    plate_input.send_keys(unique_plate)

    _select_vehicle_type(driver, "FourWheeler")

    register_btn = _register_button(driver)
    WebDriverWait(driver, 10).until(lambda d: register_btn.is_enabled())
    register_btn.click()

    _wait_for_vehicle_card(driver, unique_plate)
    _delete_vehicle(driver, unique_plate)


def test_park_and_unpark_vehicle(driver: WebDriver):
    # Ensure a vehicle exists; create one if needed.
    existing_cards = driver.find_elements(By.XPATH, "//h3[not(normalize-space()='Register Vehicle')]")
    plate = None
    for card in existing_cards:
        text = card.text.strip()
        if text:
            plate = text
            break

    if plate is None:
        plate = f"AUTO{int(time.time()) % 1000000:06d}"
        plate_input = driver.find_element(By.ID, "numberplate")
        plate_input.clear()
        plate_input.send_keys(plate)
        _select_vehicle_type(driver, "FourWheeler")
        register_btn = _register_button(driver)
        WebDriverWait(driver, 10).until(lambda d: register_btn.is_enabled())
        register_btn.click()
        _wait_for_vehicle_card(driver, plate)

    # Park the vehicle
    park_buttons = _park_button(driver, plate)
    unpark_buttons = _unpark_button(driver, plate)

    if not park_buttons and not unpark_buttons:
        pytest.skip("No Park/Unpark button available for the vehicle card")

    if park_buttons:
        driver.execute_script("arguments[0].click();", park_buttons[0])
        WebDriverWait(driver, 10).until(lambda d: len(_unpark_button(d, plate)) > 0)
    else:
        # Already parked; ensure unpark button present
        WebDriverWait(driver, 10).until(lambda d: len(_unpark_button(d, plate)) > 0)

    # Unpark the vehicle
    unpark_buttons = _unpark_button(driver, plate)
    driver.execute_script("arguments[0].click();", unpark_buttons[0])
    WebDriverWait(driver, 10).until(lambda d: len(_park_button(d, plate)) > 0)
