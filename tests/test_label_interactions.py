import unittest
from unittest.mock import Mock, call

import jira

from jira_agile_toolbox import JiraAgileToolBox
from lib_for_tests import MockedJiraIssue, DEFAULT_FIELDS_RETURN_VALUE


class TestLabelSettingForSubItemsOfAnEpic(unittest.TestCase):
    def setUp(self) -> None:
        self.jira_client = Mock(spec=jira.JIRA)

    def test_setting_a_label_for_all_sub_items(self):
        # Given
        sub_story = MockedJiraIssue()
        self.jira_client.search_issues.return_value = [
            sub_story,
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.add_labels_to_all_sub_items_of_epic("PROJ001-001", ["label_to_set"])

        # Then
        sub_story.add_field_value.assert_called_with("labels", "label_to_set")

    def test_setting_a_label_for_all_sub_items_multiple_labels(self):
        # Given
        sub_story = MockedJiraIssue()
        self.jira_client.search_issues.return_value = [
            sub_story,
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.add_labels_to_all_sub_items_of_epic("PROJ001-001", ["label_to_set", "label2"])

        # Then
        sub_story.add_field_value.assert_any_call("labels", "label_to_set")
        sub_story.add_field_value.assert_any_call("labels", "label2")

    def test_setting_a_label_for_all_sub_items_raises_an_exception_on_a_label_with_a_space(self):
        # Given
        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        sub_story = MockedJiraIssue(labels=["some_other_label"])
        self.jira_client.search_issues.return_value = [
            sub_story,
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        self.assertRaisesRegex(
            ValueError, "no spaces are allowed in labels", jat.add_labels_to_all_sub_items_of_epic, "PROJ001-001", ["label_to set"]
        )
        sub_story.update.assert_not_called()

    def test_setting_a_label_for_all_sub_items_retrieves_only_the_label_fields(self):
        # Given
        self.jira_client.fields.return_value = DEFAULT_FIELDS_RETURN_VALUE
        sub_story = MockedJiraIssue()
        self.jira_client.search_issues.return_value = [
            sub_story,
        ]
        jat = JiraAgileToolBox(self.jira_client)

        # When
        jat.add_labels_to_all_sub_items_of_epic("PROJ001-001", ["label_to_set"])

        # Then
        self.jira_client.search_issues.assert_called_with(f"'Epic Link' = PROJ001-001", fields=["labels"], maxResults=0)


if __name__ == "__main__":
    unittest.main()
