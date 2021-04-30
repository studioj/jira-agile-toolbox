import jira
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("package-name").version
except DistributionNotFound:
    # package is not installed
    pass


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

        epic_key = epic.key if isinstance(epic, jira.Issue) else epic

        issues_in_epic = self._jira_client.search_issues(
            "'Epic Link' = " + epic_key, fields=[self._story_points_custom_field, "status"], maxResults=0
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
        """
        helper method to find custom fields

        :param name: name of the field you want the "customxxxxx" value from
        :return:
        """
        for field in self._jira_client.fields():
            if field["name"] == name:
                return field["id"]

    def rank_issues_by_list(self, ranked_list, on_top_of_issue):
        """
        sorts the provided list by rank on top of the latter issue

        :param ranked_list: list of issues to be sorted by rank index 0 has highest rank
        :param on_top_of_issue: issue on top of which these issues need to land
        """
        reversed_list = ranked_list[::-1]
        reversed_list.insert(0, on_top_of_issue)
        for i, value in enumerate(reversed_list):
            if i < len(reversed_list) - 1:
                self._jira_client.rank(reversed_list[i + 1].key, value.key)
