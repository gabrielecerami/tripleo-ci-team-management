import datetime
import inspect
import logging
import pandas
import pprint
import texttable
import subprocess
from taigacli.exceptions import *

class QueryResult(object):
    def __init__(self, result_list, measurement, fields_names, tags=None):
        self.result = result_list
        self.measurement = measurement
        self.tags = tags
        self.fields_names = fields_names

    def __str__(self):
        results_dict = dict(zip(fields_names, results))
        return pprint.pformat(results_dict)


class Queries(object):

    def __init__(self, config):
        self.storage = config.db_storage
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        self.query_methods = {}
        for method_name, object in dict(methods).items():
            if 'query_' in method_name:
                self.query_methods[method_name] = object


    def store_in_graph(self):
        pass


    def get_latest_timestamp(self):
        query = "select MAX(timestamp) from snapshots;"
        rows = self.storage.query(query)
        return rows[0]['MAX(timestamp)']

    def verify_timestamp(self, timestamp):
        query = "select timestamp from snapshots where timestamp like {};".format(timestamp)
        rows = self.storage.query(query)
        if rows:
            return True
        else:
            return False

    def print_query(self, rows, output_type='table'):
        if output_type == 'table':
            height, width = subprocess.check_output(['stty', 'size']).split()
            table = texttable.Texttable(max_width=int(width))
            headers = [rows[0].keys()]
            table.set_cols_dtype(['t'] * len(rows[0].keys()))
            table.add_rows(headers + rows)
            print(table.draw())
        elif output_type == 'pandas':
            df = pandas.DataFrame(rows, columns=rows[0].keys())
            pandas.set_option('display.max_colwidth',1000)
            df['timestamp'] = pandas.to_datetime(df['timestamp'],unit='s')
            print(df)

    def list_snapshots(self):
        query = 'select * from snapshots'
        self.print_query(self.storage.query(query))

    def raw(self, query, timestamp=None):
        """ Run Custom SQL Query """
        self.print_query(self.storage.query(query))

    def query_unfinished_tasks_by_snapshot(self):
        """ Query for unfinished tasks """
        query = 'select timestamp,count(ref) from tasks where status_name != "Done" group by timestamp'
        rows = self.storage.query(query)
        self.print_query(rows, output_type='pandas')

    def query_us_completion(self, timestamp=None):
        query = 'select ref, subject, DOD, Design, QE, assigned_users_names from user_stories where "timestamp" like {} and (DOD = "" or Design = "" or QE = "" or assigned_users_names = "[]")'.format(timestamp)
        rows = self.storage.query(query)
        self.print_query(rows)

    def query_reviewable_tasks(self, timestamp=None):
        query = 'select ref, subject, Reviews from tasks where status_name = "Ready for Review" and timestamp like {}'.format(timestamp)
        rows = self.storage.query(query)
        self.print_query(rows)
