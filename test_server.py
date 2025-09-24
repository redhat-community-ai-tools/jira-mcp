#!/usr/bin/env python

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
import json

# Set up required environment variables before importing server module
os.environ["JIRA_URL"] = "https://test.example.com"
os.environ["JIRA_API_TOKEN"] = "test-token"

# Mock JIRA client creation before importing server module
with patch("jira.JIRA"):
    # Import the server module
    import server


class MockJiraIssue:
    """Mock Jira issue object"""

    def __init__(self, key, summary="Test Summary", description="Test Description", **kwargs):
        self.key = key
        self.fields = MagicMock()
        self.fields.summary = summary
        self.fields.description = description

        # Set up common fields
        self.fields.status = MagicMock()
        self.fields.status.name = kwargs.get("status_name", "Open")

        self.fields.assignee = MagicMock() if kwargs.get("assignee") else None
        if self.fields.assignee:
            self.fields.assignee.displayName = kwargs.get("assignee", "Test User")

        self.fields.reporter = MagicMock()
        self.fields.reporter.displayName = kwargs.get("reporter", "Test Reporter")

        self.fields.priority = MagicMock()
        self.fields.priority.name = kwargs.get("priority", "Medium")

        self.fields.issuetype = MagicMock()
        self.fields.issuetype.name = kwargs.get("issuetype", "Task")

        self.fields.fixVersions = kwargs.get("fixVersions", [])
        self.fields.created = kwargs.get("created", "2023-01-01T00:00:00.000+0000")
        self.fields.updated = kwargs.get("updated", "2023-01-01T00:00:00.000+0000")
        self.fields.labels = kwargs.get("labels", [])

        # QA Contact custom field
        setattr(self.fields, server.QA_CONTACT_FID, kwargs.get("qa_contact"))

        # Comments
        self.fields.comment = MagicMock()
        self.fields.comment.comments = kwargs.get("comments", [])

        # Mock methods
        self.update = MagicMock()
        self.delete = MagicMock()


class MockJiraProject:
    """Mock Jira project object"""

    def __init__(self, key, name="Test Project"):
        self.key = key
        self.name = name
        self.raw = {"key": key, "name": name}


class MockJiraUser:
    """Mock Jira user object"""

    def __init__(self, account_id, display_name="Test User"):
        self.accountId = account_id
        self.displayName = display_name
        self.raw = {"accountId": account_id, "displayName": display_name}


class MockJiraComment:
    """Mock Jira comment object"""

    def __init__(self, comment_id, body="Test comment", author_name="Test Author"):
        self.id = comment_id
        self.body = body
        self.author = MagicMock()
        self.author.displayName = author_name
        self.created = "2023-01-01T00:00:00.000+0000"
        self.updated = "2023-01-01T00:00:00.000+0000"

        # Mock methods
        self.delete = MagicMock()


@pytest.fixture
def mock_jira_client():
    """Create a mock Jira client"""
    with patch("server.jira_client") as mock_client:
        yield mock_client


@pytest.fixture
def sample_issue():
    """Create a sample issue for testing"""
    return MockJiraIssue(
        "TEST-123",
        summary="Test Issue",
        description="This is a test issue",
        assignee="John Doe",
        priority="High",
    )


@pytest.fixture
def sample_project():
    """Create a sample project for testing"""
    return MockJiraProject("TEST", "Test Project")


