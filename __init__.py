from queue import Queue

from threading import Thread

num_threads = 8

new_tweets_queue = Queue()

#####################################################################################
# Start the threads
for i in range(num_threads):
    worker = Thread(target=tweet_worker, args=(queue, session, db_table, con))
    worker.setDaemon(True)
    worker.start()

queue.join()
