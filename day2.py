import time
import warnings
warnings.filterwarnings("ignore")

import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driver():
    """Create and configure a Chrome WebDriver instance."""
    chrome_options = Options()
    # Run in headed mode so the user can watch the automation
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

@pytest.fixture(autouse=True)
def reset_page(driver):
    """Reload the page before each test to ensure a clean state."""
    driver.get("https://vinothqaacademy.com/demo-site/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "registration-1"))
    )
    # Give the page's lazy-loading scripts a moment to stabilize the DOM
    time.sleep(0.5)

# ── Helpers ──────────────────────────────────────────────────────────────────

URL = "https://vinothqaacademy.com/demo-site/"

def _get_element(driver, by, value):
    """Robust element fetching handling dynamic DOM rerenders."""
    return WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    )

def _get_elements(driver, by, value):
    return WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((by, value))
    )

def _clear_and_type(element, text):
    """Clear any existing value and type new text."""
    element.clear()
    element.send_keys(text)


# ── Test Classes ─────────────────────────────────────────────────────────────

class TestPageLoad:
    """Verify the page loads correctly and the form is visible."""

    def test_page_title_contains_registration(self, driver):
        assert "Registration Form" in driver.title or "Demo Site" in driver.title

    def test_form_is_displayed(self, driver):
        form = _get_element(driver, By.ID, "registration-1")
        assert form.is_displayed()

    def test_form_heading_text(self, driver):
        legend = _get_element(driver, 
            By.CSS_SELECTOR, "fieldset.registration-form .vfb-legend h3"
        )
        assert legend.text.strip() == "Registration Form"


# ─────────────────────────────────────────────────────────────────────────────
#  TEXT INPUTS
# ─────────────────────────────────────────────────────────────────────────────

class TestFirstName:
    """Tests for the First Name text input (id=vfb-5)."""

    def test_first_name_field_present(self, driver):
        field = _get_element(driver, By.ID, "vfb-5")
        assert field.is_displayed()

    def test_first_name_field_type(self, driver):
        field = _get_element(driver, By.ID, "vfb-5")
        assert field.get_attribute("type") == "text"

    def test_first_name_accepts_text(self, driver):
        field = _get_element(driver, By.ID, "vfb-5")
        _clear_and_type(field, "Vinoth")
        assert field.get_attribute("value") == "Vinoth"

    def test_first_name_label_text(self, driver):
        label = _get_element(driver, By.CSS_SELECTOR, 'label[for="vfb-5"]')
        assert "First Name" in label.text


class TestLastName:
    """Tests for the Last Name text input (id=vfb-7)."""

    def test_last_name_field_present(self, driver):
        field = _get_element(driver, By.ID, "vfb-7")
        assert field.is_displayed()

    def test_last_name_accepts_text(self, driver):
        field = _get_element(driver, By.ID, "vfb-7")
        _clear_and_type(field, "Kumar")
        assert field.get_attribute("value") == "Kumar"


# ─────────────────────────────────────────────────────────────────────────────
#  RADIO BUTTONS — Gender
# ─────────────────────────────────────────────────────────────────────────────

class TestGenderRadioButtons:
    """Tests for the Gender radio button group (name=vfb-31)."""

    def test_gender_radio_buttons_present(self, driver):
        radios = _get_elements(driver, By.CSS_SELECTOR, 'input[name="vfb-31"]')
        assert len(radios) == 3

    def test_select_female(self, driver):
        female = _get_element(driver, By.ID, "vfb-31-2")
        female.click()
        assert female.is_selected()
        male = _get_element(driver, By.ID, "vfb-31-1")
        assert not male.is_selected()


# ─────────────────────────────────────────────────────────────────────────────
#  CHECKBOXES — Course Interested
# ─────────────────────────────────────────────────────────────────────────────

class TestCourseCheckboxes:
    """Tests for the 'Course Interested' checkbox group (name=vfb-20[])."""

    def test_devops_pre_checked(self, driver):
        """DevOps should be checked by default."""
        devops = _get_element(driver, By.ID, "vfb-20-3")
        assert devops.is_selected()

    def test_multiple_checkboxes_selectable(self, driver):
        ids = ["vfb-20-0", "vfb-20-1"]
        for cb_id in ids:
            cb = _get_element(driver, By.ID, cb_id)
            if not cb.is_selected():
                cb.click()
        for cb_id in ids:
            assert _get_element(driver, By.ID, cb_id).is_selected()


# ─────────────────────────────────────────────────────────────────────────────
#  ADDRESS FIELDS
# ─────────────────────────────────────────────────────────────────────────────

class TestAddressFields:
    """Tests for the composite Address field group (id prefix vfb-13)."""

    def test_address_fields_accept_text(self, driver):
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-address"), "123 Main Street")
        assert _get_element(driver, By.ID, "vfb-13-address").get_attribute("value") == "123 Main Street"
        
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-city"), "London")
        assert _get_element(driver, By.ID, "vfb-13-city").get_attribute("value") == "London"

    def test_country_select(self, driver):
        select = Select(_get_element(driver, By.ID, "vfb-13-country"))
        select.select_by_visible_text("United Kingdom")
        assert select.first_selected_option.text == "United Kingdom"


