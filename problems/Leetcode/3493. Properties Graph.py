class Solution:
    def numberOfComponents(self, properties: List[List[int]], k: int) -> int:
        adjMap = defaultdict(list)
        n = len(properties)
        for node in range(n):
            for node2 in range(n):
                if node == node2:
                    continue
                p1 = properties[node]
                p2 = properties[node2]
                s1 = set(p1)
                s2 = set(p2)
                common = 0
                for value in range(1, 101):
                    if value in s1 and value in s2:
                        common += 1
                if common >= k:
                    adjMap[node].append(node2)
                    adjMap[node2].append(node)
        
        seen = set() # touched nodes
        ans = 0
        
        def dfs(node):
            seen.add(node)
            for adj in adjMap[node]:
                if not adj in seen:
                    dfs(adj)
        
        for node in range(n):
            if not node in seen:
                ans += 1
                dfs(node)
        
        return ans
                    
                