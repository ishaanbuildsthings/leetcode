class Solution:
    def maxScore(self, edges: List[List[int]]) -> int:
        n = len(edges)
        children = [[] for _ in range(n)]
        for node in range(n):
            par, wt = edges[node]
            if par != -1:
                children[par].append((node, wt))


        # take means we are allowed to take some edge coming down from this node
        # take would be false if we chose a parent edge
        @cache
        def dp(node, canTake):
            if not children[node]:
                return 0

            childrenWeDidNotTakeEdge = sum(dp(child, True) for child, wt in children[node])

            if not canTake:
                return childrenWeDidNotTakeEdge

            # for every node we could take that one coming down, and the sum of all others not taken
            childrenWeDidTakeEdge = [dp(child, False) for child, wt in children[node]]
            resHere = childrenWeDidNotTakeEdge
            for child, wt in children[node]:
                # if we take this child we score that edge + child cannot take
                # we also score all other children that did not take
                scoreIfTakeEdge = wt + dp(child, False)
                alsoScore = childrenWeDidNotTakeEdge - dp(child, True)
                score = scoreIfTakeEdge + alsoScore
                resHere = max(resHere, score)
            return resHere
        
        return max(dp(0,True),dp(0,False))

            


