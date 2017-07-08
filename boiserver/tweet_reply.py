from . import reply_queue


def check_for_tweet_reply() -> None:

    while True:

        # Get the response back from the C++ server which will need to be decoded.
        reply_to_parse = reply_queue.get()
        reply_to_parse = reply_to_parse.decode("utf-8")

        # Split up the tweet ID and the responses.
        tweet_id = reply_to_parse.split("|")[0]
        found_images = reply_to_parse.split("|")[1].split(";")
        found_images = list(filter(None, found_images))

        print(tweet_id)
        print(found_images)
