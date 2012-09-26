from sqlalchemy.exc import IntegrityError

import sspps
from database import db_session
import models

class LifeCollectorPlugin(sspps.Plugin):
    def __init__(self):
        self.event_types = {}
        self.sources = {}

    def event_type(self, source, type_str):
        try:
            return self.event_types[type_str]
        except KeyError:
            pass
        try:
            ev_t = models.EventType(source.id, type_str, '')
            db_session.add(ev_t)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        self.event_types[type_str] = models.EventType.query.filter(
            models.EventType.event_source_id==source.id).filter(
            models.EventType.name==type_str).one()
        return self.event_types[type_str]

    def event_source(self, source_str, description=''):
        try:
            return self.sources[source_str]
        except KeyError:
            pass
        try:
            ev_src = models.EventSource(source_str, description)
            db_session.add(ev_src)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        self.sources[source_str] = models.EventSource.query.filter(
            models.EventSource.name==source_str).one()
        return self.sources[source_str]

