import logging
import pickle
from taigacli.exceptions import *


class Snapshot(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config, scope='sprint'):
        self.config = config
        self.client = config.client
        self.scope = scope
        try:
            with open('fixtures.pik', 'rb') as pickle_file:
                logging.warning(
                    "Fixture file found, loading snapshot from file")
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
            self.tasks = []

        elif self.scope == 'project':
            log.info("Collecting Epics")
            project_epics = self.client.get_epics()
            self.user_stories = []
            for epic in project_epics:
                epic['status_name'] = self.client.epic_statuses[str(epic['status'])]
                epic['owner_name'] = self.client.users[epic['owner']]
                epic['assigned_to_name'] = self.client.users.get(epic('assigned_to', ""))
                # XXX custom attributes ?
                epic_attributes = self.clients.get_epic_attributes(epic['id'])[
                    'attributes_values'].items()
                for attribute_id, attribute_value in epic_attributes:
                    attribute_name = self.client.epic_attributes[attribute_id]
                    setattr(epic, attribute_name, attribute_value)
                self.log.info("Collecting user stories for epic #{}".format(epic['ref']))
                self.user_stories += self.client.get_us_by_epic(epic['id'])
        else:
            self.log.error('unrecognized scope')
            raise SnapshotException

        for user_story in self.user_stories:
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
            self.log.info("collecting tasks for us #{}".format(us.ref))
            self.tasks += self.client.get_tasks_by_us(user_story.id)

        for task in self.tasks:
            task.status_name = self.client.task_statuses[str(task.status)]
            task.owner_name = self.client.users[task.owner]
            task.assigned_to_name = self.client.users.get(task.assigned_to, "")
            task_attributes = task.get_attributes()[
                'attributes_values'].items()
            for attribute_id, attribute_value in task_attributes:
                attribute_name = self.client.task_attributes[attribute_id]
                setattr(task, attribute_name, attribute_value)

    def dump_pickle(self):
        with open('fixtures.pik', 'w+b') as pickle_file:
            pickle.dump(self, pickle_file)

    def dump(self):
        # logging.debug(pprint.pformat(self.__dict__))
        self.config.db_storage.dump(self)
