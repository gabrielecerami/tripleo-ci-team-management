import logging
import pprint
import json
import sqlite3

class Row(object):

    def __init__(self, timestamp, table):
        self.fields = fields

        self.timestamp = timestamp
        for value in values:
            setattr(self, )


class Table(object):

    def __init__(self, name, config, connection, timestamp):
        self.name = name
        self.conn = connection
        self.timestamp = timestamp
        self.rows = []

        self.explicit_columns = config.db_parameters[self.name]['columns'].split(',')
        self.implicit_columns = ["timestamp"]
        self.columns = self.implicit_columns + self.explicit_columns
        self.quoted_columns = ['"{}"'.format(s) for s in self.columns]
        query_variables = ['?'] * len(self.columns)
        self.values_string = ','.join(query_variables)
        columns_string = ','.join(self.quoted_columns)
        create_table = 'create table if not exists {} ({})'.format(self.name, columns_string)

        self.conn.execute(create_table)

    def add_row(self, element):
        values = [self.timestamp]
        ## logging.debug("Adding row to table {}".format(self.name))
        for attribute in self.explicit_columns:
            try:
                value = getattr(element, attribute)
                if isinstance(value, list):
                    value = json.dumps(value)
            except AttributeError:
                # logging.warning("Attribute {} not found, setting empty".format(attribute))
                value = ""
            # logging.debug("Adding value {} from attribute {} to element {}".format(value, attribute, str(element)))
            values.append(value)
        self.rows.append(tuple(values))

    def commit(self):
        insert_row = 'insert into {} values ({})'.format(self.name, self.values_string)
        # logging.debug(insert_row)
        self.conn.executemany(insert_row, self.rows)
        self.conn.commit()

class Storage(object):

    def __init__(self, config):
        self.timestamp = config.timestamp
        self.config = config
        self.file=config.db_options.get('file', ':memory:')
        self.tables = {}
        if self.file == ':memory:':
            logging.warning('No db file configured, using memory, effectively making a dry run')
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row

        self.tables["snapshots"] = Table("snapshots", self.config, self.conn, self.timestamp)
        # logging.debug("snapshots" + pprint.pformat(self.tables['snapshots']))

        for element_name in self.config.main_elements:
            self.tables[element_name] = Table(element_name, self.config, self.conn, self.timestamp)

        cursor = self.conn.execute("select * from sqlite_master")
        # logging.debug(pprint.pformat(cursor.fetchall()))

    def dump(self, snapshot):
        for element_name in self.config.main_elements:
            elements_list = getattr(snapshot, element_name)
            table = self.tables[element_name]
            # logging.debug(pprint.pformat(table.__dict__))
            for element in elements_list:
                table.add_row(element)

            table.commit()

            # logging.debug(pprint.pformat(self.conn.execute("select * from {}".format(element_name)).fetchall()))

        #insert_row = "insert into snapshots values ({}, {})".format(self.timestamp, snapshot.current_sprint.id)
        #self.conn.execute(insert_row)

    def query(self, query):
        rows = self.conn.execute(query)
        return rows.fetchall()
