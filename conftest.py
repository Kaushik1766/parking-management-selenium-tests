import pytest
from pytest_html import extras

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" :

        driver = item.funcargs.get("driver")

        if driver:
            screenshot = driver.get_screenshot_as_base64()

            if not hasattr(report, "extras"):
                report.extras = []

            report.extras.append(
                extras.image(screenshot, mime_type="image/png")
            )
