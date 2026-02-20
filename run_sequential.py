
from tsp import *
from timer import *
import sys


def main(num_cities):
    route = Route()
    distance_matrix = generate_distance_matrix(num_cities)
    route = find_shortest_route(distance_matrix, route)
    print('Shortest path: ', route.path)
    print('Distance: ', route.distance)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage <num cities>')
        sys.exit(0)
    num_cities = int(sys.argv[1])
    timer = Timer()
    with timer:
        main(num_cities)
    print('Execution time in seconds: ', timer.duration_in_seconds())