from queue import Queue

from .image_grabbers import tweet_worker

TWEET_CHECK_THREADS = 1
TWEET_REPLY_THREADS = 5
IMAGE_GRABBER_THREADS = 2
CHECK_FOR_PROCESSING_THREADS = 1

ELAPSED_SECONDS_UNTIL_QUEUE = 30

new_tweets_queue = Queue()
reply_queue = Queue()
