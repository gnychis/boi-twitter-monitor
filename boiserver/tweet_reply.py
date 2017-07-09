from .database import db_connect, tweet_table_session, Tweet
from twython import Twython, TwythonError

APP_KEY = '6LTEgHCBchKPIQdXb3IH6kJSI'
APP_SECRET = 'waHGTlmTVKQmsm485tf5WPWpUShQkTecvdvwKOBB7DA8nQlnSB'

OAUTH_TOKEN = '873749293118742528-seejM0pUZqKOCQbCzIIASapBAFMIXVH'
OAUTH_TOKEN_SECRET = 'TojXnSU3lWyiWgwoikMGI9JlCSsZjWXpxHwqvayQMYKFk'


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

    # Create an easy-to-access dictionary.
    items = {}
    for child in root:
        items[child.attrib["gfx"].lower()] = child.attrib

    # Connect to Twitter.
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.verify_credentials()

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

        named_images = [items[element]["name"] for element in found_images]
        message = ", ".join(named_images)
        message = "@{} {}".format(tweet_entry.author, message)

        print("----------------------")
        print(tweet_id)
        print(message)

        twitter.update_status(status=message, in_reply_to_status_id=tweet_id)
