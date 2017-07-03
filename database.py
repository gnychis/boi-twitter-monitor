import sqlalchemy
from sqlalchemy.orm import mapper, sessionmaker

from sqlalchemy import BigInteger, Binary, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from entities import Tweet


def db_connect(user, password, db, host='localhost', port=5432):
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


def tweet_table_session(con, meta):

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

    mapper(Tweet, db_table)

    return session, db_table
