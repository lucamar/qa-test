from playwright.sync_api import Page
import pytest
from pages.register_page import RegisterPage

# Payload keys match RegisterPage.locators keys for inputs
VALID_PAYLOAD = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test.user+pw@example.com",
    "phone": "+15551234567",
    "address": "123 Test St",
    "city": "Testville",
    "zip": "12345",
    "password": "P@ssw0rd123",
    "confirm_password": "P@ssw0rd123",
}


def test_register_form_pom_flow(page: Page):
    """
    End-to-end happy-path test using the RegisterPage POM:
      - open page
      - assert fields and attributes
      - fill valid payload
      - check terms
      - verify browser-level validity
      - submit and assert success via message or navigation
    """
    rp = RegisterPage(page)
    rp.goto()

    # Structural and attribute assertions
    rp.assert_fields_present()

    # Fill form and check terms
    rp.fill_form(VALID_PAYLOAD)
    rp.check_terms()

    # Confirm password values match in the page before submit
    assert (
        page.locator("#password").input_value() == page.locator("#confirmPassword").input_value()
    ), "Password and Confirm Password should match in the test payload"

    # Browser-level validity
    assert rp.form_is_valid(), "Form is not valid according to browser validation (check required/format constraints)"

    # Submit: try navigation first, otherwise wait for #registerMessage to receive text
    nav = rp.submit(timeout=3000)
    if not nav:
        # wait for registerMessage to be populated by app.js (best-effort)
        msg = rp.wait_for_message_non_empty(timeout=5000)
        assert msg, "Expected a non-empty register message after submit"

    # If the app redirected we also accept that as success
    # No explicit assert needed here: either navigation occurred (nav truthy) or a message was found above.
