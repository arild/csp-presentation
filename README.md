
#### Parallelization of [travelling salesman problem (TSP)](http://en.wikipedia.org/wiki/Travelling_salesman_problem) using [PyCSP](https://code.google.com/p/pycsp/)

Used as an example in the presentation: ["Communicating Sequential Processes (CSP) - An alternative to the actor model"](http://arild.github.io/csp-presentation)

The implementation models TSP as a complete, undirected weighted graph, and implements the branch-and-bound optimization. The parallelization uses a master-slave pattern, and requires Python 2.6 or 2.7.

##### How to run sequential version:

`python run_sequential.py <num_cities>`, where
  * `num_cities` is number of cites/node in TSP 
  
##### How to run parallel version:  

`python run_parallel.py <num_cities><task depth><num workers>`, where
  * `num_cities` is number of cities/nodes in TSP
  * `task depth` is the length of sub-routes the master will use as tasks in the parallelization. A larger task depth results in more tasks.
  * `num workers` is number of workers that will be spawned


##### Branches
  * **iter1**: Does not use branch-and-bound optimization in parallelization. Less complexity.
  * **cluster**: Minor modification for using the cluster module in PyCSP. 
