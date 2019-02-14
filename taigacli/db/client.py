import logging
from taigacli.db.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Client():
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.engine = create_engine(config.db_uri)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
        Base.metadata.create_all(self.engine)
        self.tables = Base.metadata.tables
        # useful for conversion tool
        #self.auto_base = automap_base()
        #self.auto_base.prepare(self.engine, reflect=True)
        self.model_classes = model_classes

    def dump_snapshot(self, snapshot):
        #self.auto_base = automap_base()
        #self.auto_base.prepare(self.engine, reflect=True)
        for model_class in self.model_classes:
            table_name = model_class.__table__.name
            self.log.debug(table_name)
            if table_name == 'snapshots':
                db_snapshot = model_class()
                db_snapshot.timestamp = snapshot.timestamp
                db_snapshot.sprint_id = snapshot.sprint_id
                db_snapshot.scope = snapshot.scope
                instance = self.session.query(model_class).filter_by(timestamp = db_element.timestamp).one_or_none()
                if not instance:
                    self.log.debug('%s id %d added to db', str(model_class), db_element.timestamp)
                    self.session.add(db_snapshot)
            else:
                category = getattr(snapshot, table_name)
                for element in category:
                    db_element = model_class()
                    for column in model_class.__table__.columns:
                        value = None
                        try:
                            value = getattr(element, column.name)
                        except AttributeError:
                            try:
                                value = element[column.name]
                            except (KeyError, TypeError):
                                self.log.warning("%s - %s: value for %s not found, assuming NULL", table_name, str(element), column.name)

                        setattr(db_element, column.name, value)

                    if hasattr(db_element, 'timestamp'):
                        instance = self.session.query(model_class).filter_by(timestamp = db_element.timestamp, id = db_element.id).one_or_none()
                    else:
                        instance = self.session.query(model_class).filter_by(id = db_element.id).one_or_none()
                    if not instance:
                        self.log.debug('%s id %d added to db', str(model_class), db_element.id)
                        self.session.add(db_element)
                    else:
                        self.log.debug('%s id %d exists', str(model_class), db_element.id)

        self.session.commit()

