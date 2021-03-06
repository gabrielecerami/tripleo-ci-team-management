import datetime
import logging
import pickle
import pprint
import json
from taigacli.exceptions import *
from taigacli.db.client import Client as DBClient


class Snapshot(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config, scope='sprint'):
        self.config = config
        self.client = config.client
        self.dbclient = DBClient(self.config)
        self.scope = scope
        try:
            with open('fixtures.pik', 'rb') as pickle_file:
                logging.warning(
                    "Fixture file found, loading snapshot from file")
                snapshot = pickle.load(pickle_file)
                self.tasks = snapshot['tasks']
                self.user_stories = snapshot['user_stories']
                self.epics = snapshot['epics']
                self.sprints = snapshot['sprints']
                self.users = snapshot['users']
                self.scope = snapshot['scope']
                self.timestamp = snapshot['timestamp']
                self.sprint_id = snapshot['sprint_id']
        except FileNotFoundError:
            self.pull()

    def pull(self):
        self.sprints = self.client.get_sprints()
        self.users = self.client.get_users()
        self.timestamp = datetime.datetime.now()

        if self.scope == 'sprint':
            self.epics = None
            current_sprint = self.client.get_sprint()
            self.sprint_id = current_sprint.id
            self.user_stories = self.client.get_us_by_sprint(current_sprint)
            self.tasks = []

        elif self.scope == 'project':
            self.log.info("Collecting Epics")
            self.sprint_id = None
            self.epics = self.client.get_epics()
            self.user_stories = []
            for epic in self.epics:
                epic.timestamp = self.timestamp
                self.log.info("Flattening epic #%s", epic['ref'])
                epic['status_name'] = self.client.epic_statuses[str(epic['status'])]
                epic['owner_name'] = self.client.users[epic['owner']]
                epic['assigned_to_name'] = self.client.users.get(epic['assigned_to'], "")
                epic_attributes = self.client.get_epic_attributes(epic['id'])[
                    'attributes_values'].items()
                for attribute_id, attribute_value in epic_attributes:
                    attribute_name = self.client.epic_attributes[attribute_id]
                    epic['attribute_name'] = attribute_value
                related_us = self.client.get_us_by_epic(epic['id'])
                epic['user_stories'] = list(map(lambda x:x['user_story'], related_us))
            self.log.info("Collecting User Stories")
            self.user_stories = self.client.get_user_stories()
            self.log.info("Collecting Tasks")
            self.tasks = self.client.get_tasks()
        else:
            self.log.error('unrecognized snapshot scope: %s', self.scope)
            raise SnapshotException

        for user_story in self.user_stories:
            user_story.timestamp = self.timestamp
            self.log.info("Flattening User Story #%s", user_story.ref)
            user_story.status_name = self.client.user_story_statuses[
                str(user_story.status)]
            user_story.owner_name = self.client.users[user_story.owner]
            user_story.assigned_users_names = []
            for user_id in user_story.assigned_users:
                user_story.assigned_users_names.append(
                    self.client.users[user_id])
            user_story_attributes = user_story.get_attributes()[
                'attributes_values'].items()
            for attribute_id, attribute_value in user_story_attributes:
                attribute_name = self.client.user_story_attributes[
                    attribute_id]
                setattr(user_story, attribute_name, attribute_value)
            if self.scope == 'sprint':
                self.log.info("collecting tasks for us #%s", user_story.ref)
                self.tasks += self.client.get_tasks_by_us(user_story.id)

        for task in self.tasks:
            task.timestamp = self.timestamp
            self.log.info("Flattening task #%s", task.ref)
            task.status_name = self.client.task_statuses[str(task.status)]
            task.owner_name = self.client.users[task.owner]
            task.assigned_to_name = self.client.users.get(task.assigned_to, "")
            task_attributes = task.get_attributes()[
                'attributes_values'].items()
            for attribute_id, attribute_value in task_attributes:
                attribute_name = self.client.task_attributes[attribute_id]
                setattr(task, attribute_name, attribute_value)

    def dump_pickle(self):
        # do not dump config
        snapshot = {}
        snapshot['epics'] = self.epics
        snapshot['tasks'] = self.tasks
        snapshot['user_stories'] = self.user_stories
        snapshot['sprints'] = self.sprints
        snapshot['users'] = self.users
        snapshot['scope'] = self.scope
        snapshot['timestamp'] = self.timestamp
        snapshot['sprint_id'] = self.sprint_id
        with open('fixtures.pik', 'w+b') as pickle_file:
            pickle.dump(snapshot, pickle_file)

    def dump(self):
        self.log.debug(pprint.pformat(self.__dict__))
        self.dbclient.dump_snapshot(self)
