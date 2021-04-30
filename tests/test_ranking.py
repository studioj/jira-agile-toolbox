from unittest import TestCase
from unittest.mock import Mock, MagicMock, call

import jira

from jira_agile_toolbox import JiraAgileToolBox


class MockedJiraIssue(jira.Issue):
    def __init__(self, key, status="Reported"):
        self.fields = MagicMock()
        self.key = key


class TestRanking(TestCase):
    def test_ranking_by_list_calls_the_jira_client_in_the_proper_order(self):
        # Given
        jira_client = Mock()
        ranked_list = [MockedJiraIssue("PY-001"), MockedJiraIssue("PY-002"), MockedJiraIssue("PY-003")]
        on_top_of = MockedJiraIssue("PY-100")

        jat = JiraAgileToolBox(jira_client)

        # When
        jat.rank_issues_by_list(ranked_list, on_top_of)

        # Then
        jira_client.rank.assert_has_calls([call("PY-003", "PY-100"), call("PY-002", "PY-003"), call("PY-001", "PY-002")])

    def test_ranking_by_list_calls_the_jira_client_in_the_proper_order_with_other_order(self):
        # Given
        jira_client = Mock()
        ranked_list = [MockedJiraIssue("PsY-011"), MockedJiraIssue("PsY-002"), MockedJiraIssue("PsY-103")]
        on_top_of = MockedJiraIssue("PsY-100")

        jat = JiraAgileToolBox(jira_client)

        # When
        jat.rank_issues_by_list(ranked_list, on_top_of)

        # Then
        jira_client.rank.assert_has_calls([call("PsY-103", "PsY-100"), call("PsY-002", "PsY-103"), call("PsY-011", "PsY-002")])
