from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import requests
import json

from lcplugin import LifeCollectorPlugin
from eventloop import dispatcher
from database import db_session
import models
import datetime

class LastFmPlugin(LifeCollectorPlugin):
    urls = {
        'recent_tracks': 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=greghaynes&api_key=b36a99c948dc0b2cc53bb8e28a9d9a65&format=json',
    }

    def __init__(self):
        super(LastFmPlugin, self).__init__()

    def activate(self):
        dispatcher.add_timer(0, self.check_lastfm)

    def check_lastfm(self):
        s = requests.session()
        r = s.get(LastFmPlugin.urls['recent_tracks'])
        resp = json.loads(r.text)
        tracks = resp['recenttracks']['track']
        ev_src = self.event_source('lastfm', 'Last.fm')
        ev_type = self.event_type(ev_src, 'TrackPlayed')
        for track in tracks:
            try:
                slug = track['date']['uts'] + track['mbid']
            except KeyError:
                continue

            ev = models.Event(datetime.datetime.utcfromtimestamp(
                    int(track['date']['uts'])), 
                slug, ev_type.id, json.dumps(track))
            try:
                db_session.add(ev)
                db_session.commit()
            except IntegrityError:
                db_session.rollback()
        dispatcher.add_timer(10, self.check_lastfm)