class TestGetJira:
    """Test the get_jira tool"""

    def test_get_jira_success(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue

        result = server.get_jira.fn("TEST-123")

        assert result == "# TEST-123: Test Issue\n\nThis is a test issue"
        mock_jira_client.issue.assert_called_once_with("TEST-123")

    def test_get_jira_missing_fields(self, mock_jira_client):
        issue = MockJiraIssue("TEST-123", summary=None, description=None)
        mock_jira_client.issue.return_value = issue

        result = server.get_jira.fn("TEST-123")

        assert result == "# TEST-123: \n\n"

    def test_get_jira_not_found(self, mock_jira_client):
        mock_jira_client.issue.side_effect = Exception("Issue not found")

        with pytest.raises(HTTPException) as exc_info:
            server.get_jira.fn("NONEXISTENT-123")

        assert exc_info.value.status_code == 404
        assert "Failed to fetch Jira issue NONEXISTENT-123" in str(exc_info.value.detail)


class TestSearchIssues:
    """Test the search_issues tool"""

    def test_search_issues_success(self, mock_jira_client):
        issues = [
            MockJiraIssue("TEST-1", "First Issue"),
            MockJiraIssue("TEST-2", "Second Issue", assignee="Jane Doe"),
        ]
        mock_jira_client.search_issues.return_value = issues

        result = server.search_issues.fn("project = TEST", max_results=50)

        assert "TEST-1" in result
        assert "TEST-2" in result
        assert "First Issue" in result
        assert "Second Issue" in result
        mock_jira_client.search_issues.assert_called_once_with("project = TEST", maxResults=50)

    def test_search_issues_empty_result(self, mock_jira_client):
        mock_jira_client.search_issues.return_value = []

        result = server.search_issues.fn("project = EMPTY")

        assert result == ""

    def test_search_issues_invalid_jql(self, mock_jira_client):
        mock_jira_client.search_issues.side_effect = Exception("Invalid JQL")

        with pytest.raises(HTTPException) as exc_info:
            server.search_issues.fn("invalid jql")

        assert exc_info.value.status_code == 400
        assert "JQL search failed" in str(exc_info.value.detail)


class TestProjectOperations:
    """Test project-related tools"""

    def test_list_projects_success(self, mock_jira_client):
        projects = [
            MockJiraProject("TEST1", "Test Project 1"),
            MockJiraProject("TEST2", "Test Project 2"),
        ]
        mock_jira_client.projects.return_value = projects

        result = server.list_projects.fn()

        assert "TEST1" in result
        assert "TEST2" in result
        mock_jira_client.projects.assert_called_once()

    def test_get_project_success(self, mock_jira_client, sample_project):
        mock_jira_client.project.return_value = sample_project

        result = server.get_project.fn("TEST")

        assert "TEST" in result
        mock_jira_client.project.assert_called_once_with("TEST")

    def test_get_project_not_found(self, mock_jira_client):
        mock_jira_client.project.side_effect = Exception("Project not found")

        with pytest.raises(HTTPException) as exc_info:
            server.get_project.fn("NONEXISTENT")

        assert exc_info.value.status_code == 404


class TestUserOperations:
    """Test user-related tools"""

    def test_get_current_user_success(self, mock_jira_client):
        user = MockJiraUser("12345", "Current User")
        mock_jira_client.myself.return_value = user

        result = server.get_current_user.fn()

        assert "12345" in result
        assert "Current User" in result
        mock_jira_client.myself.assert_called_once()

    def test_search_users_success(self, mock_jira_client):
        users = [MockJiraUser("123", "John Doe"), MockJiraUser("456", "Jane Smith")]
        mock_jira_client.search_users.return_value = users

        result = server.search_users.fn("john", max_results=5)

        assert "John Doe" in result
        assert "Jane Smith" in result
        mock_jira_client.search_users.assert_called_once_with("john", maxResults=5)

    def test_get_user_success(self, mock_jira_client):
        user = MockJiraUser("12345", "Test User")
        mock_jira_client.user.return_value = user

        result = server.get_user.fn("12345")

        assert "12345" in result
        mock_jira_client.user.assert_called_once_with("12345")


class TestWriteOperations:
    """Test write operation tools (when enabled)"""

    @patch("server.ENABLE_WRITE", True)
    def test_create_issue_success(self, mock_jira_client):
        new_issue = MockJiraIssue("TEST-456", "New Issue")
        mock_jira_client.create_issue.return_value = new_issue

        result = server.create_issue.fn(
            project_key="TEST",
            summary="New Issue",
            description="Description",
            issue_type="Task",
            priority="High",
            assignee="john.doe",
        )

        assert "Created issue TEST-456" in result
        mock_jira_client.create_issue.assert_called_once()

        call_args = mock_jira_client.create_issue.call_args[1]["fields"]
        assert call_args["project"]["key"] == "TEST"
        assert call_args["summary"] == "New Issue"
        assert call_args["assignee"]["name"] == "john.doe"

    @patch("server.ENABLE_WRITE", True)
    def test_update_issue_success(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue

        result = server.update_issue.fn(
            issue_key="TEST-123", summary="Updated Summary", priority="Low"
        )

        assert "Updated issue TEST-123 successfully" in result
        sample_issue.update.assert_called_once()

    @patch("server.ENABLE_WRITE", True)
    def test_add_comment_success(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue
        comment = MockJiraComment("comment-123", "Test comment")
        mock_jira_client.add_comment.return_value = comment

        result = server.add_comment.fn("TEST-123", "Test comment")

        assert "Added comment to TEST-123: comment-123" in result
        mock_jira_client.add_comment.assert_called_once_with(sample_issue, "Test comment")

    @patch("server.ENABLE_WRITE", True)
    def test_assign_issue_success(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue

        result = server.assign_issue.fn("TEST-123", "john.doe")

        assert "Assigned issue TEST-123 to john.doe" in result
        mock_jira_client.assign_issue.assert_called_once_with(sample_issue, "john.doe")

    @patch("server.ENABLE_WRITE", True)
    def test_transition_issue_success(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue
        transitions = [{"id": "1", "name": "In Progress"}, {"id": "2", "name": "Done"}]
        mock_jira_client.transitions.return_value = transitions

        result = server.transition_issue.fn("TEST-123", "In Progress")

        assert "Transitioned issue TEST-123 to 'In Progress'" in result
        mock_jira_client.transition_issue.assert_called_once_with(sample_issue, "1")

    @patch("server.ENABLE_WRITE", True)
    def test_transition_issue_not_found(self, mock_jira_client, sample_issue):
        mock_jira_client.issue.return_value = sample_issue
        transitions = [{"id": "1", "name": "In Progress"}]
        mock_jira_client.transitions.return_value = transitions

        result = server.transition_issue.fn("TEST-123", "Invalid Transition")

        assert "Transition 'Invalid Transition' not found" in result
        assert "Available transitions: In Progress" in result


class TestCommentOperations:
    """Test comment-related operations"""

    def test_get_issue_comments_success(self, mock_jira_client):
        comments = [
            MockJiraComment("1", "First comment", "Author 1"),
            MockJiraComment("2", "Second comment", "Author 2"),
        ]

        issue = MockJiraIssue("TEST-123", comments=comments)
        mock_jira_client.issue.return_value = issue

        result = server.get_issue_comments.fn("TEST-123")

        assert "First comment" in result
        assert "Second comment" in result
        assert "Author 1" in result
        assert "Author 2" in result

    @patch("server.ENABLE_WRITE", True)
    def test_delete_comment_success(self, mock_jira_client):
        comment = MockJiraComment("comment-123", "Test comment")
        mock_jira_client.comment.return_value = comment

        result = server.delete_comment.fn("TEST-123", "comment-123")

        assert "Deleted comment comment-123 from TEST-123" in result
        mock_jira_client.comment.assert_called_once_with("TEST-123", "comment-123")
        comment.delete.assert_called_once()


class TestUtilityFunctions:
    """Test utility functions"""

    def test_to_markdown_dict(self):
        data = {"key": "value", "number": 123}
        result = server.to_markdown(data)

        assert result.startswith("```json\n")
        assert result.endswith("\n```")
        assert "key" in result
        assert "value" in result

    def test_to_markdown_object_with_raw(self):
        obj = MagicMock()
        obj.raw = {"test": "data"}

        result = server.to_markdown(obj)

        assert "```json\n" in result
        assert "test" in result
        assert "data" in result

    def test_to_markdown_list(self):
        data = [{"item1": "value1"}, {"item2": "value2"}]
        result = server.to_markdown(data)

        assert "item1" in result
        assert "item2" in result
        assert "value1" in result
        assert "value2" in result

    def test_to_markdown_string(self):
        data = "simple string"
        result = server.to_markdown(data)

        assert result == "simple string"


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_http_exception_status_codes(self, mock_jira_client):
        # Test different error scenarios and their status codes
        test_cases = [
            (server.get_jira.fn, ("TEST-123",), 404, "Failed to fetch Jira issue"),
            (server.search_issues.fn, ("invalid jql",), 400, "JQL search failed"),
            (server.list_projects.fn, (), 500, "Failed to fetch projects"),
            (server.get_project.fn, ("NONEXISTENT",), 404, "Failed to fetch project"),
        ]

        for func, args, expected_status, expected_detail in test_cases:
            mock_jira_client.reset_mock()

            # Configure the appropriate mock method to raise an exception
            if func == server.get_jira.fn:
                mock_jira_client.issue.side_effect = Exception("Test error")
            elif func == server.search_issues.fn:
                mock_jira_client.search_issues.side_effect = Exception("Test error")
            elif func == server.list_projects.fn:
                mock_jira_client.projects.side_effect = Exception("Test error")
            elif func == server.get_project.fn:
                mock_jira_client.project.side_effect = Exception("Test error")

            with pytest.raises(HTTPException) as exc_info:
                func(*args)

            assert exc_info.value.status_code == expected_status
            assert expected_detail in str(exc_info.value.detail)


class TestArgumentParsing:
    """Test command line argument parsing"""

    def test_parse_arguments_default(self):
        with patch("sys.argv", ["server.py"]):
            args = server.parse_arguments()

            assert args.transport == "stdio"
            assert args.host == "localhost"
            assert args.port == 3000

    def test_parse_arguments_http(self):
        with patch("sys.argv", ["server.py", "--transport", "http", "--port", "8080"]):
            args = server.parse_arguments()

            assert args.transport == "http"
            assert args.port == 8080

    def test_parse_arguments_sse(self):
        with patch("sys.argv", ["server.py", "-t", "sse", "--host", "0.0.0.0"]):
            args = server.parse_arguments()

            assert args.transport == "sse"
            assert args.host == "0.0.0.0"


class TestEnvironmentConfiguration:
    """Test environment variable configuration"""

    def test_environment_variables_exist(self):
        """Test that the environment variables are accessible"""
        # Just test that the variables exist in the server module
        assert hasattr(server, "JIRA_URL")
        assert hasattr(server, "JIRA_API_TOKEN")
        assert hasattr(server, "ENABLE_WRITE")

    def test_enable_write_boolean(self):
        """Test that ENABLE_WRITE is a boolean"""
        assert isinstance(server.ENABLE_WRITE, bool)


class TestBoardsAndSprints:
    """Test boards and sprints functionality"""

    def test_list_boards_success(self, mock_jira_client):
        boards = [
            MagicMock(raw={"id": 1, "name": "Test Board 1"}),
            MagicMock(raw={"id": 2, "name": "Test Board 2"}),
        ]
        mock_jira_client.boards.return_value = boards

        result = server.list_boards.fn(max_results=5, project_key_or_id="TEST")

        assert "Test Board 1" in result
        assert "Test Board 2" in result
        mock_jira_client.boards.assert_called_once_with(maxResults=5, projectKeyOrID="TEST")

    def test_list_sprints_success(self, mock_jira_client):
        sprints = [
            MagicMock(raw={"id": 1, "name": "Sprint 1", "state": "active"}),
            MagicMock(raw={"id": 2, "name": "Sprint 2", "state": "closed"}),
        ]
        mock_jira_client.sprints.return_value = sprints

        result = server.list_sprints.fn(board_id=123, max_results=10)

        assert "Sprint 1" in result
        assert "Sprint 2" in result
        mock_jira_client.sprints.assert_called_once_with(123, maxResults=10)

    def test_get_sprint_success(self, mock_jira_client):
        sprint = MagicMock(raw={"id": 456, "name": "Test Sprint", "state": "active"})
        mock_jira_client.sprint.return_value = sprint

        result = server.get_sprint.fn(456)

        assert "Test Sprint" in result
        mock_jira_client.sprint.assert_called_once_with(456)


class TestLabelOperations:
    """Test label operations"""

    @patch("server.ENABLE_WRITE", True)
    def test_add_issue_labels_success(self, mock_jira_client, sample_issue):
        sample_issue.fields.labels = ["existing-label"]
        mock_jira_client.issue.return_value = sample_issue

        result = server.add_issue_labels.fn("TEST-123", ["new-label", "another-label"])

        assert "Added labels ['new-label', 'another-label'] to issue TEST-123" in result
        sample_issue.update.assert_called_once()

        # Check that new labels were added to existing ones
        call_args = sample_issue.update.call_args[1]["fields"]["labels"]
        assert "existing-label" in call_args
        assert "new-label" in call_args
        assert "another-label" in call_args

    @patch("server.ENABLE_WRITE", True)
    def test_remove_issue_labels_success(self, mock_jira_client, sample_issue):
        sample_issue.fields.labels = ["label1", "label2", "label3"]
        mock_jira_client.issue.return_value = sample_issue

        result = server.remove_issue_labels.fn("TEST-123", ["label2"])

        assert "Removed labels ['label2'] from issue TEST-123" in result
        sample_issue.update.assert_called_once()

        # Check that only specified labels were removed
        call_args = sample_issue.update.call_args[1]["fields"]["labels"]
        assert "label1" in call_args
        assert "label2" not in call_args
        assert "label3" in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
