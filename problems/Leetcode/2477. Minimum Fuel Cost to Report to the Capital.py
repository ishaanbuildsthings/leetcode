# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# takes nodes from 0 to n-1 and constructs a children map rooted at 0
from collections import defaultdict
def edgeListToTree(edgeList):
    edgeMap = defaultdict(list)
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    children = defaultdict(list) # maps a node to its children

    def buildTree(node, parent):
        for adj in edgeMap[node]:
            if adj == parent:
                continue
            children[node].append(adj)
            buildTree(adj, node)
    buildTree(0, -1) # root at 0
    return children
class Solution:
    def minimumFuelCost(self, roads: List[List[int]], seats: int) -> int:
        
        children = edgeListToTree(roads)

        gas = 0

        # returns how many full cars are moving, and how many people are in the last car
        def dfs(node):
            nonlocal gas
            if not children[node]:
                if seats == 1:
                    return (1, 0)
                return (0, 1)
            fullCars = 0
            totalPeopleLast = 1
            for child in children[node]:
                fullCarsHere, people = dfs(child)
                gas += fullCarsHere
                if people:
                    gas += 1
                fullCars += fullCarsHere
                totalPeopleLast += people
            carsGain = totalPeopleLast // seats
            fullCars += carsGain
            totalPeopleLast %= seats
            return (fullCars, totalPeopleLast)
        
        dfs(0)

        return gas
