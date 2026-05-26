"""
Selenium Practice — comprehensive showcase of Selenium WebDriver in Python.

Target site: https://the-internet.herokuapp.com
Purpose-built for automation practice — every page isolates one feature.

Run the full demo:
    python selenium_practice.py

Or call individual section functions directly in a REPL / notebook.

Sections (in order):
    1.  Driver setup
    2.  Navigation + browser info
    3.  Locator strategies (all 8)
    4.  Element interactions
    5.  Waits — implicit vs. explicit
    6.  Select dropdowns
    7.  Alerts (alert / confirm / prompt)
    8.  Frames and iframes
    9.  Multiple windows and tabs
    10. ActionChains (hover, double-click, right-click, drag-and-drop)
    11. JavaScript execution
    12. Screenshots
    13. Cookies
    14. Page Object Model (delegates to pages/login_page.py)
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://the-internet.herokuapp.com"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


# ============================================================
# 1. DRIVER SETUP
# ============================================================

def create_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Build a Chrome WebDriver using webdriver-manager.

    webdriver-manager downloads the correct ChromeDriver version automatically,
    so we never need to manually match ChromeDriver to our Chrome installation.

    headless=True runs Chrome without a visible window — useful in CI pipelines
    where there's no display. Set to False while learning to see what happens.
    """
    options = webdriver.ChromeOptions()

    if headless:
        # --headless=new is Chrome's modern headless mode (replaces the old flag).
        options.add_argument("--headless=new")

    # These flags prevent common failures when running inside Docker or CI:
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Suppress the "Chrome is being controlled by automated test software" bar.
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # A sensible default viewport so pages render consistently.
    driver.set_window_size(1280, 800)

    return driver


# ============================================================
# 2. NAVIGATION + BROWSER INFO
# ============================================================

def demo_navigation(driver: webdriver.Chrome):
    """
    Covers: get(), title, current_url, back(), forward(), refresh().
    """
    print("\n=== 2. NAVIGATION ===")

    driver.get(BASE_URL)
    print(f"Title    : {driver.title}")
    print(f"URL      : {driver.current_url}")

    # Navigate to a sub-page.
    driver.get(f"{BASE_URL}/login")
    print(f"After get: {driver.current_url}")

    # Browser history navigation — same as clicking the browser arrows.
    driver.back()
    print(f"After back  : {driver.current_url}")

    driver.forward()
    print(f"After forward: {driver.current_url}")

    # Reload the page (equivalent to F5).
    driver.refresh()
    print(f"After refresh: {driver.current_url}")


# ============================================================
# 3. LOCATOR STRATEGIES
# ============================================================

def demo_locators(driver: webdriver.Chrome):
    """
    Selenium provides 8 strategies to find elements. Choosing the right one:

    • By.ID           — fastest; use when the element has a unique id.
    • By.NAME         — for form inputs that have a name attribute.
    • By.CLASS_NAME   — when the class is unique; fragile when multiple classes.
    • By.CSS_SELECTOR — flexible and fast; prefer over XPath for most cases.
    • By.XPATH        — powerful but verbose; use when CSS can't express it
                        (e.g., "find parent of element with text X").
    • By.LINK_TEXT    — exact match on anchor text; brittle if text changes.
    • By.PARTIAL_LINK_TEXT — partial match; slightly more resilient.
    • By.TAG_NAME     — rarely used alone; fine for grabbing all <a> or <input>.
    """
    print("\n=== 3. LOCATOR STRATEGIES ===")

    driver.get(f"{BASE_URL}/login")

    # By.ID — the element has id="username"
    username_by_id = driver.find_element(By.ID, "username")
    print(f"By.ID          : found '{username_by_id.get_attribute('id')}'")

    # By.NAME — the input has name="username"
    username_by_name = driver.find_element(By.NAME, "username")
    print(f"By.NAME        : found '{username_by_name.get_attribute('name')}'")

    # By.CLASS_NAME — finds by a single CSS class name.
    # Limitation: CLASS_NAME cannot handle compound class strings like "radius large".
    # For compound classes use CSS_SELECTOR: "button.radius.large"
    # The submit button on this page has class "radius" (among others).
    submit_btn = driver.find_element(By.CLASS_NAME, "radius")
    print(f"By.CLASS_NAME  : tag='{submit_btn.tag_name}', text='{submit_btn.text.strip()}'")

    # By.CSS_SELECTOR — most expressive; combine tag, id, class, attributes
    password_by_css = driver.find_element(By.CSS_SELECTOR, "input#password")
    print(f"By.CSS_SELECTOR: id='{password_by_css.get_attribute('id')}'")

    # By.XPATH — here we select the button by its text content
    # XPath is the only strategy that can traverse upward in the DOM.
    button_by_xpath = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    print(f"By.XPATH       : text='{button_by_xpath.text}'")

    # By.LINK_TEXT — navigate to a page with links first
    driver.get(BASE_URL)
    link = driver.find_element(By.LINK_TEXT, "Form Authentication")
    print(f"By.LINK_TEXT       : href='{link.get_attribute('href')}'")

    # By.PARTIAL_LINK_TEXT — match a substring of the anchor text
    partial = driver.find_element(By.PARTIAL_LINK_TEXT, "Form Auth")
    print(f"By.PARTIAL_LINK_TEXT: text='{partial.text}'")

    # By.TAG_NAME — grab all links on the page
    all_links = driver.find_elements(By.TAG_NAME, "a")  # plural → list
    print(f"By.TAG_NAME    : found {len(all_links)} <a> elements on the page")


