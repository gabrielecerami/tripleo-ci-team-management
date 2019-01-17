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
from taigacli.queries import Queries
from taigacli.snapshot import TaigaSnapshot
from taigacli.exceptions import *


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
        else:
            raise SnapshotException("DB driver not supported")

    def parse_arguments(self, arguments):
        self.parser = argparse.ArgumentParser(description='Taiga Board Snapshot utility')
        self.parser.set_defaults(handler=usage)
        subparser = self.parser.add_subparsers()
        snapshot_parser = subparser.add_parser('snapshot', help='make a snapshot')
        snapshot_parser.add_argument('--list', dest='list_snapshots', action='store_true', help='list snapshots')
        snapshot_parser.set_defaults(handler=snapshots)
        query_parser = subparser.add_parser('query-snapshot', help='query the snapshot database')
        query_parser.set_defaults(handler=run_queries)
        query_parser.add_argument('--raw-query', dest='raw_query', action='store', help='execute a raw SQL query on the database')
        query_parser.add_argument('--name', dest='query_name', action='store', help='execute a saved query')
        query_parser.add_argument('--list', dest='list_queries', action='store_true', help='list saved query')
        query_parser.add_argument('--timestamp', dest='timestamp', action='store', help='specify timestamp [default: latest]')
        args = self.parser.parse_args(arguments)
        return args

def usage(config, args):
    config.parser.print_help()

def snapshots(config, args):
    if args.list_snapshots:
        queries = Queries(config)
        queries.list_snapshots()
    else:
        get_snapshot(config, args)

def get_snapshot(config, args):
    try:
        with open('fixtures.pik', 'rb') as pickle_file:
            logging.warning("Fixture file found, loading snapshot from file")
            snapper = pickle.load(pickle_file)
            timestamp = datetime.datetime.now().timestamp()
            snapper.db_storage = sqlite.Storage(config, timestamp)
    except FileNotFoundError:
        snapper = TaigaSnapshot(config)
        snapper.gather()

    ## Uncomment to create fixture
    # snapper.dump_pickle()

    snapper.dump()

def run_queries(config, args):
    queries = Queries(config)
    if args.timestamp:
        if queries.verify_timestamp(args.timestamp):
            timestamp = args.timestamp
        else:
            logging.error("Timestamp {} not in database".format(args.timestamp))
            return
    else:
        timestamp = queries.get_latest_timestamp()
    if args.raw_query:
        queries.raw(args.raw_query)
    elif args.query_name:
        queries.query_methods[args.query_name](timestamp=timestamp)
    elif args.list_queries:
        for index, name in enumerate(queries.query_methods.keys(), 1):
            print("{}. {}".format(index, name))


def main():
    # Read conf

    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.ini'
    config = Configuration(config_file)
    args = config.parse_arguments(sys.argv[1:])
    args.handler(config, args)

    return 0

if __name__ == '__main__':
    sys.exit(main())
