import re
import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage

# Example invalid payloads
INVALID_PAYLOADS = {
    "invalid_email": {
        "first_name": "Test",
        "last_name": "User",
        "email": "not-an-email",
        "phone": "+15551234567",
        "address": "123 Test St",
        "city": "Testville",
        "zip": "12345",
        "password": "P@ssw0rd123",
        "confirm_password": "P@ssw0rd123",
    },
    "password_mismatch": {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone": "+15551234567",
        "address": "123 Test St",
        "city": "Testville",
        "zip": "12345",
        "password": "P@ssw0rd123",
        "confirm_password": "Different1!",
    },
}

ERROR_SPAN_IDS = [
    "emailError",
    "phoneError",
    "zipError",
    "passwordError",
    "confirmPasswordError",
]


def _submit_and_collect_errors(rp: RegisterPage):
    """
    Click Create Account and collect several possible error signals:
      - browser validation messages (validationMessage) for form controls
      - error span texts (ids listed in ERROR_SPAN_IDS)
      - registerMessage (#registerMessage) text
    Returns a dict with keys: validation_messages (list), span_errors (dict), register_message (str)
    """
    page = rp.page
    # Attempt submit (try navigation, but ignore if no navigation occurs)
    rp.submit(timeout=1000)

    # Collect browser validation messages from form elements
    validation_messages = page.evaluate(
        """() => {
            const form = document.querySelector('#registerForm');
            if (!form) return [];
            return Array.from(form.elements)
                .filter(el => typeof el.validationMessage === 'string')
                .map(el => ({name: el.name || el.id || '', message: el.validationMessage || ''}))
                .filter(x => x.message && x.message.trim().length > 0);
        }"""
    )

    # Collect error span texts
    span_errors = {}
    for span_id in ERROR_SPAN_IDS:
        handle = page.locator(f"#{span_id}")
        if handle.count() > 0:
            txt = (handle.first.text_content() or "").strip()
            span_errors[span_id] = txt

    # Collect registerMessage
    reg_msg_handle = page.locator("#registerMessage")
    reg_msg = ""
    if reg_msg_handle.count() > 0:
        reg_msg = (reg_msg_handle.first.text_content() or "").strip()

    return {
        "validation_messages": validation_messages,
        "span_errors": span_errors,
        "register_message": reg_msg,
    }


def _has_any_error(signals: dict) -> bool:
    if signals["validation_messages"]:
        return True
    if any(v for v in signals["span_errors"].values()):
        return True
    if signals["register_message"]:
        return True
    return False


def test_submitting_empty_form_shows_validation(register_page: RegisterPage):
    """
    Submit the form without filling required fields.
    Expect browser validation messages OR app-provided error messages to appear.
    """
    rp = register_page
    rp.goto()

    # Ensure form is visible and empty
    expect(rp.form).to_be_visible()

    signals = _submit_and_collect_errors(rp)

    assert _has_any_error(signals), (
        "Submitting an empty required form should produce browser validation messages "
        "or app-provided error messages, but none were detected. "
        f"Signals: {signals}"
    )


@pytest.mark.parametrize("case", ["invalid_email", "password_mismatch"])
def test_invalid_payloads_trigger_validation(register_page: RegisterPage, case: str):
    """
    Test two negative scenarios:
      - invalid email (app may provide email-specific error span)
      - password mismatch (app may provide confirmPasswordError)
    We assert that either a specific related span receives text, or a registerMessage mentions the issue,
    or browser validation reports an invalid control.
    """
    rp = register_page
    rp.goto()

    payload = INVALID_PAYLOADS[case]
    # Fill form with payload
    rp.fill_form(payload)
    # Ensure terms are checked only when testing non-terms scenarios
    rp.check_terms()

    signals = _submit_and_collect_errors(rp)

    # Determine expectations per case
    if case == "invalid_email":
        email_span = signals["span_errors"].get("emailError", "")
        reg_msg = signals["register_message"].lower()
        browser_msgs = signals["validation_messages"]
        # Accept any of these: emailError populated, register message mentions email, OR browser validation message for email
        email_browser_invalid = any("email" in (vm["name"] or "").lower() or "email" in (vm["message"] or "").lower() for vm in browser_msgs)
        assert email_span or ("email" in reg_msg) or email_browser_invalid, (
            "Invalid email should cause an email-related error. "
            f"Signals: {signals}"
        )
    elif case == "password_mismatch":
        confirm_span = signals["span_errors"].get("confirmPasswordError", "")
        reg_msg = signals["register_message"].lower()
        browser_msgs = signals["validation_messages"]
        # Accept either confirmPasswordError populated, registerMessage mentioning mismatch/password, or browser validation (unlikely here)
        mismatch_browser_invalid = any("password" in (vm["name"] or "").lower() or "password" in (vm["message"] or "").lower() for vm in browser_msgs)
        assert confirm_span or ("password" in reg_msg) or mismatch_browser_invalid, (
            "Password mismatch should produce an error on confirm password or a register message. "
            f"Signals: {signals}"
        )


def test_terms_must_be_checked(register_page: RegisterPage):
    """
    Fill the form but leave the 'terms' checkbox unchecked; submit and expect the app to block submission
    and show an error mentioning 'terms' or similar. Browser validation won't catch this because checkbox is not required in HTML,
    so we expect application-level handling that populates #registerMessage or other span.
    """
    rp = register_page
    rp.goto()

    # Fill with a valid payload but do NOT check terms
    rp.fill_form({
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone": "+15551234567",
        "address": "123 St",
        "city": "Testville",
        "zip": "12345",
        "password": "P@ssw0rd123",
        "confirm_password": "P@ssw0rd123",
    })
    # Explicitly ensure terms is unchecked
    terms = rp._one("terms")
    if terms.is_checked():
        terms.uncheck()

    signals = _submit_and_collect_errors(rp)

    reg_msg = signals["register_message"].lower()
    # Check for presence of any indicator mentioning terms/agree, or general non-empty message
    assert (
        ("term" in reg_msg) or ("agree" in reg_msg) or signals["span_errors"].get("passwordError") or _has_any_error(signals)
    ), (
        "Submitting without agreeing to terms should produce an application-level error mentioning terms/agree or a non-empty register message. "
        f"Signals: {signals}"
    )
