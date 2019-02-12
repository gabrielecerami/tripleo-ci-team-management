import json
from taigacli.db.queries import Queries
from taigacli.db.models import Task, UserStory
from sqlalchemy import or_, distinct, func
from operator import itemgetter

class CustomQueries(Queries):

    def query_us_completion(self, **kwargs):
        """ Returns the list of use stories that are missing critical fields
        params: None
        """

        timestamp = kwargs['timestamp']

        results = self.client.session.query(
            UserStory.ref,
            UserStory.description,
            UserStory.subject,
            UserStory.DOD,
            UserStory.Design,
            UserStory.QE,
            UserStory.assigned_users_names).\
            filter_by(timestamp = timestamp).\
            filter(or_(
                UserStory.description == None,
                UserStory.DOD == None,
                UserStory.Design == None,
                UserStory.QE == None,
                UserStory.assigned_users_names == None,
            )).all()
        self.print_query(results)

    def query_reviewable_tasks(self, **kwargs):
        ''' returns the tasks that are in Ready For Review state
        params: None

        '''
        timestamp = kwargs['timestamp']
        results = self.client.session.query(Task.ref, Task.subject, Task.Reviews).filter_by(status_name = "Ready for Review", timestamp = timestamp).all()
        self.print_query(results)

    def query_unfinished_us(self, **kwargs):
        ''' return an aggregate of user stories and tasks that are not in Done state
        params: None
        '''
        timestamp = kwargs['timestamp']

        result = self.client.session.query(
            UserStory.timestamp,
            func.count(distinct(UserStory.ref)),
            func.count(distinct(Task.ref))
        ).\
            filter(
                UserStory.timestamp == timestamp,
                UserStory.status_name != "Done",
                Task.timestamp == timestamp,
                Task.status_name != "Done"
            ).\
            one()
        rows = [result]

        self.print_table(rows,headers=['timestamp', 'unfinished us', 'unfinished tasks'])

    def query_unfinished_us_by_user(self, **kwargs):
        ''' returns the number of tasks and user stories that are not in Done state
        grouped by users
        params: user - limit to a specific user
        '''
        timestamp = kwargs['timestamp']
        users = self.team
        try:
            users = [kwargs['user']]
        except KeyError:
            users = self.team

        values = []
        for user_name in users:
            result = self.client.session.query(
                func.count(distinct(UserStory.ref)),
            ).\
                filter(
                    UserStory.timestamp == timestamp,
                    UserStory.status_name != "Done",
                    UserStory.assigned_users_names.like(["%" + user_name + "%"]),
                ).\
                one()
            unfinished_us = result[0]
            result = self.client.session.query(
                func.count(distinct(Task.ref))
            ).\
                filter(
                    Task.timestamp == timestamp,
                    Task.status_name != "Done",
                    Task.assigned_to_name.like("%" + user_name + "%")
                ).\
                one()
            unfinished_tasks = result[0]

            values.append([timestamp, user_name, unfinished_us, unfinished_tasks])
        self.print_table(values,headers=['timestamp', 'user', 'unfinished us', 'unfinished tasks'])


    #def query_unfinished_tasks_
    # by User do they have US that are not complete ?
    # How many tasks and user stories are not complete, group by team AND group by user, per week in the sprint AND at the sprint end.

    def query_assigned_us_by_user(self, **kwargs):
        ''' returns the list of assigned user stories grouped by user
        params: None
        '''
        timestamp = kwargs['timestamp']

        values = []

        result = self.client.session.query(
            func.count(distinct(UserStory.ref)),
        ).\
            filter(
                UserStory.timestamp == timestamp,
                UserStory.assigned_users_names.like([]),
            ).\
            one()
        assigned_us = result[0]
        result = self.client.session.query(
            func.count(distinct(Task.ref))
        ).\
            filter(
                Task.timestamp == timestamp,
                Task.assigned_to_name.is_(None)
            ).\
        one()

        assigned_tasks = result[0]
        values.append([timestamp, 'unassigned', assigned_us, assigned_tasks])

        for user_name in self.team:
            result = self.client.session.query(
                func.count(distinct(UserStory.ref)),
            ).\
                filter(
                    UserStory.timestamp == timestamp,
                    UserStory.assigned_users_names.like(["%" + user_name + "%"]),
                ).\
                one()
            assigned_us = result[0]
            result = self.client.session.query(
                func.count(distinct(Task.ref))
            ).\
                filter(
                    Task.timestamp == timestamp,
                    Task.assigned_to_name.like("%" + user_name + "%")
                ).\
                one()
            assigned_tasks = result[0]

            values.append([timestamp, user_name, assigned_us, assigned_tasks])

        self.print_table(sorted(values, key=itemgetter(2)),headers=['timestamp', 'user', 'assigned us', 'assigned tasks'])

    def query_stories_tasks_of_users(self, **kwargs):
        ''' returns the refIds of assigned user stories/tasks of user(s)
        params: user
        '''
        timestamp = kwargs['timestamp']
        try:
            user = kwargs['user']
            user_list = user.split(',')
        except:
            user_list = self.team

        values = []

        for user_name in user_list:
            result = self.client.session.query(
                distinct(UserStory.ref)
            ).\
                filter(
                    UserStory.timestamp == timestamp,
                    UserStory.assigned_users_names.like(["%" + user_name + "%"]),
                ).all()
            assigned_us = [ ref for ref, in result ]
            result = self.client.session.query(
                distinct(Task.ref)
            ).\
                filter(
                    Task.timestamp == timestamp,
                    Task.assigned_to_name.like("%" + user_name + "%")
                ).all()
            assigned_tasks = [ ref for ref, in result ]
            values.append([timestamp, user_name, assigned_us, assigned_tasks])

        self.print_table(values,headers=['timestamp', 'user', 'assigned us', 'assigned tasks'])

