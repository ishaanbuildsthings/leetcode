class Solution:
    def kthSmallest(self, par: List[int], vals: List[int], queries: List[List[int]]) -> List[int]:
        children = defaultdict(list)
        n = len(par)
        for i in range(n):
            parent = par[i]
            if parent != -1:
                children[parent].append(i)
        
        res = [-1] * n

        nodeToQueries = defaultdict(list) # maps a node to all of its k
        for u, k in queries:
            nodeToQueries[u].append(k)
        
        queryToAnswer = {} # maps (u, k) -> ans

        def answerQueries(node, sl):
            for k in nodeToQueries[node]:
                if k > len(sl):
                    queryToAnswer[(node, k)] = -1
                else:
                    distinct = sl[k - 1]
                    queryToAnswer[(node, k)] = distinct


        def dfs(node, aboveXor):
            if not children[node]:
                sl = SortedList()
                sl.add(aboveXor ^ vals[node])
                answertreQueries(node, sl)
                return sl
            childs = [dfs(child, aboveXor ^ vals[node]) for child in children[node]]
            childs.sort(key=lambda x : -len(x)) # biggest first
            heavySl = childs[0]
            if aboveXor ^ vals[node] not in heavySl:
                heavySl.add(aboveXor ^ vals[node])
            for i in range(1, len(childs)):
                light = childs[i]
                for v in light:
                    if v not in heavySl:
                        heavySl.add(v)
            answerQueries(node, heavySl)
            return heavySl
        
        dfs(0, 0)

        res = []
        for u, k in queries:
            res.append(queryToAnswer[u, k])
        
        return res
            
            

        










# # from sortedcontainers import SortedList
# # class Solution:
# #     def kthSmallest(self, par: List[int], vals: List[int], queries: List[List[int]]) -> List[int]:

# #         children = defaultdict(list)
# #         for node in range(len(par)):
# #             parent = par[node]
# #             if parent != -1:
# #                 children[parent].append(node)

# #         answers = {}
# #         nodeToQueries = defaultdict(list)
# #         for node, k in queries:
# #             nodeToQueries[node].append(k)
        
# #         def merge(bigSl, smallSl):
# #             for val in smallSl:
# #                 if val not in bigSl:
# #                     bigSl.add(val)
        
# #         def dfs(node, xorAbove):
# #             newXor = vals[node] ^ xorAbove

# #             bigSl = SortedList()

# #             for child in children[node]:
# #                 childSl = dfs(child, newXor)
# #                 if len(childSl) > len(bigSl):
# #                     bigSl, childSl = childSl, bigSl
# #                 merge(bigSl, childSl)
            
# #             if newXor not in bigSl:
# #                 bigSl.add(newXor)
            
# #             for k in nodeToQueries[node]:
# #                 answers[(node, k)] = bigSl[k-1] if (k-1) < len(bigSl) else -1
            
# #             return bigSl
        
# #         dfs(0, 0)

# #         res = []
# #         for node, k in queries:
# #             res.append(answers[(node, k)])
# #         return res
            


# from sortedcontainers import SortedList
# class Solution:
#     def kthSmallest(self, par: List[int], vals: List[int], queries: List[List[int]]) -> List[int]:

#         children = defaultdict(list)
#         for node in range(len(par)):
#             parent = par[node]
#             if parent != -1:
#                 children[parent].append(node)

#         answers = {}
#         nodeToQueries = defaultdict(list)
#         for node, k in queries:
#             nodeToQueries[node].append(k)
        
#         def merge(bigSl, smallSl):
#             for val in smallSl:
#                 if val not in bigSl:
#                     bigSl.add(val)
        
#         def dfs(node, xorAbove):
#             newXor = vals[node] ^ xorAbove

#             bigSl = SortedList()

#             childSls = [dfs(child, newXor) for child in children[node]]
#             for childSl in childSls:
#                 if len(childSl) > len(bigSl):
#                     bigSl = childSl
#             for childSl in childSls:
#                 if childSl == bigSl:
#                     continue
#                 merge(bigSl, childSl)
            
#             if newXor not in bigSl:
#                 bigSl.add(newXor)
                
#             for k in nodeToQueries[node]:
#                 answers[(node, k)] = bigSl[k-1] if (k-1) < len(bigSl) else -1
            
#             return bigSl
        
#         dfs(0, 0)

#         res = []
#         for node, k in queries:
#             res.append(answers[(node, k)])
#         return res
            
