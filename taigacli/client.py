import datetime
import logging
import os
import pprint
import requests
import taiga
from taigacli.exceptions import *

class TaigaClient(object):

    def __init__(self, config):
        # Taiga properties
        self.date_format = "%Y-%m-%d"
        username = os.environ.get('TAIGA_USERNAME', None)
        password = os.environ.get('TAIGA_PASSWORD', None)
        self.config = config
        if username is None or password is None:
            logging.error("Missing Credentials")
            raise SnapshotException
        try:
            self.api=taiga.TaigaAPI(self.config.taiga_host)
        except AttributeError:
            self.api=taiga.TaigaAPI()

        try:
            self.api.auth(username=username, password=password)
        except taiga.exceptions.TaigaRestException:
            logging.error("Authentication Failed")
            raise

        self.project = self.api.projects.get_by_slug(self.config.project_slug)

        self.epic_statuses = {}
        self.epic_attributes = {}
        self.task_statuses = {}
        self.task_attributes = {}
        self.user_story_attributes = {}
        self.user_story_statuses = {}

        for epic_status in self.project.epic_statuses:
            self.epic_statuses[str(epic_status['id'])] = epic_status['name']

        for epic_attribute in self.project.epic_custom_attributes:
            self.epic_attributes[str(epic_attribute['id'])] = epic_attribute['name']

        for task_status in self.project.task_statuses:
            self.task_statuses[str(task_status.id)] = task_status.name

        for task_attribute in self.project.task_custom_attributes:
            self.task_attributes[str(task_attribute['id'])] = task_attribute['name']

        for user_story_attribute in self.project.userstory_custom_attributes:
            self.user_story_attributes[str(user_story_attribute['id'])] = user_story_attribute['name']

        for user_story_status in self.project.us_statuses:
            self.user_story_statuses[str(user_story_status.id)] = user_story_status.name

        self.users = {}
        members = self.project.members
        for member in members:
            self.users[member.id] = member.username

        self.sprints = self.project.list_milestones()

    def raw_api_get(self, api_path):
        headers = {
            'Authorization': "Bearer {}".format(self.api.token)
        }
        request = "{}/api/v1/{}".format(self.api.host, api_path)
        response = requests.get(request, headers=headers)
        return response.json()

    def get_epics(self):
        api_path = "epics?project={}".format(self.project.id)
        epics = self.raw_api_get(api_path)
        return epics

    def get_sprint(self, date=datetime.datetime.today()):
        for sprint in self.sprints:
            start_date = datetime.datetime.strptime(sprint.estimated_start,
                self.date_format)
            end_date = datetime.datetime.strptime(sprint.estimated_finish,
                self.date_format).replace(hour=23, minute=59)
            logging.debug(pprint.pformat(date))
            logging.debug(pprint.pformat(start_date))
            logging.debug(pprint.pformat(end_date))
            if date <= end_date and date >= start_date:
                break
        return sprint

    def get_tasks_by_us(self, us_id=None):
        return self.api.tasks.list(user_story=us_id)
