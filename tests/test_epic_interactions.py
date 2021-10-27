from unittest import TestCase
from unittest.mock import Mock

import jira
import jira.resources

from jira_agile_toolbox import JiraAgileToolBox
from lib_for_tests import DEFAULT_FIELDS_RETURN_VALUE, MockedJiraIssue

VERSION_RAW = {
    "self": "https://atlassian-jira.com/rest/api/2/version/31063",
    "id": "31063",
    "description": "",
    "name": "JAT 0.0.9",
    "archived": False,
    "released": True,
}


class TestEpicStoryPointRetrieval(TestCase):
    def setUp(self) -> None:
        self.jira_client = Mock(spec=jira.JIRA)

    def test_get_story_points_from_epic_returns_a_dict_containing_the_total_story_points(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertIn("total", result.keys())

    def test_get_story_points_from_epic_looks_in_jira_for_all_children_of_the_epic(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        epic = "PROJ001-001"
        jat.get_storypoints_from_epic(epic)

        # Then
        self.jira_client.search_issues.assert_called_with(f"'Epic Link' = {epic}", fields=["customfield_10282", "status"], maxResults=0)

    def test_get_story_points_from_epic_looks_in_jira_for_all_children_of_the_epic_passes_on_a_jql_query(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)
        epic = "PROJ001-001"
        jql_query = "project in (PROJ001,PROJ002)"

        # When
        jat.get_storypoints_from_epic(epic, jql_query=jql_query)

        # Then
        self.jira_client.search_issues.assert_called_with(
            f"'Epic Link' = {epic} AND {jql_query}", fields=["customfield_10282", "status"], maxResults=0
        )

    def test_get_story_points_from_epic_calculates_the_total_story_pointS_for_3_issues(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(3, sps["total"])

    def test_get_story_points_from_epic_calculates_the_total_story_pointS_for_300_issues(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ] * 100
        jat = JiraAgileToolBox(self.jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(300, sps["total"])

    def test_get_story_points_from_epic_calculates_the_total_of_zero_story_point_when_none_are_assigned(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=None),
            MockedJiraIssue(),
            MockedJiraIssue(),
        ] * 1000
        jat = JiraAgileToolBox(self.jira_client)

        # When
        sps = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual(0, sps["total"])

    def test_get_story_points_from_epic_returns_a_dict_containing_the_found_statuses_as_keyword(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(0, "Reported"),
            MockedJiraIssue(1, "Investigated"),
            MockedJiraIssue(2, "Closed"),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertIn("Reported", result.keys())
        self.assertIn("Investigated", result.keys())
        self.assertIn("Closed", result.keys())
        self.assertNotIn("In Progress", result.keys())

    def test_get_story_points_from_epic_returns_a_dict_containing_the_found_statuses_with_their_totals(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(0, "Reported"),
            MockedJiraIssue(1, "Investigated"),
            MockedJiraIssue(1, "Closed"),
            MockedJiraIssue(1, "Closed"),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.assertEqual({"total": 3, "Reported": 0, "Investigated": 1, "Closed": 2}, result)

    def test_if_storypoints_custom_field_is_unknown_we_get_it_first_via_the_fields_getter(self):
        # Given

        self.jira_client.fields.return_value = [
            {
                "id": "customfield_11280",
                "name": "Release Note",
                "custom": True,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["cf[11280]", "Release Note"],
                "schema": {"type": "option", "custom": "com.atlassian.jira.plugin.system.customfieldtypes:select", "customId": 11280},
            },
            {
                "id": "customfield_10333",
                "name": "Story Points",
                "custom": True,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["cf[10333]", "Story Points"],
                "schema": {"type": "number", "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float", "customId": 10333},
            },
        ]
        mocked_jira_issue = MockedJiraIssue()
        mocked_jira_issue.fields.customfield_10333 = 100
        mocked_jira_issue2 = MockedJiraIssue()
        mocked_jira_issue2.fields.customfield_10333 = 0
        self.jira_client.search_issues.return_value = [mocked_jira_issue2, mocked_jira_issue]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_storypoints_from_epic("PROJ001-001")

        # Then
        self.jira_client.fields.assert_called_once()

        self.jira_client.search_issues.assert_called_with(
            "'Epic Link' = " + "PROJ001-001", fields=["customfield_10333", "status"], maxResults=0
        )

        self.assertEqual({"total": 100, "Reported": 100}, result)

    def test_if_storypoints_can_be_retrieved_from_a_jira_issue(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        mocked_jira_issue = MockedJiraIssue(story_points=100)
        mocked_jira_issue2 = MockedJiraIssue()
        mocked_jira_epic = MockedJiraIssue()
        mocked_jira_epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [mocked_jira_issue2, mocked_jira_issue]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_storypoints_from_epic(mocked_jira_epic)

        # Then
        self.jira_client.fields.assert_called_once()

        self.jira_client.search_issues.assert_called_with(
            "'Epic Link' = " + "PROJ001-001", fields=["customfield_10282", "status"], maxResults=0
        )

        self.assertEqual({"total": 100, "Reported": 100}, result)


class TestGetIssuesInEpic(TestCase):
    def setUp(self) -> None:
        self.jira_client = Mock(spec=jira.JIRA)

    def test_get_issues_from_epic_searches_for_the_right_epic_key(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        result = jat.get_all_issues_in_epic("PROJ001-001")

        # Then
        self.assertEqual(self.jira_client.search_issues.return_value, result)
        self.jira_client.search_issues.assert_called_with("'Epic Link' = PROJ001-001", maxResults=0)

    def test_get_issues_from_epic_can_filter_on_the_fields_to_retrieve_to_reduce_data_retrieval(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.get_all_issues_in_epic("PROJ001-001", fields=["a_specific_field"])

        # Then
        self.jira_client.search_issues.assert_called_with("'Epic Link' = PROJ001-001", fields=["a_specific_field"], maxResults=0)

    def test_get_issues_from_epic_takes_a_string_field_or_a_list_of_fields(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.get_all_issues_in_epic("PROJ001-001", fields="a_specific_field")

        # Then
        self.jira_client.search_issues.assert_called_with("'Epic Link' = PROJ001-001", fields=["a_specific_field"], maxResults=0)

    def test_get_issues_from_epic_allows_to_filter_an_extra_jql_query(self):
        # Given

        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        self.jira_client.search_issues.return_value = [
            MockedJiraIssue(story_points=0),
            MockedJiraIssue(story_points=1),
            MockedJiraIssue(story_points=2),
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.get_all_issues_in_epic("PROJ001-001", fields="a_specific_field", jql_query="project in (PROJ001,PROJ002)")

        # Then
        self.jira_client.search_issues.assert_called_with(
            "'Epic Link' = PROJ001-001 AND project in (PROJ001,PROJ002)", fields=["a_specific_field"], maxResults=0
        )


class TestSetVersionNumberForAllItemsInEpic(TestCase):
    def setUp(self) -> None:
        self.jira_client = Mock(spec=jira.JIRA)

    def test_copy_fix_version_from_epic_to_all_items_in_epic(self):
        # Given
        sub_issue1 = MockedJiraIssue(story_points=0)
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic)

        # Then
        sub_issue1.add_field_value.assert_called_with("fixVersions", {"name": version1.name})

    def test_copy_fix_version_from_epic_to_all_items_in_epic_searches_for_the_epic(self):
        # Given
        sub_issue1 = MockedJiraIssue(story_points=0)
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic)

        # Then
        self.jira_client.search_issues.assert_called_with(f"'Epic Link' = {epic.key}", fields=["fixVersions"], maxResults=0)

    def test_copy_fix_version_from_epic_to_all_items_in_epic_searches_for_the_epic_and_passes_on_extra_jql_query(self):
        # Given
        sub_issue1 = MockedJiraIssue(story_points=0)
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1]
        jat = JiraAgileToolBox(self.jira_client)
        jql_query = "project in (PROJ001,PROJ002)"

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic, jql_query=jql_query)

        # Then
        self.jira_client.search_issues.assert_called_with(f"'Epic Link' = {epic.key} AND {jql_query}", fields=["fixVersions"], maxResults=0)

    def test_copy_fix_version_from_epic_to_all_items_in_epic_for_multiple_versions(self):
        # Given
        sub_issue1 = MockedJiraIssue(story_points=0)
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        version2 = Mock(spec=jira.resources.Version)
        version2.name = "JAT 0.0.10"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1, version2]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic)

        # Then
        sub_issue1.add_field_value.assert_any_call("fixVersions", {"name": version1.name})
        sub_issue1.add_field_value.assert_any_call("fixVersions", {"name": version2.name})

    def test_copy_fix_version_from_epic_to_multiple_items_in_epic(self):
        # Given
        sub_issue1 = MockedJiraIssue()
        sub_issue2 = MockedJiraIssue()
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1, sub_issue2]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic)

        # Then
        sub_issue1.add_field_value.assert_called_with("fixVersions", {"name": version1.name})
        sub_issue2.add_field_value.assert_called_with("fixVersions", {"name": version1.name})

    def test_copy_fix_version_from_epic_to_all_items_in_epic_dont_keep_already_present(self):
        # Given
        sub_issue1 = MockedJiraIssue(story_points=0)
        version1 = Mock(spec=jira.resources.Version)
        version1.name = "JAT 0.0.9"
        epic = MockedJiraIssue()
        epic.fields.fixVersions = [version1]
        epic.key = "PROJ001-001"
        self.jira_client.search_issues.return_value = [sub_issue1]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.copy_fix_version_from_epic_to_all_items_in_epic(epic, keep_already_present=False)

        # Then
        sub_issue1.update.assert_called_with(fields={"fixVersions": [{"name": version1.name}]})
