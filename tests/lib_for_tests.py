from unittest.mock import MagicMock, Mock

import jira

DEFAULT_FIELDS_RETURN_VALUE = [
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
        "id": "customfield_10282",
        "name": "Story Points",
        "custom": True,
        "orderable": True,
        "navigable": True,
        "searchable": True,
        "clauseNames": ["cf[10282]", "Story Points"],
        "schema": {"type": "number", "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float", "customId": 10282},
    },
]


class MockedJiraIssue(jira.Issue):
    def __init__(self, story_points=None, status="Reported", labels=[], fix_versions=[]):
        self.fields = MagicMock()
        self.fields.customfield_10282 = story_points
        self.fields.status.name = status
        self.fields.labels = labels
        self.fields.fixVersions = fix_versions
        self.update = Mock()
        self.__getattr__ = Mock()
        self.add_field_value = Mock()
