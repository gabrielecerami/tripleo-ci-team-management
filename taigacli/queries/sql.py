import datetime
import inspect
import logging
import pandas
import pprint
import texttable
import subprocess
from taigacli.exceptions import *


class Queries(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.storage = config.db_storage
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        self.team = config.team
        self.user = {}
        self.date_format = "%Y-%m-%d"

        for method_name, method in dict(methods).items():
            if 'query_' in method_name:
                self.user[method_name] = method

    def list_user_queries(self):
        return self.user.keys()

    def store_in_graph(self):
        pass

    def get_latest_timestamp(self):
        query = "select MAX(timestamp) from snapshots;"
        rows = self.storage.query(query)
        return rows[0]['MAX(timestamp)']

    def get_latest_timestamp_on_sprint(self, sprint_name):
        query = "select estimated_finish from sprints where name = '{}'".format(sprint_name)
        rows = self.storage.query(query)
        estimated_finish = rows[0]['estimated_finish']
        end_date = datetime.datetime.strptime(sprint.estimated_finish,
                                                self.date_format).replace(hour=23, minute=59)
        end_timestamp = end_date.timestamp()
        query = "select MAX(timestamp) from snapshots where timestamp < {}".format(end_timestamp)
        rows = self.storage.query(query)
        return rows['0']['MAX(timestamp)']


    def verify_timestamp(self, timestamp):
        query = "select timestamp from snapshots where timestamp like {};".format(
            timestamp)
        rows = self.storage.query(query)
        if rows:
            return True
        else:
            return False

    def print_query(self, rows, output_type='table', headers=None):
        if output_type == 'table':
            height, width = subprocess.check_output(['stty', 'size']).split()
            table = texttable.Texttable(max_width=int(width))
            if headers == None:
                headers = rows[0].keys()
            table.set_cols_dtype(['t'] * len(headers))
            table.add_rows([headers] + rows)
            print(table.draw())
        elif output_type == 'pandas':
            df = pandas.DataFrame(rows, columns=rows[0].keys())
            pandas.set_option('display.max_colwidth', 1000)
            df['timestamp'] = pandas.to_datetime(df['timestamp'], unit='s')
            print(df)

    def list_snapshots(self):
        query = 'select * from snapshots'
        rows = self.storage.query(query)
        if len(rows) > 0:
            self.print_query(rows)

    def raw(self, query, timestamp=None):
        """ Run Custom SQL Query """
        self.print_query(self.storage.query(query))
