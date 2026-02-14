# QA Registration – Playwright (Python)

## Overview

This project contains automated tests for the **Registration** feature of the QA Test Web App:

https://qa-test-web-app.vercel.app/register.html

The suite includes:

- Manual test design and reporting
- Automated functional tests using **Playwright + Python**
- Page Object Model (POM)
- Optimized selectors and fast execution strategies
- Support for both HTML5 validation and custom DOM validation
- Correct handling of redirect-based success flow

The goal is to validate the correctness, usability, and robustness of the registration flow.

---

## Tech Stack

- Python 3.10+
- Playwright for Python
- Pytest
- Page Object Model (POM)

---

## Project Structure

qa-test/
├─ pages/
│  ├─ register_page.py
├─ tests/
│  ├─ test_registration_form.py
│  ├─ test_registration_negative.py
├─ conftest.py
├─ requirements.txt
└─ README.md

---

## Setup Instructions

### Clone the repository

```bash
git clone https://github.com/lucamar/qa-test.git
cd qa-test
```

2. Create and activate a virtual environment (optional)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install Playwright browsers

```bash
python -m playwright install
```

### Running Tests

Run all tests:
```bash
pytest -v
```

Run only registration tests:
```bash
pytest -v tests/test_registration_*.py
```

### Key Implementation Details
✔ Page Object Model (POM)

All UI interactions are encapsulated in the pages/ directory.
Selectors use stable IDs and unique placeholders to avoid strict‑mode conflicts.
✔ HTML5 Validation Support

The application uses native browser validation for:
- Required fields
- Email format

Tests detect this using: 
```python
page.locator("input:invalid").first
```

This ensures accurate and fast validation checks.
✔ Optimized Test Execution

To avoid unnecessary waiting:
- The Register button is clicked using a direct DOM click:

```python
self.page.evaluate("el => el.click()", self.register_button)
```

This bypasses:
- Actionability checks
- HTML5 validation blocking
- Navigation waits

Result: fast and stable tests.
✔ Correct Redirect Handling

Successful registration redirects to:
```
/index.html?registered=true
```

The success test uses:
```python
with page.expect_navigation(url="**/index.html?registered=true"):
    registration.submit()
```

This ensures Playwright waits for the redirect correctly.

What Is Tested?

Positive Scenario
- Successful registration with valid data
- Verified via redirect to index.html?registered=true

Negative Scenarios
- Missing required fields (HTML5 validation)
- Invalid email format (HTML5 validation)
- Password mismatch (custom validation)
- Terms & Conditions not checked (custom validation)
- Invalid ZIP and phone number (custom validation)
- Newsletter checkbox optional
- Navigation to Login page

Known Issues (Based on Test Results)

The following defects were identified:
- Invalid email formats are accepted (Bug‑001)
- ZIP Code validation missing (Bug‑002)
- Phone Number validation missing (Bug‑003)
- Password mismatch not detected (Bug-004)

Notes
- The test suite is designed to be stable, fast, and easy to extend.
- HTML5 validation behavior is intentionally respected and tested.
