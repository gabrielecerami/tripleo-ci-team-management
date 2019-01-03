# - s sprint (default: current)
import configparser
import datetime
import logging
import os
import pprint
import taiga
import sys
from db_drivers import *

class SnapshotException(Exception):
    pass

class Configuration(object):

    def __init__(self, config_file):
        self.relevant_attr = {}
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.read(config_file)
        self.project_slug = parser['project']['slug']
        self.scope = parser['main']['scope']
        self.db_driver = parser['main']['db-driver']
        self.db_parameters = {}
        self.db_options = {}
        self.main_elements = parser['project']['elements'].split(',')
        for element in self.main_elements:
            self.db_parameters[element] =  parser[element+':'+self.db_driver]
        try:
            self.db_options = parser['db:' + self.db_driver]
        except KeyError:
            pass


class TaigaSnapshot(object):

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
            logging.error("Authenticatio Failed")
            raise


        if config.db_driver == "influxdb":
            self.db_storage = influxdb.Storage(config)
        else:
            raise SnapshotException("DB driver not supported")


    def get_current_sprint(self):
            sprints = self.project.list_milestones()
            current_date = datetime.datetime.today()
            for sprint in sprints:
                start_date = datetime.datetime.strptime(sprint.estimated_start,
                    self.date_format)
                end_date = datetime.datetime.strptime(sprint.estimated_finish,
                    self.date_format)
                if current_date < end_date and current_date > start_date:
                    self.current_sprint = sprint
                    break

    def gather(self):
        # Find Project
        self.project = self.api.projects.get_by_slug(self.config.project_slug)

        # Gather basics
        self.task_statuses = self.project.list_task_statuses()
        self.task_attributes = self.project.list_task_attributes()
        self.user_story_attributes = self.project.list_user_story_attributes()
        self.user_story_statuses = self.project.list_user_story_statuses()

        if self.config.scope == 'sprint':
            self.get_current_sprint()

            self.user_stories = self.current_sprint.user_stories
            self.epics = set()
            self.tasks = []
            for us in self.user_stories:
                for us_epic in us.epics:
                    self.epics.add(us_epic['id'])
                self.tasks += self.api.tasks.list(user_story=us.id)


        elif self.config.scope == 'all':
            pass
            #get epics
            #user_stories = []
            #for epic in epics:
            #    use_stories + = epic.user_stories
        else:
            logging.error('unrecognized scope')
            raise

    def dump(self):
        self.db_storage.dump(self)


def main():
    # Read conf

    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.ini'
    config = Configuration(config_file)

    snapper = TaigaSnapshot(config)
    snapper.gather()
    snapper.dump()
    return 0


if __name__ == '__main__':
    sys.exit(main())
