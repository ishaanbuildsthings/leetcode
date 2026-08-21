# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant
import math

class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        if n == 0:
            self.sparse = []
            self.combineFn = combineFn
            self.log2 = [0]
            return

        BITS = n.bit_length()

        sparse = [[0] * n for _ in range(BITS)]
        sparse[0] = nums[:]

        for log in range(1, BITS):
            half = 1 << (log - 1)
            length = 1 << log
            limit = n - length + 1
            rowPrev = sparse[log - 1]
            row = sparse[log]
            for left in range(limit):
                row[left] = combineFn(rowPrev[left], rowPrev[left + half])

        self.sparse = sparse
        self.combineFn = combineFn

        log2 = [0] * (n + 1)
        for i in range(2, n + 1):
            log2[i] = log2[i >> 1] + 1
        self.log2 = log2

    def query(self, l, r):
        width = r - l + 1
        power = self.log2[width]
        windowWidth = 1 << power
        leftAnswer = self.sparse[power][l]
        rightAnswer = self.sparse[power][r - windowWidth + 1]
        return self.combineFn(leftAnswer, rightAnswer)

class Solution:
    def maxSubstringLength(self, s: str) -> int:
        res = -1
        n = len(s)
        rightmost = {}
        for i in range(n - 1, -1, -1):
            if s[i] not in rightmost:
                rightmost[s[i]] = i
        
        nums = []
        for v in s:
            nums.append(1 << (ord(v) - ord('a')))
        
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        
        sparse = SparseTable(nums, lambda x , y : x | y)

        for l in range(n):
            r = l
            while True:
                mask = sparse.query(l, r)
                before = sparse.query(0, l - 1) if l else 0
                if mask & before:
                    break
                jump = r
                for letter in ABC:
                    bit = 1 << (ord(letter) - ord('a'))
                    if not (mask & bit):
                        continue
                    jump = max(jump, rightmost[letter])
                if jump == r:
                    width = r - l + 1
                    if width != n:
                        res = max(res, width)
                    r += 1
                else:
                    r = jump
                if r == n:
                    break

        return res
                
                    
                    

