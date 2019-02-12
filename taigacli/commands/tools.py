import datetime
import logging
import sqlite3
import pprint
import sqlalchemy
from taigacli.db.models import *

class ToolsCommand(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.config = config
        self.db_client = config.db_client
        tools_parser = config.main_subparser.add_parser(
            'tools', help='Handle tools operations')
        tools_subparser = tools_parser.add_subparsers()
        tools_convert_parser = tools_subparser.add_parser(
            'convert', help='convert db files to sqlalchemy format')
        tools_convert_parser.add_argument(
            'old_db', action='store', help='path to old db file')
        tools_convert_parser.set_defaults(handler=self.convert)

    def convert(self, args):

        self.conn = sqlite3.connect(args.old_db)
        self.conn.row_factory = sqlite3.Row

        query = "select * from snapshots;"
        rows = self.conn.execute(query).fetchall()

        for row in rows:
            snapshot = Snapshot()
            snapshot.timestamp = datetime.datetime.fromtimestamp(row['timestamp'])
            snapshot.sprint_id = row['id']
            snapshot.scope = 'sprint'
            self.db_client.session.add(snapshot)
            try:
                self.db_client.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                self.db_client.session.rollback()
                self.log.error(e)

        query = "select * from tasks;"
        rows = self.conn.execute(query).fetchall()
        for row in rows:
            task = Task()
            task.timestamp = datetime.datetime.fromtimestamp(row['timestamp'])
            task.id = row["id"]
            task.ref = row["ref"]
            task.assigned_to = row["assigned_to"]
            task.assigned_to_name = row["assigned_to_name"]
            task.is_blocked = row["is_blocked"]
            task.is_closed = row["is_closed"]
            task.owner = row["owner"]
            task.owner_name = row["owner_name"]
            task.subject = row["subject"]
            task.tags = row["tags"]
            task.QE = row["QE"]
            task.Reviews = row["Reviews"]
            task.test_req = row["Test Req"]
            task.status_name = row["status_name"]
            self.db_client.session.add(task)
            try:
                self.db_client.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                self.db_client.session.rollback()
                self.log.error(e)


        query = "select * from user_stories;"
        rows = self.conn.execute(query).fetchall()
        for row in rows:
            us = UserStory()
            us.timestamp = datetime.datetime.fromtimestamp(row['timestamp'])
            us.id = row["id"]
            us.ref = row["ref"]
            us.assigned_to = row["assigned_to"]
            us.owner = row["owner"]
            us.owner_name = row["owner_name"]
            us.tags = row["tags"]
            us.assigned_users = row["assigned_users"]
            us.assigned_users_names = row["assigned_users_names"]
            us.is_blocked = row["is_blocked"]
            us.is_closed = row["is_closed"]
            us.subject = row["subject"]
            us.QE = row["QE"]
            us.DOD = row["DOD"]
            us.Design = row["Design"]
            us.Dependencies = row["Dependencies"]
            us.status = row["status"]
            us.status_name = row["status_name"]
            self.db_client.session.add(us)
            try:
                self.db_client.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                self.db_client.session.rollback()
                self.log.error(e)





