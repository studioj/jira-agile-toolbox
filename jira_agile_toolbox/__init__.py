__version_info__ = (0, 0, 4)
__version__ = ".".join(map(str, __version_info__))


class JiraAgileToolBox(object):
    def __init__(self, jira_client):
        """

        :param jira_client: an instance of jira.JIRA
        :type jira_client: jira.JIRA
        """
        self._jira_client = jira_client
        self._story_points_custom_field = None
        self._story_points_custom_field_name = "Story Points"

    def get_storypoints_from_epic(self, epic):
        """
        searches for the epic and returns the number of storypoints as a dict

        :param epic: the epic key or a jira Issue
        :type epic: str jira.Issue
        :return: a dictionary containing total story points
        :rtype: dict
        """
        if not self._story_points_custom_field:
            fields = self._jira_client.fields()
            for field in fields:
                if field["name"] == self._story_points_custom_field_name:
                    self._story_points_custom_field = field["id"]

        issues_in_epic = self._jira_client.search_issues(
            "'Epic Link' = " + "PROJ001-001", fields=self._story_points_custom_field, maxResults=0
        )
        sum_of_story_points = 0
        for issue in issues_in_epic:
            if issue and getattr(issue.fields, self._story_points_custom_field, None):
                sum_of_story_points += int(getattr(issue.fields, self._story_points_custom_field, 0))

        all_states = list({issue.fields.status.name for issue in issues_in_epic if issue})

        sum_of_story_points_per_state = {state: 0 for state in all_states}
        for issue in issues_in_epic:
            if issue and getattr(issue.fields, self._story_points_custom_field, None):
                sum_of_story_points_per_state[issue.fields.status.name] += int(getattr(issue.fields, self._story_points_custom_field, 0))

        sum_of_story_points_per_state["total"] = sum_of_story_points
        return sum_of_story_points_per_state
