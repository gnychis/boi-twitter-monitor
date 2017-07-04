from threading import Thread
from time import sleep

from . import IMAGE_GRABBER_THREADS, TWEET_CHECK_THREADS, CHECK_FOR_PROCESSING_THREADS, new_tweets_queue
from .image_grabbers import tweet_worker
from .tweet_checker import check_tweets
from .check_for_processing import check_for_processing

if __name__ == "__main__":

    #####################################################################################
    print("Starting image grabber threads ({})".format(IMAGE_GRABBER_THREADS))
    for i in range(IMAGE_GRABBER_THREADS):
        worker = Thread(target=tweet_worker, args=(new_tweets_queue,))
        worker.setDaemon(True)
        worker.start()

    #####################################################################################
    print("Starting tweet checking threads ({})".format(TWEET_CHECK_THREADS))
    for i in range(TWEET_CHECK_THREADS):
        worker = Thread(target=check_tweets, args=())
        worker.setDaemon(True)
        worker.start()

    #####################################################################################
    print("Starting check for processing threads ({})".format(CHECK_FOR_PROCESSING_THREADS))
    for i in range(CHECK_FOR_PROCESSING_THREADS):
        worker = Thread(target=check_for_processing, args=())
        worker.setDaemon(True)
        worker.start()

    new_tweets_queue.join()

    while True:
        sleep(1)
