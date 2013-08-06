from pycsp import *
import logger as Logger


@process
def BroadcastRouter(in_chan, out_chan):
    logger = Logger.get_logger('broadcast')
    items_to_broadcast = []
    while True:
        try:
            guards = [InputGuard(in_chan)]
            if len(items_to_broadcast) > 0:
                guards.append(OutputGuard(out_chan, msg=items_to_broadcast[-1]))

            #logger.log('before select')
            (chan, msg) = PriSelect(guards)
            #logger.log('after select')
            if chan == out_chan:
                items_to_broadcast.pop()
            elif chan == in_chan:
                items_to_broadcast = []
                (msg_, num_times) = msg
                for _ in range(0, num_times):
                    items_to_broadcast.append(msg_)
                logger.log('broacasting new value: ' + str(msg_) + ' num times: ' + str(num_times))
            else:
                logger.log('broadcast timeout')

        except ChannelPoisonException:
            break

    logger.log('DONE')