from pycsp import *
from logger import get_logger


def sendAsync(chan, msg):
    @process
    def _SendAsync():
        chan(msg)
    Spawn(_SendAsync())


@process
def BroadcastRouter(publish_chan, subscribe_chan):
    logger = get_logger('broadcast')
    subscription_channels = []
    while True:
        try:
            guards = [InputGuard(publish_chan), InputGuard(subscribe_chan)]
            (chan, msg) = PriSelect(guards)

            if chan == subscribe_chan:
                subscription_channels.append(msg)
            elif chan == publish_chan:
                for chan in subscription_channels:
                    sendAsync(chan, msg)
        except ChannelPoisonException:
            break
    logger.log('Terminating')