
from tsp import *
from pycsp import *


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


@process
def Broadcast(chan, msg, num_times):
    for _ in range(0, num_times):
        AltSelect(OutputGuard(chan, msg=msg),
                  TimeoutGuard(seconds=5))
    print 'broadcast done'


@multiprocess
def Master(init_chan, task_chan, result_chan):
    distance_matrix = generate_distance_matrix()

    # Generate tasks
    tasks = get_sub_routes(distance_matrix, 2)
    num_tasks = len(tasks)
    print 'Num tasks: ', num_tasks

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
    print 'Shortest path: ', shortest_route.path
    print 'Distance: ', shortest_route.distance


def main():
    init_channel = Channel()
    task_channel = Channel()
    result_channel = Channel()
    Parallel(Master(init_channel.writer(), task_channel.writer(), result_channel.reader()),
             Worker(init_channel.reader(), task_channel.reader(), result_channel.writer()) * 4)


if __name__ == "__main__":
    import timeit
    time = timeit.timeit(main, number=1)
    print 'Execution time in seconds: ', time
    shutdown()
