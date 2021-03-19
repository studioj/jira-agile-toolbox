import unittest
from collections import namedtuple

from unittest.mock import Mock, MagicMock

from jira_agile_toolbox import JiraAgileToolBox


class MockedJiraIssue(object):
    def __init__(self, story_points=None, status="Reported"):

        self.fields = MagicMock()
        # self.fields.status = namedtuple("status", ["name"])
        self.fields.customfield_10282 = story_points
        self.fields.status.name = status


class TestEpicStoryPointRetrieval(unittest.TestCase):
    def test_get_story_points_from_epic_returns_a_dict_containing_the_total_story_points(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertIn("total", result.keys())

    def test_get_story_points_from_epic_looks_in_jira_for_all_children_of_the_epic(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(jira_client)

        # When
        jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        jira_client.search_issues.assert_called_with("'Epic Link' = " + "PROJ001-001", fields="customfield_10282", maxResults=0)

    def test_get_story_points_from_epic_calculates_the_total_story_pointS_for_3_issues(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(3, sps["total"])

    def test_get_story_points_from_epic_calculates_the_total_story_pointS_for_300_issues(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ] * 100
        jat = JiraAgileToolBox(jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(300, sps["total"])

    def test_get_story_points_from_epic_calculates_the_total_of_zerostory_point_when_none_are_assigned(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=None),
            MockedJiraIssue(),
            MockedJiraIssue(),
        ] * 1000
        jat = JiraAgileToolBox(jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(0, sps["total"])

    def test_get_story_points_from_epic_returns_a_dict_containing_the_found_statuses_as_keyword(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(0, "Reported"),
            MockedJiraIssue(1, "Investigated"),
            MockedJiraIssue(2, "Closed"),
        ]
        jat = JiraAgileToolBox(jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertIn("Reported", result.keys())
        self.assertIn("Investigated", result.keys())
        self.assertIn("Closed", result.keys())
        self.assertNotIn("In Progress", result.keys())

    def test_get_story_points_from_epic_returns_a_dict_containing_the_found_statuses_with_their_totals(self):
        # Given
        jira_client = Mock()
        jira_client.search_issues.return_value = [
            MockedJiraIssue(0, "Reported"),
            MockedJiraIssue(1, "Investigated"),
            MockedJiraIssue(1, "Closed"),
            MockedJiraIssue(1, "Closed"),
        ]
        jat = JiraAgileToolBox(jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual({"total": 3, "Reported": 0, "Investigated": 1, "Closed": 2}, result)
