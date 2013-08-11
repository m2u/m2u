from threading import Thread
import time # for sleep

class RepeatTimer(Thread):
    """
    Creates a thread that executes some function on a given interval.
    Start/stop by using ".start()" (inherited from Thread) and ".stop()"
    """
    def __init__(self, function, interval):
        self.function = function
        self.interval = interval
        self.stopped = False
        Thread.__init__(self)

    def stop(self):
        # convenience method
        self.stopped = True

    def run(self):
        while not self.stopped:
            try:
                self.function()
            except Exception as e:
                print "RepeatTimer Error:", e
            time.sleep(self.interval)
            


# import threading

# class RepeatTimer(threading.Thread):
#     def __init__(self, interval, callable, *args, **kwargs):
#         threading.Thread.__init__(self)
#         self.interval = interval
#         self.callable = callable
#         self.args = args
#         self.kwargs = kwargs
#         self.event = threading.Event()
#         self.event.set()

#     def run(self):
#         while self.event.is_set():
#             t = threading.Timer(self.interval, self.callable,
#                                 self.args, self.kwargs)
#             t.start()
#             t.join()

#     def cancel(self):
#         self.event.clear()
