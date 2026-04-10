# Tests

Unit tests for cloud platform engineering scripts, using [pytest](https://docs.pytest.org/) with mocked AWS services.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r cpe_project/requirements.txt
pip install pytest pytest-cov
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cpe_project --cov-report=term-missing

# Run a specific test file
pytest tests/infra/s3/test_s3_bucket_check.py -v
```

## Structure

```
tests/
├── infra/
│   └── s3/
│       └── test_s3_bucket_check.py    # S3 compliance check tests
└── deployments/
```

Tests mirror the `cpe_project/` directory structure. Each test file corresponds to a script in the main codebase.

## Writing Tests

- Mock all AWS API calls using `unittest.mock` — tests must not require real AWS credentials.
- Test both success and failure paths (e.g., bucket exists vs. 404 vs. 403).
- Name test files `test_<script_name>.py` to match the source file.
