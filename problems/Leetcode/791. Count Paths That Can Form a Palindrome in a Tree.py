class Info:
    def __init__(self):
        self.mp = {} # maps mask -> count
        self.offset = 0
    
    def shift(self, x):
        self.offset ^= x
    
    def items(self):
        for k, v in self.mp.items():
            yield k ^ self.offset, v
    
    def get(self, realMask):
        return self.mp.get(realMask ^ self.offset, 0)
    
    def add(self, mask, frq):
        self.mp[mask ^ self.offset] = self.mp.get(mask ^ self.offset, 0) + frq

class Solution:
    def countPalindromePaths(self, parent: List[int], s: str) -> int:
        n = len(parent)
        children = [[] for _ in range(n)]
        for i in range(n):
            if parent[i] != -1:
                children[parent[i]].append(i)
        
        res = 0

        def dfs(node):
            nonlocal res
            above = s[node]
            mask = 1 << (ord(above) - ord('a'))
            if not children[node]:
                info = Info()
                info.add(0, 1)
                info.shift(mask)
                return info
            childs = [dfs(c) for c in children[node]]
            childs.sort(key=lambda x: len(x.mp),reverse=True)
            heavy = childs[0]
            for i in range(1, len(childs)):
                light = childs[i]
                for k, v in light.items():
                    # xor this mask against the heavy
                    cnt1 = heavy.get(k) * v
                    res += cnt1

                    # anything 1 bit off also works
                    for b in range(26):
                        nmask = k ^ (1 << b)
                        cnt2 = heavy.get(nmask) * v
                        res += cnt2
                # fold in
                for k, v in light.items():
                    heavy.add(k, v)
            
            # score anything that ends at the node
            res += heavy.get(0)
            for b in range(26):
                res += heavy.get(1 << b)
            heavy.add(0, 1)

            heavy.shift(mask)
            return heavy
        
        dfs(0)

        return res
                    





# class Info:
#     def __init__(self):
#         self.mp = {} # maps mask -> count
#         self.offset = 0 # xor offset


# class Solution:
#     def countPalindromePaths(self, parent: List[int], s: str) -> int:
        # n = len(parent)
        # children = [[] for _ in range(n)]
        # for i in range(n):
        #     if parent[i] != -1:
        #         children[parent[i]].append(i)
        
        # res = 0
        
#         def dfs(node):
#             nonlocal res
#             above = s[node]
#             msk = 1 << (ord(above) - ord('a'))
#             if not children[node]:
#                 info = Info()
#                 info.mp[0] = info.mp.get(0, 0) + 1 # this is actually the right mask, handled by the offset
#                 info.offset ^= msk
#                 return info

#             childs = [dfs(child) for child in children[node]]
#             childs.sort(key=lambda x: len(x.mp),reverse=True)
#             heavyInfo = childs[0]
#             for i in range(1, len(childs)):
#                 lightInfo = childs[i]
#                 for key, frq in lightInfo.mp.items():
#                     actualMask = key ^ lightInfo.offset
#                     res += frq * heavyInfo.mp.get(actualMask ^ heavyInfo.offset, 0) # xor with itself
#                     for b in range(26):
#                         res += frq * heavyInfo.mp.get(actualMask ^ (1 << b) ^ heavyInfo.offset, 0)
#                 for key, frq in lightInfo.mp.items():
#                     real = key ^ lightInfo.offset
#                     heavyInfo.mp[real ^ heavyInfo.offset] = heavyInfo.mp.get(real ^ heavyInfo.offset, 0) + frq
#             # any paths ending at the node itself also work
#             res += heavyInfo.mp.get(heavyInfo.offset, 0) # check any 0 paths
#             for b in range(26):
#                 res += heavyInfo.mp.get(((1<<b) ^ heavyInfo.offset), 0)
#             heavyInfo.mp[heavyInfo.offset] = heavyInfo.mp.get(heavyInfo.offset, 0) + 1
#  # this part is confusing...
#             heavyInfo.offset ^= msk
#             return heavyInfo
        
#         dfs(0)

#         return res

