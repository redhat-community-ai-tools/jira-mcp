# Testing Guide

This project includes test coverage for the Jira MCP server.

## Test Structure

The test suite (`test_server.py`) provides coverage for all MCP tools and utility functions in `server.py`:

### Test Categories

- **TestGetJira**: Tests for retrieving individual Jira issues
- **TestSearchIssues**: Tests for JQL-based issue searching
- **TestProjectOperations**: Tests for project-related operations
- **TestUserOperations**: Tests for user-related operations
- **TestWriteOperations**: Tests for create/update/delete operations (when write mode enabled)
- **TestCommentOperations**: Tests for comment management
- **TestBoardsAndSprints**: Tests for Agile board and sprint operations
- **TestLabelOperations**: Tests for issue label management
- **TestUtilityFunctions**: Tests for helper functions like `to_markdown`
- **TestArgumentParsing**: Tests for command-line argument parsing
- **TestEnvironmentConfiguration**: Tests for environment variable handling
- **TestErrorHandling**: Tests for various error scenarios and HTTP status codes

## Running Tests

### Basic Commands

```bash
# Run all tests
make quiet-test

# Run tests with verbose output
make test

# Run CI pipeline (format check + tests)
make ci

# Format code with black
make fmt
```

### Advanced pytest Commands

```bash
# Run specific test class
python -m pytest test_server.py::TestGetJira -v

# Run specific test method
python -m pytest test_server.py::TestGetJira::test_get_jira_success -v

# Run tests matching a pattern
python -m pytest test_server.py -k "test_get" -v

# Run tests with detailed output
python -m pytest test_server.py -v -s
```

## Test Configuration

- **pyproject.toml**: Test configuration including markers and options (in `[tool.pytest.ini_options]` section)
- **Makefile**: Test automation targets
- Tests use mocking to avoid requiring actual Jira connections
- All MCP tools are tested by accessing their underlying functions via `.fn` attribute

## Mocking Strategy

The tests use sophisticated mock objects:

- **MockJiraIssue**: Simulates Jira issue objects with all required fields
- **MockJiraProject**: Simulates project objects
- **MockJiraUser**: Simulates user objects
- **MockJiraComment**: Simulates comment objects
- **mock_jira_client**: Fixture that mocks the entire JIRA client


## Adding New Tests

When adding new MCP tools to `server.py`:

1. Add corresponding test methods to appropriate test class
2. Use existing mock objects or create new ones as needed
3. Test both success and error scenarios
4. Access MCP tool functions via `.fn` attribute (e.g., `server.new_tool.fn()`)
5. Ensure tests pass the format check: `make ci`

Example test structure:
```python
def test_new_tool_success(self, mock_jira_client):
    # Setup mocks
    mock_jira_client.some_method.return_value = expected_result

    # Call the tool function
    result = server.new_tool.fn("test-input")

    # Assertions
    assert "expected output" in result
    mock_jira_client.some_method.assert_called_once_with("test-input")
```

## Continuous Integration

The `make ci` target runs:
1. **Format check**: Ensures code follows black formatting standards
2. **Tests**: Runs the full test suite

This should be run before committing changes to ensure code quality.
