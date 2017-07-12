from twython import Twython, TwythonStreamer
from time import sleep

from . import new_tweets_queue
from .database import db_connect, tweet_table_session

from threading import Lock
twython_lock = Lock()

APP_KEY = '6LTEgHCBchKPIQdXb3IH6kJSI'
APP_SECRET = 'waHGTlmTVKQmsm485tf5WPWpUShQkTecvdvwKOBB7DA8nQlnSB'

OAUTH_TOKEN = '873749293118742528-seejM0pUZqKOCQbCzIIASapBAFMIXVH'
OAUTH_TOKEN_SECRET = 'TojXnSU3lWyiWgwoikMGI9JlCSsZjWXpxHwqvayQMYKFk'


def queue_tweet(tweet):

    # Ensure there is a screenshot attached.
    if "media" in tweet["entities"] and "boiitems" != tweet["user"]["screen_name"].lower() and tweet['in_reply_to_status_id'] is None:
        new_tweets_queue.put(tweet)

connected = False


class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        queue_tweet(data)


    def on_error(self, status_code, data):
        global connected, twython_lock
        twython_lock.acquire()
        print(status_code)
        self.disconnect()
        connected = False
        twython_lock.release()


def check_tweets() -> None:
    global connected

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    twitter.verify_credentials()

    con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
    session, db_table = tweet_table_session(con, meta)

    twython_lock.acquire()
    stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    connected = True
    twython_lock.release()

    stream.statuses.filter(track='boiitems')

    # A one-time check whether or not we've missed anything since starting.
    try:
        user_timeline = twitter.get_mentions_timeline()
        for tweet in user_timeline:
            instance = session.query(db_table).filter_by(tweet_id=tweet['id']).first()
            if not instance:
                queue_tweet(tweet)
        sleep(30)
    except:
        pass

    while True:
        twython_lock.acquire()
        if not connected:
            stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            connected = True
        twython_lock.release()

        sleep(5)

