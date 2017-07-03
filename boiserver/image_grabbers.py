import requests
import sys
from .database import db_connect, tweet_table_session


#####################################################################################
# Worker that fetches the image from the tweet and stores it.
def tweet_worker(q) -> None:

    con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
    session, db_table = tweet_table_session(con, meta)

    while True:
        tweet = q.get()

        print(tweet['id'], tweet['text'], tweet['entities']['media'][0]['media_url'])
        sys.stdout.flush()

        r = requests.get(tweet['entities']['media'][0]['media_url'] + ":large", stream=True)
        if r.status_code == 200:
            clause = db_table.insert().values(tweet_id=tweet['id'], image=r.raw.read())
            con.execute(clause)

        q.task_done()

