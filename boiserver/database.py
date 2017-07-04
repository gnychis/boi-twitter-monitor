import sqlalchemy

from sqlalchemy import BigInteger, Binary, Table, Column, String, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from threading import Lock

from typing import Tuple

lock = Lock()
mapped = False


class Tweet(object):

    def __init__(self, tweet_id, image):
        self.tweet_id = tweet_id
        self.image = image
        self.queued_at = None
        self.boxed_image = None
        self.matches = None


def db_connect(user: str, password: str, db, host='localhost', port: int=5432) -> Tuple:
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta


def tweet_table_session(con, meta) -> Tuple:
    global mapped

    Session = sessionmaker(bind=con)
    session = Session()

    #####################################################################################
    # Setup the database
    lock.acquire()
    extend_existing = True
    if "posts" not in meta.tables:
        extend_existing = False

    db_table = Table(
        'posts', meta,
        Column('tweet_id', BigInteger, primary_key=True, autoincrement=False),
        Column('image', Binary),
        Column('queued_at', DateTime),
        Column('boxed_image', Binary),
        Column('matches', String),
        extend_existing=extend_existing
    )

    if not extend_existing:
        meta.create_all(con)

    if not mapped:
        mapper(Tweet, db_table)
        mapped = True
    lock.release()

    return session, db_table
