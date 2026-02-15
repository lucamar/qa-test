import uuid
import pytest
from playwright.sync_api import expect
from pages.register_page import RegisterPage

# Base payload used as a starting point for tests; we will customize per-case.
BASE_VALID_PAYLOAD = {
    "first_name": "Hans",
    "last_name": "Muster",
    "email": "hans.muster@example.com",
    "phone": "+385 91 1234567",
    "address": "Ulica Test",
    "city": "Testgrad",
    "zip": "12345",
    "password": "P@ssw0rd123",
    "confirm_password": "P@ssw0rd123",
}


def _random_email():
    """Return a random email address to avoid collisions with existing users."""
    return f"{uuid.uuid4().hex[:8]}@example.invalid"


def _has_duplicate_message(text: str) -> bool:
    """Heuristic: return True if text likely signals a duplicate-user/email error."""
    if not text:
        return False
    t = text.lower()
    return ("already" in t and "exist" in t) or ("user already" in t) or ("email already" in t)

# TC10: Successful registration with valid fields
def test_TC10_successful_registration_shows_success_message_or_navigation(register_page: RegisterPage):
    """
    Happy-path: fill the form with a unique email and valid data, check for success.
    We accept either navigation away from the register page or a non-empty #registerMessage.
    """
    rp = register_page
    rp.goto()

    payload = BASE_VALID_PAYLOAD.copy()
    payload["email"] = _random_email()

    rp.fill_form(payload)
    rp.check_terms()

    # Try navigation first, otherwise wait for message
    nav = rp.submit(timeout=3000)
    if not nav:
        # No navigation: expect registerMessage to be populated by app.js
        msg = rp.wait_for_message_non_empty(timeout=5000)
        assert msg, "Expected a non-empty success message in #registerMessage after successful registration"

# TC11: Missing required fields are reported
def test_TC11_missing_required_fields_are_reported(register_page: RegisterPage):
    """
    For each required field in the form, clear it and submit. Expect browser validationMessage
    on that element OR an app-provided error (span or #registerMessage) mentioning required/missing.
    """
    rp = register_page

    # Discover required fields from the page object (RegisterPage.required_fields)
    required_field_keys = sorted(list(rp.required_fields))

    for key in required_field_keys:
        rp.goto()

        # Fill everything valid first
        payload = BASE_VALID_PAYLOAD.copy()
        # Use a fresh unique email for each iteration to avoid duplicate-email server-side errors
        payload["email"] = _random_email()
        rp.fill_form(payload)

        # Clear the single target required field to simulate missing input
        target = rp._one(key)
        target.fill("")  # clear the field
        # Trigger validators (input/blur) so client-side validation can run
        target.evaluate("el => { el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('blur', { bubbles: true })); }")
        rp.page.wait_for_timeout(150)

        # Ensure terms is checked so missing-terms does not interfere with required-field checks
        rp.check_terms()

        # Submit and collect signals
        rp.submit(timeout=1000)
        # 1) Check browser validation message for the specific element
        validation_msg = target.evaluate("el => el.validationMessage || ''") or ""
        if validation_msg and validation_msg.strip():
            # Browser reported a validation problem for this specific field — acceptable
            continue

        # 2) Otherwise, check app-provided signals: #registerMessage or any error spans
        reg_msg = rp._one("message").text_content() or ""
        reg_msg = reg_msg.strip().lower()

        # Collect known error span texts (defensive; these ids exist in the HTML)
        span_texts = []
        for span_id in ("emailError", "phoneError", "zipError", "passwordError", "confirmPasswordError"):
            h = rp.page.locator(f"#{span_id}")
            if h.count():
                span_texts.append((h.first.text_content() or "").strip().lower())

        combined = " ".join([reg_msg] + span_texts)

        # Accept either a message mentioning 'required' or the field name, or any non-empty app error
        if "required" in combined or key.replace("_", " ") in combined or any(s for s in span_texts if s):
            continue

        # If neither browser nor app reported anything specific, fail the specific case
        pytest.fail(
            f"Missing required field '{key}' did not produce a validation signal.\n"
            f"Field id: {target.get_attribute('id')}\n"
            f"Browser validationMessage: '{validation_msg}'\n"
            f"App registerMessage: '{reg_msg}'\n"
            f"Span texts: {span_texts}"
        )

# TC12 Duplicate email is detected and raises an error message
def test_TC12_duplicate_email_is_detected(register_page: RegisterPage):
    """
    Attempt to register twice with the same (unique) email:
      - first registration should succeed (navigation or non-empty success message)
      - second registration with the same email should be rejected with a duplicate-user/email error
        (heuristically looking for 'already exists' or similar in #registerMessage or error spans).
    """
    rp = register_page
    unique_email = _random_email()

    # First registration (should succeed)
    rp.goto()
    payload = BASE_VALID_PAYLOAD.copy()
    payload["email"] = unique_email
    rp.fill_form(payload)
    rp.check_terms()

    nav = rp.submit(timeout=3000)
    if not nav:
        # wait for success message
        try:
            _ = rp.wait_for_message_non_empty(timeout=5000)
        except Exception as e:
            pytest.fail(f"First registration did not report success (no navigation and no message). Exception: {e}")

    # Prepare to register again with the same email
    # Some apps may redirect after successful registration; navigate back to registration page to re-attempt
    rp.goto()
    payload2 = BASE_VALID_PAYLOAD.copy()
    payload2["email"] = unique_email
    rp.fill_form(payload2)
    rp.check_terms()
    rp.submit(timeout=1000)

    # Inspect #registerMessage and known error spans for duplicate indication
    reg_msg = rp._one("message").text_content() or ""
    reg_msg = reg_msg.strip()
    span_texts = []
    for span_id in ("emailError", "phoneError", "zipError", "passwordError", "confirmPasswordError"):
        h = rp.page.locator(f"#{span_id}")
        if h.count():
            span_texts.append((h.first.text_content() or "").strip())

    combined = " ".join([reg_msg] + span_texts).lower()

    assert _has_duplicate_message(reg_msg) or any(_has_duplicate_message(s) for s in span_texts) or ("already" in combined and "exist" in combined), (
        "Second registration with the same email did not produce a duplicate-user error. "
        f"#registerMessage: '{reg_msg}' | Spans: {span_texts}"
    )
