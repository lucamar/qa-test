# QA Registration – Playwright (Python)

## Overview

This project contains automated tests for the **Registration** feature of the QA Test Web App: 
[https://qa-test-web-app.vercel.app/register.html](https://qa-test-web-app.vercel.app/register.html)

The suite includes:

- Manual test design described in [PLAN](PLAN)
- Automated functional tests using **Playwright + Python**
- Page Object Model (POM)
- Correct handling of redirect-based success flow
- Report test results in [REPORT](REPORT.md)

The goal is to validate the correctness, usability, and robustness of the registration flow.

### Tech Stack

- Python 3.10+
- Playwright for Python
- Pytest
- Page Object Model (POM)

### Project Structure
```
qa-test
    - pages/
        - register_page.py
    - tests/
        - test_registration_form.py
        - test_registration_negative.py
conftest.py
requirements.txt
README.md
```

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

Run all tests (success and negative tests, verbose mode):
```bash
pytest -v --html=reports/report.html --self-contained-html
```

### Key Implementation Details

- Page Object Model (POM)
    - All UI interactions are encapsulated in the pages/ directory.
    - Selectors use stable IDs and unique placeholders to avoid strict‑mode conflicts
- HTML5 Validation Support

The application uses native browser validation for:
- Required fields
- Email format
This ensures accurate and fast validation checks.

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
