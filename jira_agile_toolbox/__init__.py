__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))


class JiraAgileToolBox(object):
    def __init__(self, jira_client):
        """

        :param jira_client: an instance of jira.JIRA
        :type jira_client: jira.JIRA
        """
        self._jira_client = jira_client

    def get_storypoints_from_epic(self, epic):
        """
        searches for the epic and returns the number of storypoints as a dict

        :param epic: the epic key or a jira Issue
        :type epic: str jira.Issue
        :return: a dictionary containing total story points
        :rtype: dict
        """
        issues_in_epic = self._jira_client.search_issues("'Epic Link' = " + "PROJ001-001", fields="customfield_10282", maxResults=0)
        sum_of_story_points = sum(
            int(issue.fields.customfield_10282) for issue in issues_in_epic if issue and issue.fields.customfield_10282
        )
        all_states = list({issue.fields.status.name for issue in issues_in_epic if issue})

        sum_of_story_points_per_state = {state: 0 for state in all_states}
        for issue in issues_in_epic:
            if issue and issue.fields.customfield_10282:
                sum_of_story_points_per_state[issue.fields.status.name] += issue.fields.customfield_10282

        sum_of_story_points_per_state["total"] = sum_of_story_points
        return sum_of_story_points_per_state
