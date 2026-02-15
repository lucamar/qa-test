import re
import pytest
from playwright.sync_api import expect
from pages.register_page import RegisterPage

BASE_VALID_PAYLOAD = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test.user@example.com",
    "phone": "+15551234567",
    "address": "123 Test St",
    "city": "Testville",
    "zip": "12345",
    "password": "P@ssw0rd123",
    "confirm_password": "P@ssw0rd123",
}

ERROR_SPAN_IDS = [
    "emailError",
    "phoneError",
    "zipError",
    "passwordError",
    "confirmPasswordError",
]


def _trigger_input_and_blur(locator):
    locator.evaluate(
        """el => {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        }"""
    )


def _submit_and_collect_errors(rp: RegisterPage):
    page = rp.page
    rp.submit(timeout=1000)

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

    span_errors = {}
    for span_id in ERROR_SPAN_IDS:
        handle = page.locator(f"#{span_id}")
        span_errors[span_id] = (handle.first.text_content() or "").strip() if handle.count() > 0 else ""

    reg_msg_handle = page.locator("#registerMessage")
    reg_msg = (reg_msg_handle.first.text_content() or "").strip() if reg_msg_handle.count() > 0 else ""

    return {
        "validation_messages": validation_messages,
        "span_errors": span_errors,
        "register_message": reg_msg,
        "current_url": page.url,
    }


def _has_any_error(signals: dict) -> bool:
    if signals["validation_messages"]:
        return True
    if any(v for v in signals["span_errors"].values()):
        return True
    if signals["register_message"]:
        return True
    return False


@pytest.mark.parametrize(
    "field,invalid_value,expected_keywords",
    [
        # TC01: Invalid First Name format (only letters aA-zZ)
        ("first_name", "John123!", ["first", "name", "letters", "invalid"]),
        # TC02: Invalid Last Name format (only letters aA-zZ)
        ("last_name", "Doe99$", ["last", "name", "letters", "invalid"]),
        # TC03: Invalid email format (must contain @ and a domain)
        ("email", "user@invalid", ["@", "email", "domain", "invalid"]),
        # TC04: Invalid Phone Number (should contain a country code followed by digits)
        ("phone", "abcd-efg", ["phone", "country", "code", "+", "digits", "invalid"]),
        # TC05: Invalid ZIP Code (only 4 or 5 digits)
        ("zip", "12ab", ["zip", "postal", "code", "digit", "invalid"]),
    ],
)
def test_TC01_to_TC05_field_format_validations(register_page: RegisterPage, field: str, invalid_value: str, expected_keywords: list):
    """
    TC01 - TC05:
    Fill the form with one invalid field value (others valid), trigger input/blur events,
    submit, and require a validation signal that references the field/format.
    """
    rp = register_page
    rp.goto()

    payload = BASE_VALID_PAYLOAD.copy()
    payload[field] = invalid_value

    rp.fill_form(payload)

    target_loc = rp._one(field)
    # Ensure invalid value was actually written
    assert target_loc.input_value() == invalid_value, f"Could not set invalid value for '{field}'"

    _trigger_input_and_blur(target_loc)
    rp.page.wait_for_timeout(200)

    rp.check_terms()

    signals = _submit_and_collect_errors(rp)

    span_texts = " ".join(signals["span_errors"].values()).lower()
    reg_msg = signals["register_message"].lower()
    browser_msgs = " ".join([f"{vm['name']} {vm['message']}".lower() for vm in signals["validation_messages"]])
    combined_text = " ".join([span_texts, reg_msg, browser_msgs])

    # Must have at least one validation signal
    assert _has_any_error(signals), (
        f"Invalid input for '{field}' did not produce any validation signal. "
        f"Value='{invalid_value}', Signals={signals}"
    )

    # Prefer to see at least one expected keyword in the messages to ensure relevance
    if not any(kw.lower() in combined_text for kw in expected_keywords):
        pytest.fail(
            f"Validation occurred for '{field}', but none of expected keywords {expected_keywords} were present in messages. "
            f"Combined messages: '{combined_text}'"
        )


