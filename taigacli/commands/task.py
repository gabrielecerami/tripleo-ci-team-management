class TaskCommand(object):

    def __init__(self, config):
        self.config = config
        task_parser = config.main_subparser.add_parser(
            'task', help='Handle task operations')
        task_subparser = task_parser.add_subparsers()
        task_move_parser = task_subparser.add_parser(
            'move', help='move tasks between us')
        task_move_parser.add_argument(
            'task_ref', action='store', help='task to move')
        task_move_parser.add_argument(
            'us_ref', action='store', help='user story to move to')
        task_move_parser.set_defaults(handler=self.noop)

    def noop(self, args):
        print("Not implemented")
