__version_info__ = (0, 0, 5)
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
            self._story_points_custom_field = self.get_custom_field_from_name(self._story_points_custom_field_name)

        issues_in_epic = self._jira_client.search_issues(
            "'Epic Link' = " + epic, fields=[self._story_points_custom_field, "status"], maxResults=0
        )
        sum_of_story_points = sum(
            int(getattr(issue.fields, self._story_points_custom_field, 0))
            for issue in issues_in_epic
            if issue and getattr(issue.fields, self._story_points_custom_field, None)
        )

        all_states = list({issue.fields.status.name for issue in issues_in_epic if issue})

        sum_of_story_points_per_state = {state: 0 for state in all_states}
        for issue in issues_in_epic:
            if issue and getattr(issue.fields, self._story_points_custom_field, None):
                sum_of_story_points_per_state[issue.fields.status.name] += int(getattr(issue.fields, self._story_points_custom_field, 0))

        sum_of_story_points_per_state["total"] = sum_of_story_points
        return sum_of_story_points_per_state

    def get_custom_field_from_name(self, name):
        for field in self._jira_client.fields():
            if field["name"] == name:
                return field["id"]
