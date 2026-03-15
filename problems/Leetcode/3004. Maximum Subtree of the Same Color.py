class Solution:
    def maximumSubtreeSize(self, edges: List[List[int]], colors: List[int]) -> int:

        # note, you can do this in one dfs, where the dfs returns if the subtree is all the same color so far, and the size of it
        
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

        children = edgeListToTree(edges)

        @cache
        def size(node):
            if not children[node]:
                return 1
            return 1 + sum(size(child) for child in children[node])
        
        @cache
        def allSame(node):
            return all(
                colors[node] == colors[child] for child in children[node]
            ) and all(
                allSame(child) for child in children[node]
            )
        
        res = 0

        def dfs(node):
            nonlocal res
            if allSame(node):
                res = max(res, size(node))
            for child in children[node]:
                dfs(child)
        
        dfs(0)

        return res