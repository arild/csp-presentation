
import sys
import logger as Logger
from tsp import *
from pycsp import *
from timer import *
from broadcast_router import *


@multiprocess
def Worker(init_chan, task_chan, result_chan, shortest_route_chan):
    logger = Logger.get_logger('worker')
    distance_matrix = init_chan()
    shortest_distance = sys.maxint
    tasks = []
    while True:
        try:
            guards = [InputGuard(shortest_route_chan)]
            if not tasks:
                guards += [InputGuard(task_chan)]
            guards += [SkipGuard()]

            (chan, msg) = PriSelect(guards)
            if chan == shortest_route_chan:
                logger.log('NEW SHORTEST ROUTE: ', msg)
                shortest_distance = msg
            elif chan == task_chan:
                tasks = msg

            if tasks:
                shortest_route = find_shortest_route(distance_matrix, tasks.pop(), shortest_distance)
                result_chan(shortest_route)
        except ChannelPoisonException:
            break
    logger.log('DONE')


@multiprocess
def Master(init_chan, task_chan, result_chan, shortest_route_chan, num_cities, task_depth):
    logger = Logger.get_logger('master')
    distance_matrix = generate_distance_matrix(num_cities)

    # Generate tasks
    tasks = get_sub_routes(distance_matrix, task_depth)
    num_tasks = len(tasks)
    logger.log('Num tasks: ', num_tasks)

    num_results_collected = 0
    num_workers = 0
    shortest_route = Route(distance=sys.maxint)
    while num_results_collected < num_tasks:
        guards = [OutputGuard(init_chan, msg=distance_matrix),
                  InputGuard(result_chan)]
        if len(tasks) > 0:
            next_task = tasks[0:5]
            guards.append(OutputGuard(task_chan, msg=next_task))

        #logger.log('before select')
        (chan, msg) = AltSelect(guards)
        #logger.log('after select')
        if chan == init_chan:
            num_workers += 1
        elif chan == task_chan:
            tasks = tasks[5:]
        elif chan == result_chan:
            num_results_collected += 1
            if msg is not None and msg.distance < shortest_route.distance:
                shortest_route = msg
                #logger.log('sending new shortest route')
                shortest_route_chan((shortest_route.distance, num_workers))
                #logger.log('done sending new shortest route')

    poison(task_chan)
    poison(shortest_route_chan)
    logger.log('Shortest path: ', shortest_route.path)
    logger.log('Distance: ', shortest_route.distance)


def main(num_cities, task_depth, num_workers):
    init_channel = Channel()
    task_channel = Channel()
    result_channel = Channel()

    broadcast_chan_in = Channel()
    broadcast_chan_out = Channel()

    Logger.init()

    Parallel(Master(init_channel.writer(), task_channel.writer(), result_channel.reader(), broadcast_chan_in.writer(), num_cities, task_depth),
             Worker(init_channel.reader(), task_channel.reader(), result_channel.writer(), broadcast_chan_out.reader()) * num_workers,
             BroadcastRouter(broadcast_chan_in.reader(), broadcast_chan_out.writer()))

    Logger.shutdown()

    shutdown()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'usage <num cities<task depth><num workers>'
        sys.exit(0)
    num_cities = int(sys.argv[1])
    task_depth = int(sys.argv[2])
    num_workers = int(sys.argv[3])

    timer = Timer()
    with timer:
        main(num_cities, task_depth, num_workers)
    print 'Execution time in seconds: ', timer.duration_in_seconds()
