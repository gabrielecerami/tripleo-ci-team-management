# - s sprint (default: current)
import argparse
import configparser
import datetime
import logging
import pprint
import sys
from taigacli.client import TaigaClient
from taigacli.exceptions import *
from taigacli_custom_queries import *
from taigacli.commands.task import TaskCommand
from taigacli.commands.snapshots import SnapshotsCommand
from taigacli.commands.epic import EpicCommand
from taigacli.commands.tools import ToolsCommand
from taigacli.db.client import Client as DBClient



class Configuration(object):

    def __init__(self, config_file):
        self.relevant_attr = {}
        parser = configparser.ConfigParser(allow_no_value=True)
        parser.read(config_file)
        self.timestamp = datetime.datetime.now().timestamp()
        self.project_slug = parser['project']['slug']
        self.scope = parser['main']['scope']
        self.team = parser['project']['team'].split(',')
        self.db_uri = parser['db']['uri']

        self.argparser = argparse.ArgumentParser(
            description='Taiga Board Snapshot utility')
        self.main_subparser = self.argparser.add_subparsers()


        self.client = TaigaClient(self)
        self.db_client = DBClient(self)

        # Commands
        self.commands = []
        self.commands.append(EpicCommand(self))
        self.commands.append(TaskCommand(self))
        self.commands.append(SnapshotsCommand(self))
        self.commands.append(ToolsCommand(self))

        # TODO ideas for commands/ queries
        # move unfinished issues to the next sprint
        # epics dependency graph
        # timeline for tasks by user (over the course of time, when are the
        # status changes.)


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
