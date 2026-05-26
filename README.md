# Selenium Practice

A hands-on reference project covering the core Selenium WebDriver concepts in Python. Built to work as both a runnable demo and a copy-paste toolkit for real test automation work.

**Target site:** [the-internet.herokuapp.com](https://the-internet.herokuapp.com) — purpose-built for Selenium practice, each page isolates one browser feature.

---

## What's inside

```
selenium-practice/
├── selenium_practice.py   # Main showcase — 14 sections, one per concept
├── pages/
│   ├── base_page.py       # Page Object Model base class (reusable wait helpers)
│   └── login_page.py      # Concrete page object example (login flow)
└── requirements.txt
```

### `selenium_practice.py` — section by section

| # | Section | What it covers |
|---|---------|----------------|
| 1 | Driver setup | Chrome options, headless mode, webdriver-manager |
| 2 | Navigation | `get()`, `back()`, `forward()`, `refresh()`, `title`, `current_url` |
| 3 | Locator strategies | All 8: ID, Name, Class, CSS, XPath, Link Text, Partial Link Text, Tag Name |
| 4 | Element interactions | `click`, `send_keys`, `clear`, `get_attribute`, `is_displayed`, `is_selected` |
| 5 | Waits | Implicit vs. explicit (`WebDriverWait` + `expected_conditions`), why explicit wins |
| 6 | Select dropdowns | `Select` class — by visible text, by value, by index |
| 7 | Alerts | JS alert / confirm / prompt — `accept()`, `dismiss()`, `send_keys()` |
| 8 | Frames / iframes | `switch_to.frame()`, `default_content()` |
| 9 | Multiple windows | `window_handles`, `switch_to.window()`, closing tabs |
| 10 | ActionChains | Hover, double-click, right-click, drag-and-drop |
| 11 | JavaScript execution | `execute_script()` — scroll, highlight elements, read DOM properties |
| 12 | Screenshots | Full page and element-level PNG capture |
| 13 | Cookies | Read, add, delete, inject session cookies |
| 14 | Page Object Model | How POM keeps tests readable when the DOM changes |

### `pages/` — Page Object Model

`base_page.py` provides shared helpers (`find`, `click`, `type`, `is_visible`) that already include explicit waits — so page subclasses only describe what a page does, not how to wait for it.

`login_page.py` shows a concrete implementation: locators are constants at the top, and public methods (`login_as`, `is_login_successful`) read like plain English in tests.

---

## Setup

**Requirements:** Python 3.9+, Google Chrome installed.

```bash
pip3 install -r requirements.txt
```

`webdriver-manager` downloads the correct ChromeDriver automatically — no manual version matching needed.

---

## How to run

### Run the full demo

```bash
python3 selenium_practice.py
```

A Chrome window opens and walks through all 14 sections. Each section prints what it finds and does. If the practice site's HTML has changed and a locator goes stale, that section prints `[SKIPPED]` and the rest continue.

### Run headless (no visible browser)

Open `selenium_practice.py` and change the `run_all()` function:

```python
driver = create_driver(headless=True)
```

Useful for running in a terminal-only environment or CI pipeline.

### Run a single section

Call any section function directly from a Python REPL or a small script:

```python
from selenium_practice import create_driver, demo_alerts

driver = create_driver(headless=False)
try:
    demo_alerts(driver)
finally:
    driver.quit()
```

---

## For QA engineers

### Adapting locators to your own app

The locator strategies in section 3 apply to any web app. Priority order for reliability:

1. `By.ID` — fastest, most stable. Request unique IDs from devs if missing.
2. `By.CSS_SELECTOR` — flexible, readable, covers most cases.
3. `By.XPATH` — reach for this when you need to traverse up the DOM or match by text.
4. Avoid `By.CLASS_NAME` for styling classes (`btn`, `active`) — they change with redesigns.

### Reusing the Page Object base class

Copy `pages/base_page.py` into your project and subclass it for each page you test:

```python
from pages.base_page import BasePage
from selenium.webdriver.common.by import By

class CheckoutPage(BasePage):
    URL = "https://your-app.com/checkout"
    _PLACE_ORDER_BTN = (By.ID, "place-order")
    _CONFIRMATION_MSG = (By.CSS_SELECTOR, ".order-confirmation")

    def place_order(self):
        self.click(self._PLACE_ORDER_BTN)

    def is_order_confirmed(self) -> bool:
        return self.is_visible(self._CONFIRMATION_MSG)
```

Tests then read like requirements:
```python
page = CheckoutPage(driver)
page.open(page.URL)
page.place_order()
assert page.is_order_confirmed()
```

### Taking a screenshot on test failure

Use the screenshot helper from section 12 in a pytest fixture so failures are automatically captured:

```python
import pytest

@pytest.fixture(autouse=True)
def screenshot_on_failure(driver, request):
    yield
    if request.node.rep_call.failed:
        driver.save_screenshot(f"screenshots/{request.node.name}.png")
```

### Injecting a session cookie to skip login UI

From section 13 — log in once, save the cookie, inject it in subsequent tests to avoid repeating the login flow:

```python
driver.get("https://your-app.com")
driver.add_cookie({"name": "session", "value": YOUR_SESSION_TOKEN})
driver.refresh()  # cookie takes effect on next load
```

### Handling slow or dynamic pages

The explicit wait pattern from section 5 is the right tool for AJAX-heavy pages:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located((By.ID, "results")))
```

Common `expected_conditions` for QA work:
- `visibility_of_element_located` — element is rendered and non-zero size
- `element_to_be_clickable` — visible and enabled (use before clicking buttons)
- `invisibility_of_element_located` — spinner / loader has disappeared
- `text_to_be_present_in_element` — poll until element text matches
- `number_of_windows_to_be` — new tab/window has opened

---

## Screenshots output

Screenshots from section 12 are saved to `screenshots/` in the project root (created automatically on first run).
