
import sys
import logger as Logger
from tsp import *
from pycsp import *
from timer import *
from broadcast_router import *


@clusterprocess(cluster_nodefile='nodefile')
def Worker(id, init_chan, task_chan, result_chan, shortest_route_subscribe_chan, logger):
    import socket
    logger.log(id, ' starting on: ', socket.gethostname())

    shortest_route_chan = Channel()
    shortest_route_subscribe_chan(shortest_route_chan.writer())
    shortest_route_chan = shortest_route_chan.reader()

    distance_matrix = init_chan()
    shortest_distance = sys.maxint
    tasks = []
    while True:
        guards = [InputGuard(shortest_route_chan)]
        if not tasks:
            guards += [InputGuard(task_chan)]
        guards += [SkipGuard()]

        (chan, msg) = PriSelect(guards)
        if chan == shortest_route_chan:
            logger.log('New shortest route: ', msg)
            shortest_distance = msg
        elif chan == task_chan:
            tasks = msg
            if not tasks:
                task_chan.retire()
                break

        if tasks:
            shortest_route = find_shortest_route(distance_matrix, tasks.pop(), shortest_distance)
            if shortest_route and shortest_route.distance < shortest_distance:
                result_chan(shortest_route)
    logger.log('Terminating')


@multiprocess
def Master(init_chan, task_chan, result_chan, shortest_route_chan, num_cities, task_depth):
    logger = Logger.get_logger('master')
    distance_matrix = generate_distance_matrix(num_cities)

    # Generate tasks
    tasks = get_sub_routes(distance_matrix, task_depth)
    logger.log('Number of tasks: ', len(tasks))

    shortest_route = Route(distance=sys.maxint)
    while True:
        try:
            guards = [OutputGuard(init_chan, msg=distance_matrix),
                      InputGuard(result_chan)]
            if tasks:
                guards.append(OutputGuard(task_chan, msg=tasks[0:5]))
            else:
                guards.append(OutputGuard(task_chan, msg=None))

            (chan, msg) = AltSelect(guards)

            if chan == task_chan:
                tasks = tasks[5:]
            elif chan == result_chan:
                if msg.distance < shortest_route.distance:
                    shortest_route = msg
                    logger.log('Broadcasting new shortest route')
                    shortest_route_chan(shortest_route.distance)
        except ChannelRetireException:
            break
    poison(shortest_route_chan)
    logger.log('Shortest path: ', shortest_route.path)
    logger.log('Distance: ', shortest_route.distance)


def main(num_cities, task_depth, num_workers):
    init_channel = Channel('init')
    task_channel = Channel('task')
    result_channel = Channel('result')

    broadcast_publish_chan = Channel('broadcast_publish')
    broadcast_subscribe_chan = Channel('broadcast_subscribe')

    Logger.init()

    workers = []
    for i in range(0, num_workers):
        logger = Logger.get_logger('worker')
        workers.append(Worker(i, init_channel.reader(), task_channel.reader(), result_channel.writer(), broadcast_subscribe_chan.writer(), logger))

    Parallel(Master(init_channel.writer(), task_channel.writer(), result_channel.reader(), broadcast_publish_chan.writer(), num_cities, task_depth),
             workers,
             BroadcastRouter(broadcast_publish_chan.reader(), broadcast_subscribe_chan.reader()))

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
