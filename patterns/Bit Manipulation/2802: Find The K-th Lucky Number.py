# https://leetcode.com/problems/find-the-k-th-lucky-number/description/
# difficulty: medium
# tags: bit manipulation

# Solution, O(log k) time and space

class Solution:
    def kthLuckyNumber(self, k: int) -> str:
        return bin(k + 1)[3:].replace('0', '4').replace('1', '7')


        # 0 -> 4
        # 1 -> 7
        # 2 -> 44
        # 3 -> 47