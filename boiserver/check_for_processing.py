from time import sleep
from datetime import datetime
from .database import db_connect, tweet_table_session, Tweet

from . import ELAPSED_SECONDS_UNTIL_QUEUE

from sqlalchemy.sql import select


def check_for_processing() -> None:

    con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
    session, db_table = tweet_table_session(con, meta)

    while True:

        q = session.query(Tweet)
        results = q.all()

        for r in results:  # type: Tweet

            if r.queued_at is None or (datetime.now()-r.queued_at).total_seconds() > ELAPSED_SECONDS_UNTIL_QUEUE:
                print(r.tweet_id, r.queued_at)
                r.queued_at = datetime.now()

                session.add(r)
                session.flush()
                session.commit()

        sleep(10)
