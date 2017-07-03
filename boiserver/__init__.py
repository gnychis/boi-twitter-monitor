from queue import Queue

from threading import Thread
from .image_grabbers import tweet_worker

num_threads = 2

new_tweets_queue = Queue()

#####################################################################################
# Start the threads
for i in range(num_threads):
    worker = Thread(target=tweet_worker, args=(new_tweets_queue,))
    worker.setDaemon(True)
    worker.start()

new_tweets_queue.join()
