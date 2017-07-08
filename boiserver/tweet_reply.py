from .database import db_connect, tweet_table_session, Tweet

from . import reply_queue
from os import path
import xml.etree.ElementTree as ET
import json


def check_for_tweet_reply() -> None:

    # Connect to the database
    con, meta = db_connect('boiitems', 'kN1PcOQd', 'boiitems')
    session, db_table = tweet_table_session(con, meta)

    # Read through the items.xml that is extracted from the game to get a mapping of sprite names to human
    # readable names.
    tree = ET.parse('boiserver/items.xml')
    root = tree.getroot()

    items = {}
    for child in root:
        items[child.attrib["gfx"].lower()] = child.attrib

    while True:

        # Get the response back from the C++ server which will need to be decoded.
        reply_to_parse = reply_queue.get()
        reply_to_parse = reply_to_parse.decode("utf-8")

        # Split up the tweet ID and the responses.
        tweet_id = int(reply_to_parse.split("|")[0])

        # Get the found images out, dealing with formatting (get rid of base path)
        found_images = reply_to_parse.split("|")[1].split(";")
        found_images = list(filter(None, found_images))
        found_images = [path.basename(element) for element in found_images]

        # Get the database entry
        tweet_entry = session.query(Tweet).filter_by(tweet_id=tweet_id).first()
        tweet_entry.matches = json.dumps(found_images)

        # Save the entry
        session.add(tweet_entry)
        session.flush()
        session.commit()

        print("----------------------")
        print(tweet_id)

        for img in found_images:
            print(items[img]["name"])
