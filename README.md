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

## Features

- ### Getting story points from an epic

Example:
```python
>>> from jira_agile_toolbox import JiraAgileToolBox
>>> from jira import JIRA
>>> my_jira_client = JIRA("https://my-jira-server.com", basicauth("MYUSERNAME","MYPASSWORD")
>>> tb = JiraAgileToolBox(my_jira_client)
>>> tb.get_storypoints_from_epic("PROJ-001")
{'total': 100, "Reported": 50, "Closed": 50}



