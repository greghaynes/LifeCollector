from sspps import PluginLoader
import database
import eventloop
import logging

def init_db():
    print 'initializing database...',
    import models
    database.Base.metadata.create_all(bind=database.engine)
    print 'done'

def main():
    pl = PluginLoader('plugins')
    pl.load_all()
    eventloop.dispatcher.loop_forever()

if __name__ == '__main__':
    main()
