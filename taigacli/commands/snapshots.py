import logging
from taigacli.operations.snapshot import Snapshot


class SnapshotsCommand(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.config = config
        snapshot_parser = config.main_subparser.add_parser(
            'snapshots', help='Handle local snapshots')
        snapshot_subparser = snapshot_parser.add_subparsers()
        snapshot_create_parser = snapshot_subparser.add_parser(
            'create', help='Create a snapshot of the Taiga board')
        snapshot_create_parser.add_argument(
            '--fixture', dest='fixture', action='store', help='dump snapshot to fixture file')
        snapshot_create_parser.set_defaults(handler=self.create)
        snapshot_list_parser = snapshot_subparser.add_parser(
            'list', help='list stored snapshots')
        snapshot_list_parser.set_defaults(handler=self.list)

        query_parser = snapshot_subparser.add_parser(
            'query', help='query the snapshot database')
        query_parser.set_defaults(handler=self.run_queries)
        query_parser.add_argument(
            '--raw-query', dest='raw_query', action='store', help='execute a raw SQL query on the database')
        query_parser.add_argument(
            '--name', dest='query_name', action='store', help='execute a saved query')
        query_parser.add_argument(
            '--list', dest='list_queries', action='store_true', help='list saved query')
        query_parser.add_argument(
            '--timestamp', dest='timestamp', action='store', help='specify timestamp [default: latest]')

    def list(self, args):
        self.config.queries.list_snapshots()

    def create(self, args):
        snapper = Snapshot(self.config)

        if args.fixture:
            snapper.dump_pickle()
        else:
            snapper.dump()

    def run_queries(self, args):
        queries = self.config.queries
        custom_queries = self.config.custom_queries
        if args.timestamp:
            if queries.verify_timestamp(args.timestamp):
                timestamp = args.timestamp
            else:
                self.log.error(
                    "Timestamp {} not in database".format(args.timestamp))
                return
        else:
            timestamp = queries.get_latest_timestamp()
        if args.raw_query:
            queries.raw(args.raw_query)
        elif args.query_name:
            custom_queries.user[args.query_name](timestamp=timestamp)
        elif args.list_queries:
            for index, name in enumerate(self.config.custom_queries.user.keys(), 1):
                print("{}. {}".format(index, name))
        else:
            self.log.warning("No queries specified")
