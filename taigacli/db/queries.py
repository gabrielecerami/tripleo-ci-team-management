import datetime
import inspect
import logging
import pandas
import pprint
import texttable
import subprocess
from taigacli.exceptions import *
from sqlalchemy import func
from taigacli.db.client import Client
from taigacli.db.models import Snapshot


class Queries(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        self.config = config
        self.client = Client(config)
        self.team = config.team
        self.custom = {}
        self.date_format = "%Y-%m-%d"

        for method_name, method in dict(methods).items():
            if 'query_' in method_name:
                self.custom[method_name] = method

    def list_user_queries(self):
        return self.user.keys()

    def store_in_graph(self):
        pass

    def get_latest_timestamp(self):
        result = self.client.session.query(func.max(Snapshot.timestamp)).one()
        return result[0]

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
        try:
            self.client.session.query(Snapshot).filter_by(timestamp = timestamp).one()
            return True
        except NoResultFound:
            return False

    def print_table(self, rows, headers=None, title=None):
        height, width = subprocess.check_output(['stty', 'size']).split()
        table = texttable.Texttable(max_width=int(width))
        content = []
        if headers:
            content += [headers]
            table.set_cols_dtype(['t'] * len(headers))
        else:
            table.set_cols_dtype(['t'] * len(rows[0]))

        content += rows
        table.add_rows(content)
        if title:
            print(title)
        print(table.draw())


    def print_query(self, results, output_type='table', title=None):
        if output_type == 'table':
            if len(results) == 0:
                return

            if hasattr(results[0], '__table__'):
                headers = [column.name for column in results[0].__table__.columns]
            elif hasattr(results[0], 'keys'):
                headers = results[0].keys()
            rows = []
            for record in results:
                row = []
                for header in headers:
                    row.append(getattr(record, header))
                rows.append(row)
        self.print_table(rows, headers=headers, title=title)
        # TODO: is pandas neeeded at all ?
        #elif output_type == 'pandas':
        #    df = pandas.DataFrame(rows, columns=rows[0].keys())
        #    pandas.set_option('display.max_colwidth', 1000)
        #    df['timestamp'] = pandas.to_datetime(df['timestamp'], unit='s')
        #    print(df)

    def list_snapshots(self):
        results = self.client.session.query(Snapshot).all()
        self.print_query(results)

    def raw(self, raw_sql, timestamp=None):
        """ Run Custom SQL Query """
        results = self.client.engine.execute(raw_sql)
        self.print_query(self.storage.query(query))
