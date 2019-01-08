import datetime
import inspect
import logging
import pandas
import pprint

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
            if 'query' in method_name:
                self.query_methods[method_name] = object


    def store_in_graph(self):
        pass

    def query_unfinished_tasks_by_snapshot(self, timestamp=None):
        """ Query for unfinished tasks """
        query = 'select timestamp,count(ref) from tasks where status_name != "Done" group by timestamp'
        rows = self.storage.query(query)
        df = pandas.DataFrame(rows, columns=rows[0].keys())
        df['timestamp'] = pandas.to_datetime(df['timestamp'],unit='s')
        print(df)

