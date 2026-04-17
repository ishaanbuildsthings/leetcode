# good solution, store parent pointers list of all shortest paths instead of the entire path
class Solution:
    def findLadders(self, beginWord: str, endWord: str, wordList: List[str]) -> List[List[str]]:
        if endWord not in wordList:
            return []
        if beginWord not in wordList:
            wordList.append(beginWord)
        adj = defaultdict(list) # could avoid n^2
        for i in range(len(wordList)):
            for j in range(i + 1, len(wordList)):
                diffs = sum(wordList[i][k] != wordList[j][k] for k in range(len(wordList[i])))
                if diffs == 1:
                    adj[wordList[i]].append(wordList[j])
                    adj[wordList[j]].append(wordList[i])
        parents = defaultdict(list) # stores a list of parent pointers that could be traversed for all shortest paths
        q = deque()
        q.append(beginWord)
        seen = {beginWord}
        while q:
            length = len(q)
            levelSeen = set() # we store seen on a batched per-level basis
            # this prevents the first node in the level from marking an adjacent node as seen
            for _ in range(length):
                w = q.popleft()
                for adjN in adj[w]:
                    if adjN in seen:
                        continue
                    if adjN not in levelSeen:
                        q.append(adjN)
                    levelSeen.add(adjN)
                    parents[adjN].append(w)
            seen |= levelSeen
                
        
        res = []
        path = [endWord]
        def backtrack(node):
            if node == beginWord:
                res.append(path[::-1])
                return
            for w in parents[node]:
                path.append(w)
                backtrack(w)
                path.pop()
        backtrack(endWord)
        return res


        




# failing solution (MLE)

# for each node, store all min length paths to reach it
# we use the seen set as normal, exists to prevent adding things to queue only
# but doesn't prevent us from adding paths (which is good)
# class Solution:
#     def findLadders(self, beginWord: str, endWord: str, wordList: List[str]) -> List[List[str]]:
        # if endWord not in wordList:
        #     return []
        # if beginWord not in wordList:
        #     wordList.append(beginWord)
        # adj = defaultdict(list) # could avoid n^2
        # for i in range(len(wordList)):
        #     for j in range(i + 1, len(wordList)):
        #         diffs = sum(wordList[i][k] != wordList[j][k] for k in range(len(wordList[i])))
        #         if diffs == 1:
        #             adj[wordList[i]].append(wordList[j])
        #             adj[wordList[j]].append(wordList[i])
        
#         mins = defaultdict(list) # maps a word -> list of all shortest paths to reach it
#         mins[beginWord].append([beginWord])
#         q = deque()
#         q.append(beginWord)
#         seen = {beginWord}
#         while q:
#             length = len(q)
#             for _ in range(length):
#                 w = q.popleft()
#                 wDist = len(mins[w][0]) # we could reach w in a minimum word chain of this size
#                 for adjN in adj[w]:
#                     # if we reached the adjacent word in a faster distance, don't go there
#                     if mins[adjN] and len(mins[adjN][0]) != wDist + 1:
#                         continue
#                     for path in mins[w]:
#                         npath = path + [adjN]
#                         mins[adjN].append(npath)
#                     if adjN not in seen:
#                         q.append(adjN)
#                         seen.add(adjN)
        
#         return mins[endWord]
