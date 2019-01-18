from taigacli.queries.sql import Queries


class CustomQueries(Queries):

    def query_unfinished_tasks_by_snapshot(self):
        """ Query for unfinished tasks """
        query = 'select timestamp,count(ref) from tasks where status_name != "Done" group by timestamp'
        rows = self.storage.query(query)
        self.print_query(rows, output_type='pandas')

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