# ============================================================
# 4. ELEMENT INTERACTIONS
# ============================================================

def demo_element_interactions(driver: webdriver.Chrome):
    """
    Common actions on WebElement objects:

    • send_keys()     — types into an input (or sends keyboard shortcuts)
    • clear()         — clears the current value of an input
    • click()         — clicks the element
    • text            — visible text between the element's tags
    • get_attribute() — reads any HTML attribute or property
    • is_displayed()  — True if the element is visible on screen
    • is_enabled()    — True if the element is not disabled
    • is_selected()   — True if a checkbox/radio is checked
    """
    print("\n=== 4. ELEMENT INTERACTIONS ===")

    driver.get(f"{BASE_URL}/login")

    username_input = driver.find_element(By.ID, "username")

    username_input.send_keys("tomsmith")
    print(f"Typed value    : '{username_input.get_attribute('value')}'")

    username_input.clear()
    print(f"After clear    : '{username_input.get_attribute('value')}'")

    username_input.send_keys("tomsmith")
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")

    # send_keys(Keys.RETURN) submits the form without clicking the button —
    # useful for testing keyboard accessibility.
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

    flash = driver.find_element(By.ID, "flash")
    print(f"Flash text     : '{flash.text.strip()}'")
    print(f"is_displayed() : {flash.is_displayed()}")
    print(f"Tag name       : {flash.tag_name}")

    # Checkboxes — navigate to a page with them
    driver.get(f"{BASE_URL}/checkboxes")
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    for i, cb in enumerate(checkboxes):
        print(f"Checkbox {i}: is_selected={cb.is_selected()}, is_enabled={cb.is_enabled()}")
    # Toggle the first checkbox
    checkboxes[0].click()
    print(f"Checkbox 0 after click: is_selected={checkboxes[0].is_selected()}")


# ============================================================
# 5. WAITS
# ============================================================

def demo_waits(driver: webdriver.Chrome):
    """
    WHY waits matter:
    Modern pages load content dynamically (AJAX, React, etc.).  Without waits,
    find_element() throws NoSuchElementException before the element appears.

    IMPLICIT wait — set once, applied globally to every find_element call.
        driver.implicitly_wait(10)
        Pitfall: it masks slow pages instead of failing fast; it stacks badly
        with explicit waits and can cause 2× timeouts.

    EXPLICIT wait — precise, per-element wait with a specific condition.
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(...))
        Prefer this: it fails fast when the condition can never be met,
        and the condition name documents *why* we wait.

    FLUENT wait — explicit wait with configurable polling interval and
        ignored exceptions. Used for flaky external services or animations.
    """
    print("\n=== 5. WAITS ===")

    # -- Implicit wait (shown for completeness; avoid mixing with explicit) --
    driver.implicitly_wait(5)
    driver.get(f"{BASE_URL}/dynamic_loading/1")
    # This page hides an element; clicking Start makes it appear after a delay.
    driver.find_element(By.CSS_SELECTOR, "#start button").click()

    # -- Explicit wait: wait until the hidden element is visible --
    # EC.visibility_of_element_located checks that the element exists AND has
    # non-zero width/height (i.e., CSS display is not 'none').
    wait = WebDriverWait(driver, 15)
    finish_text = wait.until(
        EC.visibility_of_element_located((By.ID, "finish"))
    )
    print(f"Explicit wait resolved: '{finish_text.text}'")

    # -- Waiting for element to disappear --
    driver.get(f"{BASE_URL}/dynamic_loading/2")
    driver.find_element(By.CSS_SELECTOR, "#start button").click()
    # Wait for the loading spinner to become invisible
    wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
    result = driver.find_element(By.ID, "finish")
    print(f"Spinner gone, result: '{result.text}'")

    # Reset implicit wait so it doesn't interfere with the rest of the demo.
    driver.implicitly_wait(0)


