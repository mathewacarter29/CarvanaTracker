#!/usr/bin/env python

'''
Source: https://realpython.com/intro-to-python-threading/#starting-a-thread
'''
import threading
import logging
import time
import concurrent.futures

def thread_function(name):
  logging.info("Thread %s: starting", name)
  time.sleep(2)
  logging.info("Thread %s: stopping", name)

if __name__ == "__main__":
  format = "%(asctime)s: %(message)s"
  logging.basicConfig(format=format, level=logging.INFO,
                      datefmt="%H:%M:%S")

  # End of with block causes the threadpool to wait for its threads to complete
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    # can also use executor.submit(thread_routine, arg)
    executor.map(thread_function, range(3))

'''
x = threading.Thread(target=thread_function, args=(index,))
x.join() joins a thread
when you create threads, you should add them to a list so you can join them later

Easiest to use a threadpool though
ThreadPoolExecuter
import concurrent.futures


we CAN have race conditions
need to use a Lock - threading.Lock()
- my_lock.acquire() and my_lock.release()
'''