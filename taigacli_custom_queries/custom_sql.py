import json
from taigacli.queries.sql import Queries


class CustomQueries(Queries):

    def query_unfinished_tasks_team_eosprint(self, timestamp=None):
        """ Query for unfinished tasks """
        query = 'select timestamp,count(ref) from tasks where status_name != "Done" group by timestamp'
        rows = self.storage.query(query)
        self.print_query(rows, output_type='pandas')

    def query_unfinished_tasks_user_eosprint(self, timestamp=None):
        """ Query for unfinished tasks """
        query1 = ('select timestamp,ref, assigned_users_names'
                 ' from user_stories'
                 ' where status_name != "Done"'
                 )

        query1_rows = self.storage.query(query1)
        query2_rows = self.storage.query(query2)

        rows = []
        rows.append(query_rows[0])
        for index, row in enumerate(query_rows[1:], 1):
            print(row['ref'],row['assigned_users_names'])
            try:
                users = json.loads(row['assigned_users_names'])
            except json.decoder.JSONDecodeError:
                users = [""]
            for user in users:
                query2 = ('select timestamp,ref, assigned_to_name'
                        ' from user_stories'
                        ' where status_name != "Done"'
                        ' and assigned_to_name like {}'.format(user)
                        )
                query2_rows = self.storage.query(query2)
                rows.append((float(row['timestamp']),
                             row['ref'],
                             user
                            ))

        self.print_query(rows)

    def query_us_completion(self, timestamp=None):
        query = 'select ref, subject, DOD, Design, QE, assigned_users_names from user_stories where "timestamp" like {} and (DOD = "" or Design = "" or QE = "" or assigned_users_names = "[]")'.format(
            timestamp)
        rows = self.storage.query(query)
        self.print_query(rows)

    def query_reviewable_tasks(self, timestamp=None):
        query = 'select ref, subject, Reviews from tasks where status_name = "Ready for Review" and timestamp like {}'.format(
            timestamp)
        rows = self.storage.query(query)
        self.print_query(rows)

    def query_unfinished_us(self, timestamp=None):
        timestamp = self.get_latest_timestamp()
        sprint_name = None
        args = {}
        if 'timestamp' in args:
            timestamp = args['timestamp']
        if 'sprint-name' in args:
            sprint_name = args['sprint-name']
            self.get_latest_timestamp_on_sprint(sprint_name)

        query = 'select COUNT(distinct(ref)) as unfinished_us from user_stories where timestamp like {} and status_name != "Done"'.format(timestamp)
        rows = self.storage.query(query)
        unfinished_us = rows[0]['unfinished_us']
        query = 'select COUNT(distinct(ref)) as unfinished_tasks from tasks where timestamp like {} and status_name != "Done"'.format(timestamp)
        rows = self.storage.query(query)
        unfinished_tasks = rows[0]['unfinished_tasks']
        values = [[timestamp, unfinished_us, unfinished_tasks]]

        self.print_query(values,headers=['timestamp', 'unfinished us', 'unfinished tasks'])

    def query_unfinished_us_by_user(self, timestamp=None):
        timestamp = self.get_latest_timestamp()
        sprint_name = None
        args = {}
        if 'timestamp' in args:
            timestamp = args['timestamp']
        if 'sprint-name' in args:
            sprint_name = args['sprint-name']
            self.get_latest_timestamp_on_sprint(sprint_name)

        values = []
        for user_name in self.team:
            query = 'select COUNT(distinct(ref)) as unfinished_us from user_stories where timestamp like {} and status_name != "Done" and assigned_users_names like "%{}%"'.format(timestamp, user_name)
            rows = self.storage.query(query)
            unfinished_us = rows[0]['unfinished_us']
            query = 'select COUNT(distinct(ref)) as unfinished_tasks from tasks where timestamp like {} and status_name != "Done" and assigned_to_name like "%{}%"'.format(timestamp, user_name)
            rows = self.storage.query(query)
            unfinished_tasks = rows[0]['unfinished_tasks']

            if int(unfinished_us) != 0 or int(unfinished_tasks) != 0:
                values.append([timestamp, user_name, unfinished_us, unfinished_tasks])

        self.print_query(values,headers=['timestamp', 'user', 'unfinished us', 'unfinished tasks'])

    #def query_unfinished_tasks_
    # by User do they have US that are not complete ?
    # How many tasks and user stories are not complete, group by team AND group by user, per week in the sprint AND at the sprint end.
