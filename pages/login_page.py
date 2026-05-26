"""
Login Page — concrete Page Object for the-internet.herokuapp.com/login.

Shows how a real page object works: locators live here (not scattered
in test code), and public methods express user intent ("login_as")
rather than low-level actions ("find input, type, click button").

When the site's DOM changes, we only update this file — tests stay untouched.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://the-internet.herokuapp.com/login"

    # Locators are constants so a typo shows up at import time, not at runtime.
    # CSS selectors are preferred over XPath when the id/class is stable —
    # they are shorter, faster, and easier to read.
    _USERNAME_INPUT = (By.ID, "username")
    _PASSWORD_INPUT = (By.ID, "password")
    _LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    _FLASH_MESSAGE = (By.ID, "flash")

    def open_login_page(self):
        self.open(self.URL)

    def login_as(self, username: str, password: str):
        """High-level action: fill credentials and submit.

        Callers read like plain English: page.login_as("admin", "wrong")
        """
        self.type(self._USERNAME_INPUT, username)
        self.type(self._PASSWORD_INPUT, password)
        self.click(self._LOGIN_BUTTON)

    def get_flash_message(self) -> str:
        return self.get_text(_FLASH_MESSAGE := self._FLASH_MESSAGE)

    def is_login_successful(self) -> bool:
        # The success message contains "You logged into a secure area"
        return "secure" in self.get_text(self._FLASH_MESSAGE).lower()

    def is_login_failed(self) -> bool:
        return "invalid" in self.get_text(self._FLASH_MESSAGE).lower()
