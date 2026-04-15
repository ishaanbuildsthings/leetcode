# Solution 1, O(1) pick using remapping
class Solution:

    def __init__(self, n: int, blacklist: List[int]):
        blacklist.sort()
        self.bset = set(blacklist)
        m = n - len(blacklist)
        # split the world into 2 regions
        # 0...m-1
        # m...n-1

        # some numbers in 0...m-1 might be blacklisted, these are holes, we can't pick them (there could also be blacklisted ones in region 2, sure, but not the point)
        # for every blacklisted number in region 1 there is an un-blacklisted number in region 2
        # consider numbers 0...999 with 20 blacklists
        # so if all 20 are blacklisted in 0...979 then all 20 in 980...999 are free
        # if 5 are blacklisted in the left, 5 are free in the right
        # so we're just going to pick any number in region 1 and if it's blacklisted it gets mapped to a free one in region 2
        rightI = m
        while rightI in self.bset:
            rightI += 1
        self.mp = {}
        for i in range(len(blacklist)):
            bi = blacklist[i]
            self.mp[bi] = rightI
            rightI += 1
            while rightI in self.bset:
                rightI += 1
        self.m = m

    def pick(self) -> int:
        rand = random.randint(0,self.m-1)
        if rand not in self.bset:
            return rand
        return self.mp[rand]
        


# SOLUTION 2, O(log n * log B) per query
# import random

# class Solution:

#     def __init__(self, n: int, blacklist: List[int]):
#         self.n = n
#         self.blacklist = sorted(blacklist)

#     def pick(self) -> int:
#         # pick some number from 0...r as if these were all valid
#         rand = random.randint(0, self.n - len(self.blacklist) - 1) # so 10 numbers with 2 blacklisted, we want to pick 0...7

#         # say our random selection is 6, we want the 6th non-hole number
#         # lets find the smallest number X in the range 0...n-1 where (X - blacklisted<=X) is 6

#         def countBlacklistedLTE(x):
#             return bisect.bisect_right(self.blacklist, x)

#         l = 0
#         r = self.n - 1
#         res = None
#         while l <= r:
#             m = (l + r) // 2
#             diff = m - countBlacklistedLTE(m)
#             if diff > rand:
#                 # too big a number
#                 r = m - 1
#                 continue
#             if diff < rand:
#                 # too small a number
#                 l = m + 1
#             if diff == rand:
#                 res = m
#                 r = m - 1

#         return res

        
        


# # Your Solution object will be instantiated and called as such:
# # obj = Solution(n, blacklist)
# # param_1 = obj.pick()