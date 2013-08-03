
from tsp import *


def main():
    route = Route()
    distance_matrix = generate_distance_matrix()
    route = find_shortest_route(distance_matrix, route)
    print 'Shortest path: ', route.path
    print 'Distance: ', route.distance


if __name__ == "__main__":
    import timeit
    time = timeit.timeit(main, number=1)
    print 'Execution time in seconds: ', time