# ============================================================
# 6. SELECT DROPDOWNS
# ============================================================

def demo_select_dropdown(driver: webdriver.Chrome):
    """
    The Select class wraps a <select> element and provides three ways to
    choose an option — by visible text, by value attribute, or by index.

    select_by_visible_text() is the most readable; use value or index
    when the text is dynamically generated or localised.
    """
    print("\n=== 6. SELECT DROPDOWNS ===")

    driver.get(f"{BASE_URL}/dropdown")
    dropdown_element = driver.find_element(By.ID, "dropdown")
    dropdown = Select(dropdown_element)

    print(f"Options: {[o.text for o in dropdown.options]}")

    # Three equivalent ways to select "Option 1":
    dropdown.select_by_visible_text("Option 1")
    print(f"Selected by text  : '{dropdown.first_selected_option.text}'")

    dropdown.select_by_value("2")
    print(f"Selected by value : '{dropdown.first_selected_option.text}'")

    dropdown.select_by_index(1)
    print(f"Selected by index : '{dropdown.first_selected_option.text}'")


# ============================================================
# 7. ALERTS
# ============================================================

def demo_alerts(driver: webdriver.Chrome):
    """
    JavaScript dialogs (alert, confirm, prompt) pause script execution.
    Selenium represents the active dialog as driver.switch_to.alert.

    • alert   — informational, only "OK" button. Call accept().
    • confirm — "OK" or "Cancel". accept() → OK, dismiss() → Cancel.
    • prompt  — text input + OK/Cancel. send_keys() to type, accept() to confirm.
    """
    print("\n=== 7. ALERTS ===")

    driver.get(f"{BASE_URL}/javascript_alerts")

    # -- Alert --
    driver.find_element(By.XPATH, "//button[text()='Click for JS Alert']").click()
    alert = driver.switch_to.alert
    print(f"Alert text  : '{alert.text}'")
    alert.accept()
    result = driver.find_element(By.ID, "result")
    print(f"Result      : '{result.text}'")

    # -- Confirm (accept) --
    driver.find_element(By.XPATH, "//button[text()='Click for JS Confirm']").click()
    confirm = driver.switch_to.alert
    print(f"Confirm text: '{confirm.text}'")
    confirm.accept()
    print(f"Result      : '{driver.find_element(By.ID, 'result').text}'")

    # -- Confirm (dismiss) --
    driver.find_element(By.XPATH, "//button[text()='Click for JS Confirm']").click()
    driver.switch_to.alert.dismiss()
    print(f"After dismiss: '{driver.find_element(By.ID, 'result').text}'")

    # -- Prompt --
    driver.find_element(By.XPATH, "//button[text()='Click for JS Prompt']").click()
    prompt = driver.switch_to.alert
    prompt.send_keys("Hello Selenium!")
    prompt.accept()
    print(f"Prompt result: '{driver.find_element(By.ID, 'result').text}'")


# ============================================================
# 8. FRAMES AND IFRAMES
# ============================================================

def demo_frames(driver: webdriver.Chrome):
    """
    An iframe embeds a separate HTML document inside the page.
    Elements inside it are invisible to the main document's find_element —
    we must explicitly switch context before interacting with them.

    switch_to.frame() accepts: the iframe element, its name, or its index.
    switch_to.default_content() returns to the top-level document.
    switch_to.parent_frame() moves up one level (useful for nested iframes).
    """
    print("\n=== 8. FRAMES AND IFRAMES ===")

    driver.get(f"{BASE_URL}/iframe")

    # The page contains a TinyMCE editor inside an iframe.
    # Attempting find_element before switching raises NoSuchElementException.

    # Switch by element reference — more robust than switching by index
    iframe_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe_element)

    # Now we're inside the iframe context and can find its elements.
    body = driver.find_element(By.ID, "tinymce")
    print(f"Inside iframe body text: '{body.text}'")
    body.clear()
    body.send_keys("Typed inside an iframe!")
    print(f"After typing           : '{body.text}'")

    # Return to the top-level document before interacting with the main page.
    driver.switch_to.default_content()
    print("Switched back to main document.")


# ============================================================
# 9. MULTIPLE WINDOWS AND TABS
# ============================================================

