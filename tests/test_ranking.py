from unittest import TestCase
from unittest.mock import Mock, MagicMock, call

import jira

from jira_agile_toolbox import JiraAgileToolBox

mocked_issue_1 = Mock(spec=jira.Issue)
mocked_issue_1.key = "PsY-001"
mocked_issue_2 = Mock(spec=jira.Issue)
mocked_issue_2.key = "PsY-002"
mocked_issue_3 = Mock(spec=jira.Issue)
mocked_issue_3.key = "PsY-003"
mocked_issue_4 = Mock(spec=jira.Issue)
mocked_issue_4.key = "PsY-004"
MOCKED_JIRA_ISSUE_PS_Y_ = [mocked_issue_1, mocked_issue_2, mocked_issue_3]


class TestRanking(TestCase):
    def test_ranking_by_list_calls_the_jira_client_in_the_proper_order(self):
        # Given
        jira_client = Mock(spec=jira.JIRA)
        ranked_list = MOCKED_JIRA_ISSUE_PS_Y_
        on_top_of = mocked_issue_4

        jat = JiraAgileToolBox(jira_client)

        # When
        jat.rank_issues_by_list(ranked_list, on_top_of)

        # Then
        jira_client.rank.assert_has_calls(
            [
                call(mocked_issue_3.key, mocked_issue_4.key),
                call(mocked_issue_2.key, mocked_issue_3.key),
                call(mocked_issue_1.key, mocked_issue_2.key),
            ]
        )

    def test_ranking_by_list_calls_the_jira_client_in_the_proper_order_with_other_order(self):
        # Given
        jira_client = Mock(spec=jira.JIRA)
        ranked_list = list(reversed(MOCKED_JIRA_ISSUE_PS_Y_))
        on_top_of = mocked_issue_4

        jat = JiraAgileToolBox(jira_client)

        # When
        jat.rank_issues_by_list(ranked_list, on_top_of)

        # Then
        jira_client.rank.assert_has_calls(
            [
                call(mocked_issue_1.key, mocked_issue_4.key),
                call(mocked_issue_2.key, mocked_issue_1.key),
                call(mocked_issue_3.key, mocked_issue_2.key),
            ]
        )

    def test_ranking_at_the_top_of_the_backlog_searches_for_the_highest_ranked_issue(self):
        jira_client = Mock()

        ranked_list = MOCKED_JIRA_ISSUE_PS_Y_ + [mocked_issue_4]

        jira_client.search_issues = Mock(return_value=ranked_list)

        project = "PsY"

        jat = JiraAgileToolBox(jira_client)

        # When
        jat.rank_issues_at_top_of_project(MOCKED_JIRA_ISSUE_PS_Y_, project)

        # Then
        jira_client.rank.assert_has_calls(
            [
                call(mocked_issue_3.key, mocked_issue_4.key),
                call(mocked_issue_2.key, mocked_issue_3.key),
                call(mocked_issue_1.key, mocked_issue_2.key),
            ]
        )
