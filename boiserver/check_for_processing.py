import zmq
from time import sleep
from datetime import datetime
from .database import db_connect, tweet_table_session, Tweet
import base64
from typing import Dict, Optional
import uuid

import json

from . import ELAPSED_SECONDS_UNTIL_QUEUE, reply_queue


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

    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    identity = "worker:{}".format(uuid.uuid4())
    socket.identity = identity.encode('ascii')
    socket.connect('tcp://localhost:5555')

    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    while True:

        # Only get items that have not been matched before.
        q = session.query(Tweet).filter_by(matches=None)
        results = q.all()

        for r in results:  # type: Tweet

            if r.queued_at is None or (datetime.now()-r.queued_at).total_seconds() > ELAPSED_SECONDS_UNTIL_QUEUE:

                r.queued_at = datetime.now()

                # Base64 the image and get ready to send it.
                b64_image = base64.b64encode(r.image).decode("utf-8")

                # Convert it to a jsonable form
                tfp = TweetForProcessing(r.tweet_id, b64_image)
                payload = json.dumps(tfp.dict())

                # Send it over the ZMQ socket
                socket.send_string(payload)

                session.add(r)
                session.flush()
                session.commit()

        sockets = dict(poll.poll(50))
        if socket in sockets:
            msg = socket.recv()
            reply_queue.put(msg)
