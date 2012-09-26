from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from database import Base

class EventSource(Base):
    __tablename__ = 'event_sources'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(250))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Event Source: id: %d, name: %s>' % (self.id, self.name)

class EventType(Base):
    __tablename__ = 'event_types'
    __table_args__ = (UniqueConstraint('event_source_id', 'name', name='event_type_uc'), )
    id = Column(Integer, primary_key=True)
    event_source_id = Column(Integer, ForeignKey('event_sources.id'))
    name = Column(String(50))
    description = Column(String(250))
    source = relationship("EventSource", backref="event_types")

    def __init__(self, source_id, name, description):
        self.event_source_id = source_id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Event Type: id: %d>' % self.id

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    slug = Column(String, unique=True)
    event_type_id = Column(Integer, ForeignKey('event_types.id'))
    properties = Column(Text)
    type = relationship("EventType", backref="events")

    def __init__(self, time, slug, event_type_id, properties):
        self.time = time
        self.slug = slug
        self.event_type_id = event_type_id
        self.properties = properties
 
    def __repr__(self):
        return '<Event: Time: %s, Type: %s, Slug: %s, properties: %s>' % (
            self.time, self.event_type_id, self.slug, self.properties)

