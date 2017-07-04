import sqlalchemy
from sqlalchemy.orm import mapper, sessionmaker

from sqlalchemy import BigInteger, Binary, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from threading import Lock

from typing import Tuple

lock = Lock()
mapped = False


class Tweet(object):

    def __init__(self, tweet_id, image):
        self.tweet_id = tweet_id
        self.image = image


def db_connect(user: str, password: str, db, host='localhost', port: int=5432) -> Tuple:
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
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
    extend_existing = True
    if "posts" not in meta.tables:
        extend_existing = False

    print("Extend existing: {}".format(extend_existing))
    db_table = Table(
        'posts', meta,
        Column('tweet_id', BigInteger, primary_key=True, autoincrement=False),
        Column('image', Binary),
        extend_existing=extend_existing
    )

    if not extend_existing:
        meta.create_all(con)

    lock.acquire()
    if not mapped:
        mapper(Tweet, db_table)
        mapped = True
    lock.release()

    return session, db_table
