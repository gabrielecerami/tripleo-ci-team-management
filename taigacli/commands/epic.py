import graphviz
import logging
import pprint
from taigacli.operations.snapshot import Snapshot

class EpicCommand(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.config = config
        self.client = config.client
        epic_parser = config.main_subparser.add_parser(
            'epic', help='Handle epic operations')
        epic_subparser = epic_parser.add_subparsers()
        epic_diagram_parser = epic_subparser.add_parser(
            'diagram', help='Show epic diagram')
        epic_diagram_parser.add_argument(
            'epic_ref', action='store', help='epic to show diagram')
        epic_diagram_parser.set_defaults(handler=self.draw_dep_diagram)

    def noop(self, args):
        print("Not implemented")

    def draw_dep_diagram(self, args):
        epic_ref = args.epic_ref
        snapshot = Snapshot(self.config, scope='project')
        #snapshot.dump_pickle()

        draw_epic = None
        dot = graphviz.Digraph(comment='Epic Dependency Tree')
        for epic in snapshot.epics:
            if str(epic['ref']) == epic_ref:
                draw_epic = epic
                break
        if draw_epic is None:
            self.log.error('epic %s not found', epic_ref)
            return

        epic_label = 'Epic #{}'.format(draw_epic['id'])
        dot.node(epic_label, draw_epic['subject'])

        for us in snapshot.user_stories:
            if us.id in draw_epic['user_stories']:
                dot.node('US #{}'.format(us.ref))
                if not hasattr(us, 'Dependencies'):
                    dot.edge(epic_label, 'US #{}'.format(us.ref))
                else:
                    dep_id = us.Dependencies.split('US #')[1]
                    dot.node('US #{}'.format(dep_id))
                    dot.edge('US #{}'.format(dep_id), 'US #{}'.format(us.ref))
        dot.render('graph.gv', view=True)
