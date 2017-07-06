from time import sleep
from datetime import datetime
from .database import db_connect, tweet_table_session, Tweet
import base64
from typing import Dict, Optional

import json

from . import ELAPSED_SECONDS_UNTIL_QUEUE


class TweetForProcessing:

    def __init__(self, tweet_id: str=Optional[None], image: str=Optional[None]):

        self.tweet_id = tweet_id
        self.image = image

    def dict(self) -> Dict:
        return {
            'tweet_id': self.tweet_id,
            'image': self.image
        }


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

                # Base64 the image and get ready to send it.
                b64_image = base64.b64encode(r.image)

                # Convert it to a jsonable form
                tfp = TweetForProcessing(r.tweet_id, b64_image)
                payload = json.dumps(tfp.dict())


                session.add(r)
                session.flush()
                session.commit()

        sleep(10)
