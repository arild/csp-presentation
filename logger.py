from pycsp import *
import datetime

log_chan = None


@process
def LoggerProcess(log_chan):
    while True:
        try:
            (prefix, msg) = log_chan()
            print '[' + str(datetime.datetime.now().strftime('%H:%M:%S.%f')) + '][' + prefix.upper() + '] ' + msg
        except ChannelPoisonException:
            break


def init():
    global log_chan
    log_chan = Channel('logger')
    Spawn(LoggerProcess(log_chan.reader()))


def shutdown():
    poison(log_chan.reader())


def get_logger(prefix):
    return Logger(prefix, log_chan.writer())


class Logger:
    def __init__(self, prefix, log_chan):
        self.prefix = prefix
        self.log_chan = log_chan

    def log(self, *args):
        msg = ''
        for arg in args:
            msg += str(arg)
        self.log_chan((self.prefix, msg))