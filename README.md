# QA Registration – Playwright (Python)

## Overview

This project contains automated tests for the **Registration** feature of the QA Test Web App:

- Manual test design and reporting
- Automated functional tests for registration using **Playwright + Python**
- Page Object Model (POM) structure

## Tech stack

- Python 3.10+
- Playwright for Python
- Pytest

## Setup

1. **Clone the repository**

```bash
git clone https://github.com/lucamar/qa-test.git
cd qa-test
```

2. Create and activate a Python virtual environment (optional)
```bash
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Install Playwright browsers
```
python -m playwright install
```

## Running tests

### Run all tests
```
pytest -v
```

### Run only registration tests:
```
pytest -v tests/test_registration_*.py
```
