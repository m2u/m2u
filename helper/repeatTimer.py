from threading import Thread
import time # for sleep

class RepeatTimer(Thread):
    """
    Creates a thread that executes some function on a given interval.
    Start/stop by using ".start()" (inherited from Thread) and ".stop()"
    """
    def __init__(self, function, interval):
        super(RepeatTimer, self).__init__()
        self.function = function
        self.interval = interval
        self.stopped = False

    def stop(self):
        # Convenience method
        self.stopped = True

    def run(self):
        while not self.stopped:
            try:
                self.function()
            except Exception as e:
                print "RepeatTimer Error:", e
            time.sleep(self.interval)