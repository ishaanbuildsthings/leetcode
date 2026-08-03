class Solution:
    def countHighestScoreNodes(self, parents: List[int]) -> int:
        children = defaultdict(list)
        for i in range(len(parents)):
            par = parents[i]
            if par != -1:
                children[par].append(i)
            
        @cache
        def sz(node):
            if not children[node]:
                return 1
            return 1 + sum(sz(child) for child in children[node])
        
        mxScore = 0
        res = 0

        n = sz(0)

        def dfs(node):
            nonlocal res
            nonlocal mxScore
            sizes = []
            above = n - sz(node)
            if above:
                sizes.append(above)
            for child in children[node]:
                sizes.append(sz(child))
            score = 1
            for v in sizes:
                score *= v
            if score > mxScore:
                mxScore = score
                res = 1
            elif score == mxScore:
                res += 1
            for child in children[node]:
                dfs(child)
        
        dfs(0)

        return res