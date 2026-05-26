"""
Base Page — Page Object Model foundation.

Every page class inherits from here so we get a shared set of safe
helper methods (find, click, type) that already include explicit waits.
This removes wait boilerplate from every subclass and keeps page objects
focused on *what* the page does rather than *how* to wait for it.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


DEFAULT_TIMEOUT = 10  # seconds; adjust globally here rather than per page


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # Storing the wait object on the instance avoids recreating it on
        # every helper call while still allowing per-call timeout overrides.
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def open(self, url: str):
        self.driver.get(url)

    @property
    def title(self) -> str:
        return self.driver.title

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ------------------------------------------------------------------
    # Element helpers — all use explicit waits so callers don't have to
    # ------------------------------------------------------------------

    def find(self, locator: tuple):
        """Wait for element to be present in DOM, then return it."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: tuple):
        """Wait for element to be visible AND enabled before returning it.

        Use this for buttons/links — presence_of_element_located returns the
        element even when it is invisible, which causes click() to fail.
        """
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_visible(self, locator: tuple):
        """Wait for element to be visible (rendered with non-zero size)."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: tuple):
        self.find_clickable(locator).click()

    def type(self, locator: tuple, text: str):
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.find_visible(locator).text

    def is_visible(self, locator: tuple) -> bool:
        try:
            return self.find_visible(locator).is_displayed()
        except Exception:
            return False
