import uuid
import pytest
from playwright.sync_api import expect
from pages.register_page import RegisterPage

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

ERROR_SPAN_IDS = [
    "emailError",
    "phoneError",
    "zipError",
    "passwordError",
    "confirmPasswordError",
]


def _trigger_input_and_blur(locator):
    """Trigger input and blur events so client-side validators run."""
    locator.evaluate(
        """el => {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        }"""
    )


def _submit_and_collect_errors(rp: RegisterPage):
    """
    Submit the form and collect:
      - browser validation messages (validationMessage)
      - text from known error spans
      - text from #registerMessage
      - current URL
    """
    page = rp.page
    # Attempt submit - we ignore navigation result here
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


def _run_invalid_field_case(register_page: RegisterPage, field: str, invalid_value: str, expected_keywords: list):
    """
    Helper to apply an invalid value to a single field, trigger validators, submit,
    and assert that a relevant validation/error signal is present.
    """
    rp = register_page
    rp.goto()

    payload = BASE_VALID_PAYLOAD.copy()
    payload[field] = invalid_value

    rp.fill_form(payload)

    target_loc = rp._one(field)
    # Ensure the invalid value was set
    assert target_loc.input_value() == invalid_value, f"Could not set invalid value for '{field}'"

    _trigger_input_and_blur(target_loc)
    rp.page.wait_for_timeout(200)

    rp.check_terms()

    signals = _submit_and_collect_errors(rp)

    span_texts = " ".join(signals["span_errors"].values()).lower()
    reg_msg = signals["register_message"].lower()
    browser_msgs = " ".join([f"{vm['name']} {vm['message']}".lower() for vm in signals["validation_messages"]])
    combined_text = " ".join([span_texts, reg_msg, browser_msgs])

    # Must detect at least one error signal
    assert _has_any_error(signals), (
        f"Invalid input for '{field}' did not produce any validation signal. "
        f"Value='{invalid_value}', Signals={signals}"
    )

    # Prefer to find at least one expected keyword to ensure relevancy
    if not any(kw.lower() in combined_text for kw in expected_keywords):
        pytest.fail(
            f"Validation occurred for '{field}', but none of the expected keywords {expected_keywords} "
            f"were found in messages. Combined: '{combined_text}'"
        )


# TC01: Invalid First Name format (only letters aA-zZ)
def test_TC01_invalid_first_name_format(register_page: RegisterPage):
    _run_invalid_field_case(
        register_page,
        field="first_name",
        invalid_value="John123!",
        expected_keywords=["first", "name", "letters", "invalid"],
    )


# TC02: Invalid Last Name format (only letters aA-zZ)
def test_TC02_invalid_last_name_format(register_page: RegisterPage):
    _run_invalid_field_case(
        register_page,
        field="last_name",
        invalid_value="Doe99$",
        expected_keywords=["last", "name", "letters", "invalid"],
    )


# TC03: Invalid email format (must contain @ and a domain)
def test_TC03_invalid_email_format(register_page: RegisterPage):
    """
    Generates a randomized invalid email string to avoid 'User already exists' server message.
    The generated value includes '@' and a domain-like part but lacks a proper TLD,
    e.g. '<random>@invalid', which should exercise the client-side/email-format validation
    without colliding with existing users.
    """
    rp = register_page
    rp.goto()

    # random local part to avoid existing-email collisions
    local = uuid.uuid4().hex[:8]
    invalid_email = f"{local}@invalid"  # contains '@' and a domain-like part but no TLD

    payload = BASE_VALID_PAYLOAD.copy()
    payload["email"] = invalid_email

    rp.fill_form(payload)

    # confirm it was set correctly
    email_loc = rp._one("email")
    assert email_loc.input_value() == invalid_email, f"Failed to set randomized invalid email: {invalid_email}"

    _trigger_input_and_blur(email_loc)
    rp.page.wait_for_timeout(200)

    rp.check_terms()

    signals = _submit_and_collect_errors(rp)

    # validate we got an email-related validation signal
    span_texts = " ".join(signals["span_errors"].values()).lower()
    reg_msg = signals["register_message"].lower()
    browser_msgs = " ".join([f"{vm['name']} {vm['message']}".lower() for vm in signals["validation_messages"]])
    combined_text = " ".join([span_texts, reg_msg, browser_msgs])

    assert _has_any_error(signals), f"Randomized invalid email '{invalid_email}' did not produce any validation signal. Signals: {signals}"
    assert any(kw in combined_text for kw in ["@", "email", "domain", "invalid"]), (
        f"Email validation occurred but messages did not reference expected keywords. Combined: '{combined_text}'"
    )


# TC04: Invalid Phone Number (should contain a country code followed by digits)
def test_TC04_invalid_phone_number(register_page: RegisterPage):
    _run_invalid_field_case(
        register_page,
        field="phone",
        invalid_value="abcd-efg",
        expected_keywords=["phone", "country", "code", "+", "digits", "invalid"],
    )


# TC05: Invalid ZIP Code (only 4 or 5 digits)
def test_TC05_invalid_zip_code(register_page: RegisterPage):
    _run_invalid_field_case(
        register_page,
        field="zip",
        invalid_value="12ab",
        expected_keywords=["zip", "postal", "code", "digit", "invalid"],
    )


# TC06: Password mismatch (password and confirm_password must be identical)
def test_TC06_password_mismatch(register_page: RegisterPage):
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


# TC07: Terms not checked (Terms and Conditions checkbox must be checked)
def test_TC07_terms_not_checked(register_page: RegisterPage):
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


# TC08: Newsletter optional (not checking newsletter should NOT block submission)
def test_TC08_newsletter_optional(register_page: RegisterPage):
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


# TC09: Login link navigation must bring to the specific login page URL
def test_TC09_login_link_navigation(register_page: RegisterPage):
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
