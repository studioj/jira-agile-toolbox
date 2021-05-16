import jira
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("package-name").version
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"


class JiraAgileToolBox(object):
    """
    a class which helps you do agile things with jira

    :param jira_client: an instance of jira.JIRA
    :type jira_client: jira.JIRA


    ``Example``

        .. code-block:: python

            >>> from jira import JIRA
            >>> jira_client = JIRA("https://jira.atlassian.org")
            >>> jat = JiraAgileToolBox(jira_client)

    """

    def __init__(self, jira_client):
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

        ``Example``

            .. code-block:: python

                >>> from jira_agile_toolbox import JiraAgileToolBox
                >>> from jira import JIRA
                >>> my_jira_client = JIRA("https://my-jira-server.com", basic_auth("MYUSERNAME","MYPASSWORD")
                >>> tb = JiraAgileToolBox(my_jira_client)
                >>> tb.get_storypoints_from_epic("JAT-001")
                {'total': 100, "Reported": 50, "Closed": 50}

        """
        if not self._story_points_custom_field:
            self._story_points_custom_field = self._get_custom_field_from_name(self._story_points_custom_field_name)

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

    def _get_custom_field_from_name(self, name):
        """
        helper method to find custom fields

        :param name: name of the field you want the "customxxxxx" value from
        """
        for field in self._jira_client.fields():
            if field["name"] == name:
                return field["id"]

    def rank_issues_by_list(self, ranked_list, on_top_of_issue):
        """
        sorts the provided list by rank on top of the latter issue

        :param ranked_list: list of issues to be sorted by rank index 0 has highest rank
        :param on_top_of_issue: issue on top of which these issues need to land


        ``Example``

            .. code-block:: python

                >>> from jira_agile_toolbox import JiraAgileToolBox
                >>> from jira import JIRA
                >>> my_jira_client = JIRA("https://my-jira-server.com", basic_auth("MYUSERNAME","MYPASSWORD")
                >>> tb = JiraAgileToolBox(my_jira_client)
                >>> tb.rank_issues_by_list([my_jira_client.issue("JAT-001"), my_jira_client.issue("JAT-003")], my_jira_client.issue("JAT-005"))

        will rank issues like:

        =======     =======
         before      after
        =======     =======
        JAT-010     JAT-010
        JAT-005     JAT-001
        JAT-003     JAT-003
        JAT-002     JAT-005
        JAT-001     JAT-002
        =======     =======

        """
        reversed_list = ranked_list[::-1]
        reversed_list.insert(0, on_top_of_issue)
        for i, value in enumerate(reversed_list):
            if i < len(reversed_list) - 1:
                self._jira_client.rank(reversed_list[i + 1].key, value.key)

    def rank_issues_at_top_of_project(self, ranked_list, project):
        """
        moves the provided ranked_list at the top of the backlog of the given project

        :param ranked_list: a list of jira Issues
        :param project: project key
        :type project: str

        ``Example``

            .. code-block:: python

                >>> from jira_agile_toolbox import JiraAgileToolBox
                >>> from jira import JIRA
                >>> my_jira_client = JIRA("https://my-jira-server.com", basic_auth("MYUSERNAME","MYPASSWORD")
                >>> tb = JiraAgileToolBox(my_jira_client)
                >>> tb.rank_issues_by_list([my_jira_client.issue("JAT-001"), my_jira_client.issue("JAT-003")])

        will produce following result

        =======     =======
         before      after
        =======     =======
        JAT-010     JAT-001
        JAT-005     JAT-003
        JAT-003     JAT-010
        JAT-002     JAT-005
        JAT-001     JAT-002
        =======     =======

        """
        issues_sorted_on_rank = self._jira_client.search_issues(f"project = { project } ORDER BY Rank ASC", fields="key", maxResults=1000)
        for issue in issues_sorted_on_rank:
            if issue not in ranked_list:
                self.rank_issues_by_list(ranked_list, issue)
                break
