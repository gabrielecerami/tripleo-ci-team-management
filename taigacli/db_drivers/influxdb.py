import datetime
import logging
import pprint
import json

try:
    from influxdb import InfluxDBClient
except ImportError:
    logging.error("python bindings for Influxdb not installed")
    pass


class DataPoint(object):

    def __init__(self, measurement, timestamp, tags, fields):
        self.measurement = measurement
        self.timestamp = timestamp
        self.tags = tags
        self.fields = fields

    def to_dict(self):
        point_dict = {}
        point_dict['measurement'] = self.measurement
        point_dict['timestamp'] = self.timestamp
        point_dict['tags'] = self.tags
        point_dict['fields'] = self.fields

        return point_dict


class Storage(object):
    log = logging.getLogger('taigacli')

    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.datetime.now().isoformat()
        self.host = config.db_options.get('host', 'localhost')
        self.log.debug(self.host)
        self.port = config.db_options.get('port', '8086')
        self.db_name = config.db_options.get('database', 'test')
        self.client = InfluxDBClient(host=self.host, port=self.port)
        self.client.switch_database(self.db_name)
        self.points = []
        self.tags = {}
        self.fields = {}
        for element_name in self.config.main_elements:
            self.tags[element_name] = []
            self.fields[element_name] = []
            try:
                self.tags[element_name] = self.config.db_parameters[
                    element_name]['tags'].split(',')
            except KeyError:
                pass
            try:
                self.fields[element_name] = self.config.db_parameters[
                    element_name]['fields'].split(',')
            except KeyError:
                pass
        self.log.debug(pprint.pformat(self.tags))
        self.log.debug(pprint.pformat(self.fields))

    def query(self, query, date=None):
        if date is None:
            snapshots = self.client.query(
                'select * from snapshots order by desc limit 1')
        else:
            snapshots = self.client.query(
                'select * from snapshots where time < ' + date + ' order by desc limit 1')

        snapshot = snapshots.get_points()[0]
        timestamp = snapshot['time']

        results = self.client.query(query + ' AND "time" = ' + timestamp)
        rows = results.get_points()

        return rows

    def dump(self, snapshot):
        for element_name in self.config.main_elements:
            measurement = element_name
            elements_list = getattr(snapshot, element_name)
            for element in elements_list:
                tags = {}
                fields = {}
                for attribute in self.tags[element_name]:
                    try:
                        tags[attribute] = getattr(element, attribute)
                    except AttributeError:
                        self.log.warning("Attribute not found")
                for attribute in self.fields[element_name]:
                    try:
                        fields[attribute] = getattr(element, attribute)
                    except AttributeError:
                        self.log.warning("Attribute not found")

                self.points.append(
                    DataPoint(measurement, self.timestamp, tags, fields).to_dict())

        self.log.debug(pprint.pformat(self.points))
        self.client.write_points(self.points)
        snap_info = [{"measurement": "snapshots", "timestamp": self.timestamp,
                      "tags": {}, "fields": {"sprint": snapshot.current_sprint.id}}]
        self.client.write_points(snap_info)
