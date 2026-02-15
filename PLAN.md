# Introduction

QA Test of the registration form at the URL:
- [https://qa-test-web-app.vercel.app/register.html](https://qa-test-web-app.vercel.app/register.html)

The plan will follow the steps listed below for validation: 
- Manual test of the existing fields on the registration form
- Confirm if the validations appear correctly
- Report what happens on successful registration
- Indicate if any bugs have already been noticed

The preferred automation language is Python with Playwright.

## Registration form

The following fields are available in the form:
- First Name
- Last Name
- Email Address
- Phone Number
- Street Address
- City
- ZIP Code
- Password
- Confirm Password

Then two check boxes are present :
- I agree to the Terms and Conditions
- Subscribe to newsletter

Finally, there is the button "Create Account" and the link "Already have an account? Login"

## Test Coverage

Positive Scenario
- Successful registration with valid data
- Missing required fields are not accepted
- Duplicate email is detected and reported

Successful registration should redirect to:
```
/index.html?registered=true
```

Negative Scenario
- Invalid First and Last Name format
- Invalid ZIP and phone number
- Invalid email format
- Password mismatch
- Terms & Conditions not checked
- Newsletter checkbox optional
- Navigation to Login page

Notes
- The test suite is designed to be stable, fast, and easy to extend.
- HTML5 validation behavior is intentionally respected and tested.

## Test Plan

The scope of testing covers the user registration process at the URL https://qa-test-web-app.vercel.app/register.html

This includes:
- Form field validation
- UI/UX behavior
- Error handling
- Successful account creation
- Links and checkboxes

Testing Types
- Functional testing
- Negative testing
- Usability checks
- Automated testing using Playwright

Test Environment
- Browser: Chromium (headless)
- Network: Standard broadband
- OS: Ubuntu (Linux)
- Tools: Playwright (Python), pytest, GitHub

## Key Implementation Details

- Page Object Model (POM)
    - All UI interactions are encapsulated in the pages/ directory.
    - Selectors use stable IDs and unique placeholders to avoid strict‑mode conflicts
- HTML5 Validation Support

The application uses native browser validation for:
- Required fields
- Email format
This ensures accurate and fast validation checks.

The success test uses:
```python
with page.expect_navigation(url="**/index.html?registered=true"):
    registration.submit()
```
This ensures Playwright waits for the redirect correctly.

Please check the [REPORT](REPORT.md) to view the outcome of the tests.
