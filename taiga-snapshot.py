# - s sprint (default: current)
import argparse
import configparser
import datetime
import logging
import os
import pickle
import pprint
import taiga
import sys
from db_drivers import *
from queries import Queries

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
        if self.db_driver == "influxdb":
            self.db_storage = influxdb.Storage(self)
        elif self.db_driver == "sqlite":
            self.db_storage = sqlite.Storage(self, 12334)
        else:
            raise SnapshotException("DB driver not supported")

    def parse_arguments(self, arguments):
        self.parser = argparse.ArgumentParser(description='Taiga Board Snapshot utility')
        subparser = self.parser.add_subparsers()
        snapshot_parser = subparser.add_parser('snapshot', help='make a snapshot')
        snapshot_parser.set_defaults(handler=get_snapshot)
        query_parser = subparser.add_parser('query', help='query the snapshot database')
        query_parser.set_defaults(handler=run_queries)
        args = self.parser.parse_args(arguments)
        return args



class TaigaSnapshot(object):

    def __init__(self, config, db_storage):
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

        self.project = self.api.projects.get_by_slug(self.config.project_slug)

        self.task_statuses = {}
        self.task_attributes = {}
        self.user_story_attributes = {}
        self.user_story_statuses = {}

        task_statuses_objects = self.project.list_task_statuses()
        for task_status in task_statuses_objects:
            self.task_statuses[str(task_status.id)] = task_status.name

        task_attributes_objects = self.project.list_task_attributes()
        for task_attribute in task_attributes_objects:
            self.task_attributes[str(task_attribute.id)] = task_attribute.name

        user_story_attributes_objects = self.project.list_user_story_attributes()
        for user_story_attribute in user_story_attributes_objects:
            self.user_story_attributes[str(user_story_attribute.id)] = user_story_attribute.name

        user_story_statuses_objects = self.project.list_user_story_statuses()
        for user_story_status in user_story_statuses_objects:
            self.user_story_statuses[str(user_story_status.id)] = user_story_status.name

        self.users = {}
        members = self.project.members
        for member in members:
            self.users[member.id] = member.username


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

        # Gather basics
        if self.config.scope == 'sprint':
            self.get_current_sprint()
            self.current_sprint.scope = "sprint"
            self.snapshots = [self.current_sprint]

            self.user_stories = self.current_sprint.user_stories
            self.epics = set()
            self.tasks = []
            for us in self.user_stories:
                #us.update(us.get_attributes()['attributes_values'])
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
            raise SnapshotException

        for user_story in self.user_stories:
            user_story.status_name = self.user_story_statuses[str(user_story.status)]
            user_story.owner_name = self.users[user_story.owner]
            user_story.assigned_users_names = []
            for user_id in user_story.assigned_users:
                user_story.assigned_users_names.append(self.users[user_id])
            user_story_attributes = user_story.get_attributes()['attributes_values'].items()
            for attribute_id, attribute_value in user_story_attributes:
                attribute_name = self.user_story_attributes[attribute_id]
                setattr(user_story, attribute_name, attribute_value)

        for task in self.tasks:
            task.status_name = self.task_statuses[str(task.status)]
            task.owner_name = self.users[task.owner]
            task.assigned_to_name = self.users.get(task.assigned_to, "")
            task_attributes = task.get_attributes()['attributes_values'].items()
            for attribute_id, attribute_value in task_attributes:
                attribute_name = self.task_attributes[attribute_id]
                setattr(task, attribute_name, attribute_value)


    def dump_pickle(self):
        with open('fixtures.pik', 'w+b') as pickle_file:
            pickle.dump(self, pickle_file)

    def dump(self):
        #logging.debug(pprint.pformat(self.__dict__))
        self.db_storage.dump(self)


def get_snapshot(config, args):
    try:
        with open('fixtures.pik', 'rb') as pickle_file:
            logging.warning("Fixture file found, loading snapshot from file")
            snapper = pickle.load(pickle_file)
            timestamp = datetime.datetime.now().timestamp()
            snapper.db_storage = sqlite.Storage(config, timestamp)
    except FileNotFoundError:
        snapper = TaigaSnapshot(config, db_storage)
        snapper.gather()

    ## Uncomment to create fixture
    # snapper.dump_pickle()

    snapper.dump()

def run_queries(config, args):
    queries = Queries(config)
    queries.query_methods['query_unfinished_tasks_by_snapshot']()

def main():
    # Read conf

    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.ini'
    config = Configuration(config_file)
    args = config.parse_arguments(sys.argv[1:])
    args.handler(config, args)

    return 0

if __name__ == '__main__':
    sys.exit(main())
