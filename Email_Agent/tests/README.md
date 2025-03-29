# Customer Discovery Bot Test Suite

This directory contains comprehensive unit tests for the Customer Discovery Bot application. The tests cover all major components of the system, including:

1. Email sending functionality
2. Google Sheets integration
3. Web search agent
4. Email drafting agent
5. Flask API server
6. Graph workflow
7. CSV export functionality

## Setup

Before running the tests, ensure you have installed the required testing dependencies:

```bash
pip install pytest pytest-mock
```

## Running Tests

You can run the tests in several ways:

### 1. Using the test runner script

```bash
python tests/run_tests.py
```

### 2. Using pytest directly

```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_email_sender.py

# Run a specific test
pytest tests/test_email_sender.py::test_create_contact_csv
```

### 3. Running with coverage

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=. tests/

# Generate HTML coverage report
pytest --cov=. --cov-report=html tests/
```

## Test Categories

Here's a breakdown of what each test file covers:

- **test_email_sender.py**: Tests the email functionality with a fake CSV
- **test_google_sheets.py**: Tests the ability to read and update Google Sheets
- **test_web_search.py**: Tests the web search agent
- **test_email_agent.py**: Tests the email drafting agent
- **test_api_flask.py**: Tests that the server works
- **test_graph.py**: Tests that the complete graph workflow works
- **test_csv_export.py**: Tests that the CSV export works

## Mock Data and Fixtures

The tests use fixtures defined in `conftest.py` to create mock data for testing. This includes:

- Mock contacts
- Mock environment variables
- Temporary CSV files

## Troubleshooting

If you encounter issues when running tests:

1. Ensure all dependencies are installed
2. Check that the paths in the test files match your project structure
3. Verify that environment variables are set correctly for tests that require them
4. For tests that use external services (like Google Sheets), ensure that you have the proper mock objects in place

## Adding New Tests

When adding new tests:

1. Follow the existing patterns
2. Use the fixtures provided in `conftest.py`
3. Use mocks for external dependencies
4. Ensure your tests are independent and don't rely on external services
