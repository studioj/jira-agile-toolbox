# jira_agile_toolbox

![python package workflow](https://github.com/studioj/jira-agile-toolbox/actions/workflows/python-publish.yml/badge.svg)
![python package workflow](https://github.com/studioj/jira-agile-toolbox/actions/workflows/python-package.yml/badge.svg)

A python package which extends the jira package with agile related functionality

For more info about the jira package

- PyPi: https://pypi.org/project/jira/
- rtd:  https://jira.readthedocs.io/en/latest/

## Installation
```bash
pip install jira-agile-toolbox
```

## Documentation
https://jira-agile-toolbox.readthedocs.io/

## Features

- ### Getting story points from an epic

Example:
```python
>>> from jira_agile_toolbox import JiraAgileToolBox
>>> from jira import JIRA
>>> my_jira_client = JIRA("https://my-jira-server.com", basic_auth("MYUSERNAME","MYPASSWORD")
>>> tb = JiraAgileToolBox(my_jira_client)
>>> tb.get_storypoints_from_epic("JAT-001")
{'total': 100, "Reported": 50, "Closed": 50}
```

- ### Ranking a list of epics on top of another one

Example:
```python
>>> from jira_agile_toolbox import JiraAgileToolBox
>>> from jira import JIRA
>>> my_jira_client = JIRA("https://my-jira-server.com", basic_auth("MYUSERNAME","MYPASSWORD")
>>> tb = JiraAgileToolBox(my_jira_client)
>>> tb.rank_issues_by_list([my_jira_client.issue("JAT-001"), my_jira_client.issue("JAT-003")], my_jira_client.issue("JAT-005"))
```

will rank issues like:

| original | result |
| -------- | ------ |
| JAT-010 | JAT-010
| JAT-005 | JAT-001
| JAT-003 | JAT-003 
| JAT-002 | JAT-005
| JAT-001 | JAT-002
