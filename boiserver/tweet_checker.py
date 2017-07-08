from twython import Twython
from time import sleep

from . import new_tweets_queue
from .database import db_connect, tweet_table_session

APP_KEY = '6LTEgHCBchKPIQdXb3IH6kJSI'
APP_SECRET = 'waHGTlmTVKQmsm485tf5WPWpUShQkTecvdvwKOBB7DA8nQlnSB'

OAUTH_TOKEN = '873749293118742528-seejM0pUZqKOCQbCzIIASapBAFMIXVH'
OAUTH_TOKEN_SECRET = 'TojXnSU3lWyiWgwoikMGI9JlCSsZjWXpxHwqvayQMYKFk'


def check_tweets() -> None:

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    twitter.verify_credentials()

    con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
    session, db_table = tweet_table_session(con, meta)

    while True:
        user_timeline = twitter.get_mentions_timeline()
        for tweet in user_timeline:
            instance = session.query(db_table).filter_by(tweet_id=tweet['id']).first()
            if not instance:
                # print("Putting in {}".format(tweet['id']))
                new_tweets_queue.put(tweet)
        sleep(15)
