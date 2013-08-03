import numpy
import random


""" Holds a route represented by a list of node numbers, and the route's total distance
"""
class Route:
    def __init__(self, path=[0], distance=0):
        self.path = path
        self.distance = distance

    """ Returns a new route by adding provided node to current route
    """
    def create_next_route(self, node, distance):
        return Route(self.path + [node], self.distance + distance)


""" Returns a deterministically generated matrix representing distances between nodes.

intended usage: matrix[row_idx][col_idx] represents distance from node 'row_idx' to node 'col_idx'
"""
def generate_distance_matrix():
    num_vertices = 11
    distanceMatrix = numpy.ndarray((num_vertices, num_vertices))
    random.seed(2)
    for i in range(0, num_vertices):
        for j in range(0, num_vertices):
            distanceMatrix[i][j] = random.randint(1, 5)
    return distanceMatrix


""" Returns a list of sub routes of maximum length/depth starting from provided route
"""
def get_sub_routes(distance_matrix, depth, current_route=Route()):
    max_path_length = len(distance_matrix)

    def get_remaining_vertices():
        return list(set(range(0, max_path_length)) - set(current_route.path))

    if len(current_route.path) == depth:
        return [current_route]
    else:
        vertices = get_remaining_vertices()
        sub_routes = []
        for vertex in vertices:
            from_vertex = current_route.path[-1]
            to_vertex = vertex
            distance = distance_matrix[from_vertex][to_vertex]
            new_current_route = current_route.create_next_route(vertex, distance)

            sub_routes += get_sub_routes(distance_matrix, depth, new_current_route)
        return sub_routes


""" Returns shortest route starting from provided sub route

Assumes that start node is 0,0 in distance matrix
"""
def find_shortest_route(distance_matrix, current_route):
    max_path_length = len(distance_matrix)

    def get_remaining_vertices():
        return list(set(range(0, max_path_length)) - set(current_route.path))

    if len(current_route.path) == max_path_length:
        # Add distance back to start vertices if all vertices have been visited
        current_route.distance += distance_matrix[0][0]
        return current_route
    else:
        vertices = get_remaining_vertices()
        shortest_final_route = None
        for vertex in vertices:
            from_vertex = current_route.path[-1]
            to_vertex = vertex
            distance = distance_matrix[from_vertex][to_vertex]
            new_current_route = current_route.create_next_route(vertex, distance)

            final_route = find_shortest_route(distance_matrix, new_current_route)
            if shortest_final_route is None or final_route.distance < shortest_final_route.distance:
                shortest_final_route = final_route

        return shortest_final_route
