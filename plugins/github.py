from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import requests
import sspps
import logging
import json
import datetime

import models
from database import db_session
from eventloop import dispatcher

class GhPlugin(sspps.Plugin):
    def __init__(self):
        self.event_types = {}

    def activate(self):
        self.init_source()
        dispatcher.add_timer(1, self.check_gh)

    def event_type(self, type_str):
        try:
            return self.event_types[type_str]
        except KeyError:
            pass
        try:
            ev_t = models.EventType(self.source.id, type_str, '')
            db_session.add(ev_t)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        self.event_types[type_str] = models.EventType.query.filter(
            models.EventType.event_source_id==self.source.id).filter(
            models.EventType.name==type_str).one()
        return self.event_types[type_str]

    def init_source(self):
        try:
            self.source = models.EventSource('github', 'Github.com')
            db_session.add(self.source)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        self.source = models.EventSource.query.filter(
            models.EventSource.name=='github').one()

    def process_event(self, event):
        try:
            cur_event = models.Event.query.filter(
                models.Event.slug==event['id']).filter(
                models.Event.event_type_id==self.event_type(event['type']).id).one()
        except NoResultFound:
            date = datetime.datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ') # 2012-09-16T19:39:37Z
            slug = event['id']
            try:
                ev = models.Event(date, event['id'], self.event_type(event['type']).id, json.dumps(event))
                db_session.add(ev)
                db_session.commit()
            except IntegrityError:
                db_session.rollback()
                logging.error("Could not insert event %s" % ev)

    def process_response(self, resp_txt):
        resp = json.loads(resp_txt)
        for event in resp:
            self.process_event(event)
        print models.Event.query.all()

    def check_gh(self):
        logging.debug('Checking github')
        s = requests.session()
        r = s.get('https://api.github.com/users/greghaynes/events')
        logging.debug('Got status code %d from github' % r.status_code)
        if r.status_code == 200:
            self.process_response(r.text)
        dispatcher.add_timer(1, self.check_gh)