def demo_multiple_windows(driver: webdriver.Chrome):
    """
    Some actions (target="_blank" links, window.open() calls) open new windows
    or tabs. Selenium tracks them all via window handles — unique strings
    assigned to each window.

    driver.window_handles — list of all open window handles
    driver.current_window_handle — the handle of the focused window
    driver.switch_to.window(handle) — move focus to that window
    """
    print("\n=== 9. MULTIPLE WINDOWS ===")

    driver.get(f"{BASE_URL}/windows")
    original_handle = driver.current_window_handle
    print(f"Windows before click: {len(driver.window_handles)}")

    driver.find_element(By.LINK_TEXT, "Click Here").click()

    # Wait for the new window to open — window_handles length increases.
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    new_handles = [h for h in driver.window_handles if h != original_handle]
    new_handle = new_handles[0]

    driver.switch_to.window(new_handle)
    print(f"New window title: '{driver.title}'")
    print(f"New window URL  : '{driver.current_url}'")

    driver.close()  # closes the current (new) window only
    driver.switch_to.window(original_handle)
    print(f"Back to original, title: '{driver.title}'")


# ============================================================
# 10. ACTION CHAINS
# ============================================================

def demo_action_chains(driver: webdriver.Chrome):
    """
    ActionChains builds up a sequence of low-level interactions (mouse moves,
    key presses) and dispatches them all at once with .perform().

    This is the only reliable way to test:
    • Hover menus (element only appears on mouseover)
    • Right-click context menus
    • Double-click actions
    • Drag-and-drop between elements
    """
    print("\n=== 10. ACTION CHAINS ===")

    # -- Hover --
    driver.get(f"{BASE_URL}/hovers")
    figures = driver.find_elements(By.CLASS_NAME, "figure")
    actions = ActionChains(driver)

    # Hover over the first figure; a caption div appears.
    actions.move_to_element(figures[0]).perform()
    caption = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".figure:first-child .figcaption"))
    )
    print(f"Hover caption: '{caption.text.strip()}'")

    # -- Double-click --
    driver.get(f"{BASE_URL}/")
    # (no double-click demo on this site without JS; shown as pattern)
    # actions.double_click(element).perform()
    print("Double-click pattern: ActionChains(driver).double_click(element).perform()")

    # -- Right-click (context click) --
    # actions.context_click(element).perform()
    print("Right-click pattern : ActionChains(driver).context_click(element).perform()")

    # -- Drag and Drop --
    driver.get(f"{BASE_URL}/drag_and_drop")
    source = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "column-a"))
    )
    target = driver.find_element(By.ID, "column-b")

    header_before = source.find_element(By.TAG_NAME, "header").text
    print(f"Column A before drag: '{header_before}'")

    ActionChains(driver).drag_and_drop(source, target).perform()
    # The site's drag-and-drop uses HTML5 events which some browsers handle
    # differently. If the header text doesn't swap, see the JS workaround in
    # demo_javascript_execution() below.
    time.sleep(0.5)
    header_after = driver.find_element(By.ID, "column-a").find_element(By.TAG_NAME, "header").text
    print(f"Column A after  drag: '{header_after}'")


# ============================================================
# 11. JAVASCRIPT EXECUTION
# ============================================================

def demo_javascript_execution(driver: webdriver.Chrome):
    """
    execute_script() injects and runs arbitrary JavaScript in the page context.
    Use it when:
    • An element is off-screen and you need to scroll it into view.
    • Native Selenium actions fail (e.g., HTML5 drag-and-drop events).
    • You need to read/write DOM properties not exposed by WebElement.
    • You want to click a hidden element (use sparingly — bypasses real UX).

    execute_async_script() is the async variant for Promise-based JS.
    """
    print("\n=== 11. JAVASCRIPT EXECUTION ===")

    driver.get(f"{BASE_URL}/login")

    # Scroll the page to the bottom.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Scrolled to page bottom via JS.")

    # Read a DOM property not exposed by WebElement API.
    username_input = driver.find_element(By.ID, "username")
    placeholder = driver.execute_script(
        "return arguments[0].getAttribute('placeholder');", username_input
    )
    print(f"Placeholder via JS: '{placeholder}'")

    # Highlight an element by changing its border (useful for debugging).
    driver.execute_script(
        "arguments[0].style.border = '3px solid red';", username_input
    )
    print("Highlighted username input with JS (red border).")

    # Return a value from JS — execute_script returns the expression's value.
    page_title = driver.execute_script("return document.title;")
    print(f"document.title via JS: '{page_title}'")

    # Scroll an element into view before interacting with it.
    driver.execute_script("arguments[0].scrollIntoView(true);", username_input)
    print("Scrolled element into view via JS.")


# ============================================================
# 12. SCREENSHOTS
# ============================================================

