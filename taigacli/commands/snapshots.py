import logging
from taigacli.operations.snapshot import Snapshot
from taigacli.db.queries import Queries
from taigacli_custom_queries.queries import CustomQueries


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
            '--query-args', action='append', help='pass generic argument to the query'
        )
        query_parser.add_argument(
            '--timestamp', dest='timestamp', action='store', help='specify timestamp [default: latest]')
        query_parser.add_argument(
            '--sprint-name', action='store', help='specify sprint name [default: latest]')

    def list(self, args):
        queries = Queries(self.config)
        queries.list_snapshots()

    def create(self, args):
        snapper = Snapshot(self.config)

        if args.fixture:
            snapper.dump_pickle()
        else:
            snapper.dump()

    def run_queries(self, args):
        queries = Queries(self.config)
        custom_queries = CustomQueries(self.config)
        kwargs = {}
        if args.query_args:
            for qargs in args.query_args:
                key, value = qargs.split('=')
                kwargs[key] = value


        if args.timestamp:
            if queries.verify_timestamp(args.timestamp):
                kwargs['timestamp'] = args.timestamp
            else:
                self.log.error(
                    "Timestamp {} not in database".format(args.timestamp))
                return
        else:
            if args.sprint_name:
                kwargs['timestamp'] = queries.get_latest_timestamp_on_sprint(args.sprint_name)
                if kwargs['timestamp'] is None:
                    self.log.error("No snapshots for sprint '{}'".format(args.sprint_name))
                    return
            else:
                kwargs['timestamp'] = queries.get_latest_timestamp()

        if args.raw_query:
            queries.raw(args.raw_query)
        elif args.query_name:
            custom_queries.custom[args.query_name](**kwargs)
        elif args.list_queries:
            for index, name in enumerate(custom_queries.custom.keys(), 1):
                print("{}. {}".format(index, name))
        else:
            self.log.warning("No queries specified")
