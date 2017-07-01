from twython import Twython
from threading import Thread
from queue import Queue
import requests
import zmq
from time import sleep
import sys

import requests
import shutil

from database import db_connect
from sqlalchemy import BigInteger, Binary, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

num_threads = 8

APP_KEY = '6LTEgHCBchKPIQdXb3IH6kJSI'
APP_SECRET = 'waHGTlmTVKQmsm485tf5WPWpUShQkTecvdvwKOBB7DA8nQlnSB'

OAUTH_TOKEN = '873749293118742528-w67TCJ7BvP3dRKtU1V6GPxZ2EwHCq0R'
OAUTH_TOKEN_SECRET = 'T7pmv0jDb1wcZj7jhZXF60EvkkNGC7wOa1O7gafdSv9cL'

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

twitter.verify_credentials()


con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
Session = sessionmaker(bind=con)
session = Session()


class Tweet(object):

    def __init__(self, tweet_id, image):
        self.tweet_id = tweet_id
        self.image = image


#####################################################################################
# Worker that fetches the image from the tweet and stores it.
def tweet_worker(q, session, db_table, con):
    while True:
        tweet = q.get()

        print(tweet['id'], tweet['text'], tweet['entities']['media'][0]['media_url'])
        sys.stdout.flush()

        r = requests.get(tweet['entities']['media'][0]['media_url'], stream=True)
        if r.status_code == 200:
            clause = db_table.insert().values(tweet_id=tweet['id'], image=r.raw.read())
            con.execute(clause)
            
        #with open("{}.jpg".format(tweet['id']), 'wb') as f:
        #    obj = session.query(Tweet).get(tweet['id'])
        #    f.write(obj.image)
        
        q.task_done()

#####################################################################################
# Setup the database
extend_existing=True
if "posts" not in meta.tables:
    extend_existing=False

print("Extend existing: {}".format(extend_existing))
db_table = Table(
    'posts', meta,
    Column('tweet_id', BigInteger, primary_key=True, autoincrement=False),
    Column('image', Binary),
    extend_existing=extend_existing
)

if not extend_existing:
    meta.create_all(con)

mapper(Tweet, db_table)

queue = Queue()


#####################################################################################
# Setup the ZeroMQ session
zmq_context = zmq.Context()
zmq_socket = context.socket(zmq.REQ)
port = "5555"
zmq_socket.connect ("tcp://localhost:%s" % port)

#####################################################################################
# Start the threads
for i in range(num_threads):
    worker = Thread(target=tweet_worker, args=(queue,session,db_table,con,zmq_socket))
    worker.setDaemon(True)
    worker.start()

queue.join()

#####################################################################################
# Keep scanning for new tweets
while True:
    user_timeline = twitter.get_mentions_timeline()
    for tweet in user_timeline:
        instance = session.query(db_table).filter_by(tweet_id=tweet['id']).first()
        if not instance:
            print("Putting in {}".format(tweet['id']))
            queue.put(tweet)
    sleep(15)

