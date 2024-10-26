# https://leetcode.com/problems/bus-routes/description/
# difficulty: hard
# tags: graph, unconnected, undirected

# Problem
# You are given an array routes representing bus routes where routes[i] is a bus route that the ith bus repeats forever.

# For example, if routes[0] = [1, 5, 7], this means that the 0th bus travels in the sequence 1 -> 5 -> 7 -> 1 -> 5 -> 7 -> 1 -> ... forever.
# You will start at the bus stop source (You are not on any bus initially), and you want to go to the bus stop target. You can travel between bus stops by buses only.

# Return the least number of buses you must take to travel from source to target. Return -1 if it is not possible.

# Solution
# I just treated each route itself as a node, and found which routes connect to each other. I was getting a working solution at first so the code might not be the cleanest, but the overall complexities and idea should be mostly correct.

class Solution:
    def numBusesToDestination(self, routes: List[List[int]], source: int, target: int) -> int:
        # edge case
        if source == target:
            return 0

        locations = defaultdict(list) # maps a location to a list of routes it occurs in
        for i in range(len(routes)):
            route = routes[i]
            for loc in route:
                locations[loc].append(i)

        edgeMap = defaultdict(set) # maps a node (ith route) to other routes it connects to
        for loc in locations:
            listOfRoutesThatLocIsIn = locations[loc]
            for i in range(len(listOfRoutesThatLocIsIn) - 1):
                firstRoute = listOfRoutesThatLocIsIn[i]
                for j in range(i + 1, len(listOfRoutesThatLocIsIn)):
                    secondRoute = listOfRoutesThatLocIsIn[j]
                    edgeMap[firstRoute].add(secondRoute)
                    edgeMap[secondRoute].add(firstRoute)

        targetRoutes = set(locations[target]) # we need to reach one of these routes

        seen = set() # tracks which routes we have access to
        queue = collections.deque()
        startingRoutes = locations[source]
        for startRouteIndex in startingRoutes:
            # edge case
            if startRouteIndex in targetRoutes:
                return 1
            queue.append(startRouteIndex)
            seen.add(startRouteIndex)

        res = 1

        while queue:
            res += 1
            length = len(queue)
            for _ in range(length):
                routeIndexWeAccessed = queue.popleft()
                adjToThatRoute = list(edgeMap[routeIndexWeAccessed])
                for adj in adjToThatRoute:
                    if adj in targetRoutes:
                        return res
                    if not adj in seen:
                        queue.append(adj)
                        seen.add(adj)

        return -1