# ─────────────────────────────────────────────────────────────────────────────
#  EMAIL INPUT
# ─────────────────────────────────────────────────────────────────────────────

class TestEmailField:
    """Tests for the Email input (id=vfb-14, type=email)."""

    def test_email_accepts_valid_email(self, driver):
        field = _get_element(driver, By.ID, "vfb-14")
        _clear_and_type(field, "test@example.com")
        assert field.get_attribute("value") == "test@example.com"


# ─────────────────────────────────────────────────────────────────────────────
#  DATE FIELD
# ─────────────────────────────────────────────────────────────────────────────

class TestDateField:
    """Tests for the 'Date of Demo' field (id=vfb-18)."""

    def test_date_field_accepts_date_text(self, driver):
        field = _get_element(driver, By.ID, "vfb-18")
        _clear_and_type(field, "12/25/26")
        assert field.get_attribute("value") == "12/25/26"


# ─────────────────────────────────────────────────────────────────────────────
#  TIME DROPDOWNS — Convenient Time
# ─────────────────────────────────────────────────────────────────────────────

class TestTimeDropdowns:
    """Tests for the 'Convenient Time' hour/minute selects."""

    def test_time_select(self, driver):
        hour_select = Select(_get_element(driver, By.ID, "vfb-16-hour"))
        hour_select.select_by_value("10")
        assert hour_select.first_selected_option.text == "10"
        
        min_select = Select(_get_element(driver, By.ID, "vfb-16-min"))
        min_select.select_by_value("30")
        assert min_select.first_selected_option.text == "30"


# ─────────────────────────────────────────────────────────────────────────────
#  NUMBER INPUT — Mobile Number
# ─────────────────────────────────────────────────────────────────────────────

class TestMobileNumber:
    """Tests for the Mobile Number field (id=vfb-19)."""

    def test_mobile_accepts_numbers(self, driver):
        field = _get_element(driver, By.ID, "vfb-19")
        _clear_and_type(field, "9876543210")
        assert field.get_attribute("value") == "9876543210"


# ─────────────────────────────────────────────────────────────────────────────
#  TEXTAREA — Enter your query
# ─────────────────────────────────────────────────────────────────────────────

class TestQueryTextarea:
    """Tests for the 'Enter your query' textarea (id=vfb-23)."""

    def test_textarea_accepts_multiline_text(self, driver):
        field = _get_element(driver, By.ID, "vfb-23")
        multiline = "Line 1\nLine 2"
        _clear_and_type(field, multiline)
        assert "Line 1" in field.get_attribute("value")


# ─────────────────────────────────────────────────────────────────────────────
#  VERIFICATION SECTION
# ─────────────────────────────────────────────────────────────────────────────

class TestVerificationSection:
    """Tests for the Verification fieldset and secret field."""

    def test_secret_field_accepts_digits(self, driver):
        field = _get_element(driver, By.ID, "vfb-3")
        _clear_and_type(field, "33")
        assert field.get_attribute("value") == "33"


# ─────────────────────────────────────────────────────────────────────────────
#  SUBMIT BUTTON
# ─────────────────────────────────────────────────────────────────────────────

class TestSubmitButton:
    """Tests for the form Submit button."""

    def test_submit_button_is_clickable(self, driver):
        btn = _get_element(driver, By.ID, "vfb-4")
        assert btn.is_enabled()


# ─────────────────────────────────────────────────────────────────────────────
#  END-TO-END FORM FILL
# ─────────────────────────────────────────────────────────────────────────────

class TestEndToEndFormFill:
    """
    End-to-end test: fill every input field with valid data.
    """

    def test_fill_all_fields(self, driver):

        _clear_and_type(_get_element(driver, By.ID, "vfb-5"), "Vinoth")
        _clear_and_type(_get_element(driver, By.ID, "vfb-7"), "Kumar")
        
        _get_element(driver, By.ID, "vfb-31-1").click()

        selenium_cb = _get_element(driver, By.ID, "vfb-20-0")
        if not selenium_cb.is_selected():
            selenium_cb.click()
        
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-address"), "10 Downing St")
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-city"), "London")
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-state"), "England")
        _clear_and_type(_get_element(driver, By.ID, "vfb-13-zip"), "SW1A 2AA")

        Select(_get_element(driver, By.ID, "vfb-13-country")).select_by_visible_text("United Kingdom")
        _clear_and_type(_get_element(driver, By.ID, "vfb-14"), "vinoth@example.com")
        _clear_and_type(_get_element(driver, By.ID, "vfb-18"), "01/15/27")

        _get_element(driver, By.CSS_SELECTOR, "fieldset.registration-form .vfb-legend h3").click()
        time.sleep(0.3)

        Select(_get_element(driver, By.ID, "vfb-16-hour")).select_by_value("10")
        Select(_get_element(driver, By.ID, "vfb-16-min")).select_by_value("30")
        
        _clear_and_type(_get_element(driver, By.ID, "vfb-19"), "9876543210")
        _clear_and_type(_get_element(driver, By.ID, "vfb-23"), "I am interested in Selenium WebDriver training.")
        _clear_and_type(_get_element(driver, By.ID, "vfb-3"), "33")

        assert _get_element(driver, By.ID, "vfb-4").is_enabled()


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])