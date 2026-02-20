
import sys
from functools import reduce
from tsp import *
from pycsp import *
from timer import *


@multiprocess
def Worker(init_chan, task_chan, result_chan):
    distance_matrix = init_chan()
    while True:
        try:
            sub_route = task_chan()
            shortest_route = find_shortest_route(distance_matrix, sub_route)
            result_chan(shortest_route)
        except ChannelPoisonException:
            break


@multiprocess
def Master(init_chan, task_chan, result_chan, num_cities, task_depth):
    distance_matrix = generate_distance_matrix(num_cities)

    # Generate tasks
    tasks = get_sub_routes(distance_matrix, task_depth)
    num_tasks = len(tasks)
    print('Num tasks: ', num_tasks)

    results = []
    while len(results) < num_tasks:
        guards = [OutputGuard(init_chan, msg=distance_matrix),
                  InputGuard(result_chan),
                  TimeoutGuard(seconds=1)]
        if len(tasks) > 0:
            next_task = tasks[-1]
            guards.append(OutputGuard(task_chan, msg=next_task, action=tasks.pop))

        (chan, msg) = AltSelect(guards)
        if chan == result_chan:
            results.append(msg)

    poison(task_chan)

    shortest_route = reduce(lambda res, cur: cur if cur.distance < res.distance else res, results)
    print('Shortest path: ', shortest_route.path)
    print('Distance: ', shortest_route.distance)


def main(num_cities, task_depth, num_workers):
    init_channel = Channel()
    task_channel = Channel()
    result_channel = Channel()
    Parallel(Master(init_channel.writer(), task_channel.writer(), result_channel.reader(), num_cities, task_depth),
             Worker(init_channel.reader(), task_channel.reader(), result_channel.writer()) * num_workers)
    shutdown()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method('fork')

    if len(sys.argv) != 4:
        print('usage <num cities> <task depth> <num workers>')
        sys.exit(0)
    num_cities = int(sys.argv[1])
    task_depth = int(sys.argv[2])
    num_workers = int(sys.argv[3])

    timer = Timer()
    with timer:
        main(num_cities, task_depth, num_workers)
    print('Execution time in seconds: ', timer.duration_in_seconds())
