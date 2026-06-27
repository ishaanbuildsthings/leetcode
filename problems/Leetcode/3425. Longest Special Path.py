class Solution:
    def longestSpecialPath(self, edges: List[List[int]], nums: List[int]) -> List[int]:
        
        adj = defaultdict(list) # maps node -> [(adjN, w), ...]
        for a, b, w in edges:
            adj[a].append((b, w))
            adj[b].append((a, w))
        
        left = 0
        latest = {} # maps val -> last index on our path

        n = len(nums)
        pathDists = [0] # will live track our distance from the root (across weighted edges) for each node as we dfs down

        resLength = 0
        resMin = inf


        def dfs(node, parent):
            nonlocal left
            nonlocal resLength
            nonlocal resMin

            pathI = len(pathDists) - 1

            # grab a snapshot before we dfs, so we can restore
            oldLeft = left
            oldLatest = latest.get(nums[node])

            if oldLatest is not None:
                left = max(left, oldLatest + 1)

            latest[nums[node]] = pathI

            length = pathDists[pathI] - pathDists[left]
            nodeCount = pathI - left + 1

            if length > resLength:
                resLength = length
                resMin = nodeCount
            elif length == resLength:
                resMin = min(resMin, nodeCount)

            for adjN, w in adj[node]:
                if adjN == parent:
                    continue

                pathDists.append(pathDists[-1] + w)
                dfs(adjN, node)
                pathDists.pop()

            if oldLatest is None:
                del latest[nums[node]]
            else:
                latest[nums[node]] = oldLatest

            left = oldLeft

        dfs(0, -1)
        return [resLength, resMin]