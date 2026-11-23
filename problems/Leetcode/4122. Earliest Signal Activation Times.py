# Wrong Answer
# 860 / 937 testcases passed
# Input
# n =
# 5
# edges =
# [[3,4,17],[2,4,11],[4,0,6],[0,3,11],[3,1,4]]
# requiredSignals =
# [1,1,1,1,1]
# Use Testcase
# Output
# [34,15,-1,11,28]
# Expected
# [0,15,-1,11,28]




# Wrong Answer
# 916 / 937 testcases passed
# Input
# n =
# 9
# edges =
# [[0,1,28],[1,2,75],[1,3,14],[3,4,75],[0,5,6],[3,6,60],[5,7,43],[5,8,73],[0,8,24],[2,1,63],[2,5,38],[8,0,32],[0,7,37],[0,6,38],[1,6,24],[0,4,57],[2,3,51]]
# requiredSignals =
# [1,2,1,3,1,1,1,1,2]
# Use Testcase
# Output
# [0,139,214,-1,57,6,38,37,79]
# Expected
# [0,-1,-1,-1,57,6,38,37,79]


class Solution:
    def earliestActivationTimes(self, n: int, edges: list[list[int]], requiredSignals: list[int]) -> list[int]:
        # edges.sort()
        # print(edges)

        incoming = [0] * n # how many currently incoming signals exist at a node
        time = 0

        res = [inf] * n
        res[0] = 0

        heap = [] # holds (time of arrival, from node, to node)

        adj = defaultdict(list) # maps node -> [(target, delay)]
        for a, b, w in edges:
            adj[a].append((b, w))

        for b, w in adj[0]:
            heapq.heappush(heap, (w, 0, b))

        while heap:
            # print('-------')
            time, fromNode, toNode = heapq.heappop(heap)
            # print(f'{time=} {fromNode=} {toNode=}')
            incoming[toNode] += 1
            # print(f'incoming of: {toNode} now: {incoming[toNode]}')

            if incoming[toNode] == requiredSignals[toNode] and toNode != 0:
                # print(f'satisfied node: {toNode}')
                res[toNode] = time
                # print(f'hit requirement')
                for b, w in adj[toNode]:
                    # print(f'adding edge: {toNode}->{b}')
                    heapq.heappush(heap, (time + w, toNode, b))

        res[0] = 0

        return [x if x != inf else -1 for x in res]