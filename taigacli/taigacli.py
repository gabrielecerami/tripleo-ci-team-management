# - s sprint (default: current)
import argparse
import configparser
import datetime
import logging
import os
import pickle
import pprint
import sys
from taigacli.db_drivers import *
from taigacli.queries import *
from taigacli.client import TaigaClient
from taigacli.exceptions import *
from taigacli_custom_queries import *
from taigacli.commands.task import TaskCommand
from taigacli.commands.snapshots import SnapshotsCommand


class Configuration(object):

    def __init__(self, config_file):
        self.relevant_attr = {}
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.read(config_file)
        self.timestamp = datetime.datetime.now().timestamp()
        self.project_slug = parser['project']['slug']
        self.scope = parser['main']['scope']
        self.db_driver = parser['main']['db-driver']
        self.db_parameters = {}
        self.db_options = {}
        self.main_elements = parser['project']['elements'].split(',')
        for element in self.main_elements:
            self.db_parameters[element] =  parser[element+':'+self.db_driver]
        try:
            self.db_options = parser['db:' + self.db_driver]
        except KeyError:
            pass
        if self.db_driver == "influxdb":
            self.db_storage = influxdb.Storage(self)
        elif self.db_driver == "sqlite":
            self.db_storage = sqlite.Storage(self)
            self.queries = sql.Queries(self)
            try:
                self.custom_queries = custom_sql.CustomQueries(self)
            except:
                raise
        else:
            raise SnapshotException("DB driver not supported")


        self.argparser = argparse.ArgumentParser(description='Taiga Board Snapshot utility')
        self.main_subparser = self.argparser.add_subparsers()

        self.commands = []
        self.commands.append(TaskCommand(self))
        self.commands.append(SnapshotsCommand(self))

        # TODO ideas for commands/ queries
        # move unfinished issues to the next sprint
        # epics dependency graph
        # timeline for tasks by user (over the course of time, when are the status changes.)

        self.client = TaigaClient(self)

    def parse_arguments(self, arguments):
        args = self.argparser.parse_args(arguments)
        return args

def usage(config, args):
    config.parser.print_help()

def main():
    # Read conf
    log = logging.getLogger('taigacli')
    log.setLevel(logging.DEBUG)
    config_file = 'config.ini'
    config = Configuration(config_file)
    args = config.parse_arguments(sys.argv[1:])
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        config.argparser.print_help()

    return 0

if __name__ == '__main__':
    sys.exit(main())
