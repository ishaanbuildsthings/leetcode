class Solution:
    def countPairs(self, n: int, edges: List[List[int]], queries: List[int]) -> List[int]:

        between = defaultdict(int)
        for a, b in edges:
            between[min(a, b), max(a, b)] += 1
        
        adjMap = defaultdict(list)
        for a, b in edges:
            adjMap[a].append(b)
            adjMap[b].append(a)
        
        uniqEdges = set()
        for a, b in edges:
            uniqEdges.add((min(a, b), max(a, b)))

        adjSizes = []
        for node in range(1, n + 1):
            adjSizes.append(len(adjMap[node]))
        adjSizes.sort()
        
        def solveQ(q):
            # every pair must have more total edges than q
            total = 0
            r = n - 1
            # we want to fit as much as possible
            for l in range(n):
                # if r shrunk a lot we basically step it back up
                r = max(r, l)
                # shrink while valid, r will then end up at the rightmost invalid one where the sum is too small    
                while (adjSizes[l] + adjSizes[r] > q) and r > l:
                    r -= 1
                gained = n - r - 1
                total += gained
            
            for a, b in uniqEdges:
                sz = len(adjMap[a]) + len(adjMap[b])
                if sz > q and sz - between[min(a, b), max(a, b)] <= q:
                    total -= 1
            
            return total
        
        return [solveQ(q) for q in queries]
