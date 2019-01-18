import datetime
import logging
import pickle
import pprint
from taigacli.exceptions import *

class Snapshot(object):

    def __init__(self, config, scope='sprint'):
        self.config = config
        self.client = config.client
        self.scope = scope
        try:
            with open('fixtures.pik', 'rb') as pickle_file:
                logging.warning("Fixture file found, loading snapshot from file")
                snapshot = pickle.load(pickle_file)
                self.tasks = snapshot.tasks
                self.user_stories = snapshot.user_stories
        except FileNotFoundError:
            self.pull()

    def pull(self):
        if self.scope == 'sprint':
            current_sprint = self.client.get_sprint()
            current_sprint.scope = "sprint"
            self.snapshots = [current_sprint]

            self.user_stories = current_sprint.user_stories
            self.epics = set()
            self.tasks = []
            for us in self.user_stories:
                #us.update(us.get_attributes()['attributes_values'])
                for us_epic in us.epics:
                    self.epics.add(us_epic['id'])
                self.tasks += self.client.get_tasks_by_us(us.id)

        elif self.scope == 'all':
            pass
            #get epics
            #user_stories = []
            #for epic in epics:
            #    use_stories + = epic.user_stories
        else:
            logging.error('unrecognized scope')
            raise SnapshotException

        for user_story in self.user_stories:
            user_story.status_name = self.client.user_story_statuses[str(user_story.status)]
            user_story.owner_name = self.client.users[user_story.owner]
            user_story.assigned_users_names = []
            for user_id in user_story.assigned_users:
                user_story.assigned_users_names.append(self.client.users[user_id])
            user_story_attributes = user_story.get_attributes()['attributes_values'].items()
            for attribute_id, attribute_value in user_story_attributes:
                attribute_name = self.client.user_story_attributes[attribute_id]
                setattr(user_story, attribute_name, attribute_value)

        for task in self.tasks:
            task.status_name = self.client.task_statuses[str(task.status)]
            task.owner_name = self.client.users[task.owner]
            task.assigned_to_name = self.client.users.get(task.assigned_to, "")
            task_attributes = task.get_attributes()['attributes_values'].items()
            for attribute_id, attribute_value in task_attributes:
                attribute_name = self.client.task_attributes[attribute_id]
                setattr(task, attribute_name, attribute_value)

    def dump_pickle(self):
        with open('fixtures.pik', 'w+b') as pickle_file:
            pickle.dump(self, pickle_file)

    def dump(self):
        #logging.debug(pprint.pformat(self.__dict__))
        self.config.db_storage.dump(self)

