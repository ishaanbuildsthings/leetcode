class Solution:
    def numberOfGoodPaths(self, vals: List[int], edges: List[List[int]]) -> int:
        n = len(edges) + 1
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        
        children = [[] for _ in range(n)]
        def makeChildren(node, parent):
            for adjN in g[node]:
                if adjN == parent:
                    continue
                children[node].append(adjN)
                makeChildren(adjN, node)
        makeChildren(0, -1)

        res = 0

        # returns up a hashmap of how many paths start below it, with that number, never hitting a bigger element
        def dfs(node):
            nonlocal res
            v = vals[node]
            if not children[node]:
                ans = defaultdict(int)
                ans[v] = 1
                return ans
            mp = defaultdict(int)
            mp[v] = 1
            for child in children[node]:
                childMp = dfs(child)
                if len(childMp) > len(mp):
                    mp, childMp = childMp, mp
                for key in childMp:
                    oldWays = mp[key]
                    newWays = childMp[key]
                    if key >= v:
                        res += oldWays * newWays
                    mp[key] += childMp[key]
            deleted = []
            for key in mp.keys():
                if key < v:
                    deleted.append(key)
            for key in deleted:
                del mp[key]
            return mp
        
        dfs(0)

        return res + n

                
