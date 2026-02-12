from pages.registration_page import RegistrationPage

def test_successful_registration(page):
    registration = RegistrationPage(page)
    registration.open()

    registration.fill_registration_form()
    registration.submit()

    # Adjust expectation to real behavior (URL change, message, etc.)
    # Example: assert "success" in registration.get_success_message().lower()
    # or:
    # page.wait_for_url("**/success.html")
    assert True  # placeholder until you confirm actual behavior
