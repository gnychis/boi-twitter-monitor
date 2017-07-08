from . import reply_queue
from os import path
import xml.etree.ElementTree as ET
import json


def check_for_tweet_reply() -> None:

    # Read through the items.xml that is extracted from the game to get a mapping of sprite names to human
    # readable names.
    tree = ET.parse('boiserver/items.xml')
    root = tree.getroot()

    items = {}
    for child in root:
        items[child.attrib["gfx"].lower()] = child.attrib

    print(items)

    while True:

        # Get the response back from the C++ server which will need to be decoded.
        reply_to_parse = reply_queue.get()
        reply_to_parse = reply_to_parse.decode("utf-8")

        # Split up the tweet ID and the responses.
        tweet_id = reply_to_parse.split("|")[0]

        # Get the found images out, dealing with formatting (get rid of base path)
        found_images = reply_to_parse.split("|")[1].split(";")
        found_images = list(filter(None, found_images))
        found_images = [path.basename(element) for element in found_images]

        print("----------------------")
        print(tweet_id)

        for img in found_images:
            print(items[img]["name"])