def demo_screenshots(driver: webdriver.Chrome):
    """
    Screenshots are indispensable for debugging CI failures.
    Best practice: take a screenshot in your test teardown whenever a test fails.

    save_screenshot()          — saves the full page viewport as PNG.
    get_screenshot_as_base64() — base64 string (embed in HTML reports).
    element.screenshot()       — saves just the element's bounding box.
    """
    print("\n=== 12. SCREENSHOTS ===")

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    driver.get(f"{BASE_URL}/login")

    # Full page screenshot
    full_path = os.path.join(SCREENSHOTS_DIR, "full_page.png")
    driver.save_screenshot(full_path)
    print(f"Full page screenshot saved to: {full_path}")

    # Element-level screenshot (only the login form card)
    form_element = driver.find_element(By.ID, "login")
    element_path = os.path.join(SCREENSHOTS_DIR, "login_form.png")
    form_element.screenshot(element_path)
    print(f"Element screenshot saved to  : {element_path}")


# ============================================================
# 13. COOKIES
# ============================================================

def demo_cookies(driver: webdriver.Chrome):
    """
    Selenium can read, add, modify, and delete browser cookies.

    Common use cases:
    • Inject a session cookie to skip the login UI in test setup.
    • Verify that a "remember me" flow correctly persists cookies.
    • Clean cookie state between tests with delete_all_cookies().
    """
    print("\n=== 13. COOKIES ===")

    driver.get(BASE_URL)

    # Read all cookies
    cookies = driver.get_cookies()
    print(f"Cookies before login: {[c['name'] for c in cookies]}")

    # Log in so the site sets a session cookie
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys("tomsmith")
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    cookies_after = driver.get_cookies()
    print(f"Cookies after login : {[c['name'] for c in cookies_after]}")

    # Read a specific cookie by name
    session_cookie = driver.get_cookie("rack.session")
    if session_cookie:
        print(f"Session cookie domain: '{session_cookie.get('domain')}'")

    # Add a custom cookie (must navigate to the domain first)
    driver.add_cookie({"name": "my_test_flag", "value": "enabled"})
    print(f"Added cookie value  : '{driver.get_cookie('my_test_flag')['value']}'")

    # Delete one cookie
    driver.delete_cookie("my_test_flag")
    print(f"After delete        : {driver.get_cookie('my_test_flag')}")

    # Delete all cookies (e.g., between test cases)
    driver.delete_all_cookies()
    print(f"After delete_all    : {driver.get_cookies()}")


# ============================================================
# 14. PAGE OBJECT MODEL (POM)
# ============================================================

def demo_page_object_model(driver: webdriver.Chrome):
    """
    POM separates page structure (locators + actions) from test logic.

    Benefits:
    • Locators live in one place — update once when the DOM changes.
    • Test code reads like requirements, not like HTML.
    • Pages are composable and reusable across multiple tests.

    See pages/base_page.py and pages/login_page.py for the implementation.
    """
    print("\n=== 14. PAGE OBJECT MODEL ===")

    # Import here to keep the section self-contained
    from pages.login_page import LoginPage

    page = LoginPage(driver)
    page.open_login_page()

    # Successful login
    page.login_as("tomsmith", "SuperSecretPassword!")
    print(f"Login successful: {page.is_login_successful()}")

    # Navigate back and try with wrong credentials
    page.open_login_page()
    page.login_as("tomsmith", "wrongpassword")
    print(f"Login failed    : {page.is_login_failed()}")


# ============================================================
# MAIN — run all sections in sequence
# ============================================================

def run_all():
    """
    Entry point for the full demo.

    Each section function receives the driver, runs its showcase,
    and prints what it did. The driver is quit in the finally block
    so it always closes, even if a section raises an exception.
    """
    print("Starting Selenium Practice Demo")
    print(f"Target site: {BASE_URL}")

    # Set headless=False to watch the browser; True for silent background run.
    driver = create_driver(headless=False)

    sections = [
        demo_navigation,
        demo_locators,
        demo_element_interactions,
        demo_waits,
        demo_select_dropdown,
        demo_alerts,
        demo_frames,
        demo_multiple_windows,
        demo_action_chains,
        demo_javascript_execution,
        demo_screenshots,
        demo_cookies,
        demo_page_object_model,
    ]

    try:
        for section in sections:
            try:
                section(driver)
            except Exception as e:
                # One broken section doesn't stop the rest — useful when the
                # practice site updates its HTML and a locator goes stale.
                print(f"\n[SKIPPED] {section.__name__} failed: {e}\n")

    finally:
        # Always quit the driver — leaves no zombie Chrome processes.
        driver.quit()
        print("\nDriver closed. Demo complete.")


if __name__ == "__main__":
    run_all()