def test_TC06_password_mismatch(register_page: RegisterPage):
    """
    TC06: Password mismatch (password and confirm_password must be identical)
    """
    rp = register_page
    rp.goto()

    payload = BASE_VALID_PAYLOAD.copy()
    payload["password"] = "P@ssw0rd123"
    payload["confirm_password"] = "Different1!"

    rp.fill_form(payload)

    pw_loc = rp._one("password")
    cpw_loc = rp._one("confirm_password")
    assert pw_loc.input_value() == payload["password"]
    assert cpw_loc.input_value() == payload["confirm_password"]

    _trigger_input_and_blur(cpw_loc)
    rp.page.wait_for_timeout(200)

    rp.check_terms()

    signals = _submit_and_collect_errors(rp)

    confirm_span = signals["span_errors"].get("confirmPasswordError", "")
    reg_msg = signals["register_message"].lower()
    browser_msgs = " ".join([vm["message"].lower() for vm in signals["validation_messages"]])

    assert _has_any_error(signals), f"Password mismatch did not produce any validation signal. Signals: {signals}"
    assert (
        confirm_span
        or "password" in reg_msg
        or "mismatch" in reg_msg
        or "confirm" in browser_msgs
    ), f"Password mismatch produced signals but none referenced password/mismatch. Signals: {signals}"


def test_TC07_terms_not_checked(register_page: RegisterPage):
    """
    TC07: Terms not checked (Terms and Conditions checkbox must be checked)
    """
    rp = register_page
    rp.goto()

    rp.fill_form(BASE_VALID_PAYLOAD)
    # Ensure terms is unchecked
    terms = rp._one("terms")
    if terms.is_checked():
        terms.uncheck()

    _trigger_input_and_blur(rp._one("first_name"))
    rp.page.wait_for_timeout(200)

    signals = _submit_and_collect_errors(rp)

    reg_msg = signals["register_message"].lower()
    assert _has_any_error(signals), f"Submitting without agreeing to terms did not produce an error signal. Signals: {signals}"
    assert ("term" in reg_msg) or ("agree" in reg_msg) or any("term" in v.lower() or "agree" in v.lower() for v in signals["span_errors"].values()), (
        f"Expected a terms-related error but did not find one. Signals: {signals}"
    )


def test_TC08_newsletter_optional(register_page: RegisterPage):
    """
    TC08: Newsletter optional (not checking newsletter should NOT block submission)
    """
    rp = register_page
    rp.goto()

    rp.fill_form(BASE_VALID_PAYLOAD)
    rp.check_terms()

    newsletter = rp._one("newsletter")
    if newsletter.is_checked():
        newsletter.uncheck()

    nav = rp.submit(timeout=3000)
    if nav:
        # navigation happened -> success
        return

    try:
        msg = rp.wait_for_message_non_empty(timeout=5000)
        assert msg, "Expected a non-empty register message when newsletter is not checked"
    except Exception as e:
        pytest.fail(
            f"Submission without newsletter did not succeed (no navigation and no non-empty registerMessage). Exception: {e}"
        )


def test_TC09_login_link_navigation(register_page: RegisterPage):
    """
    TC09: Login link navigation must bring to the login page:
          https://qa-test-web-app.vercel.app/index.html
    """
    rp = register_page
    rp.goto()

    login_loc = rp._one("login_link")
    target_url = "https://qa-test-web-app.vercel.app/index.html"

    # Try to click and wait for exact navigation to target_url
    try:
        with rp.page.expect_navigation(timeout=3000, url=target_url):
            login_loc.click()
        assert rp.page.url == target_url, f"Expected to land on {target_url} but landed on {rp.page.url}"
    except Exception:
        # If navigation not observed, validate href attribute
        href = login_loc.get_attribute("href") or ""
        # Accept either full absolute URL or relative 'index.html'
        assert href.endswith("index.html") or href == "/" or href == target_url, f"Login link href does not target expected login page: href='{href}'"
