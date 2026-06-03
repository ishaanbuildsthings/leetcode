from functools import cmp_to_key
class Solution:
    def sortByReflection(self, nums: List[int]) -> List[int]:
        def cmp(a, b):
            aa = int(bin(a)[2:][::-1].lstrip('0'), 2)
            bb = int(bin(b)[2:][::-1].lstrip('0'), 2)
            if aa < bb:
                return -1
            if aa > bb:
                return 1
            if aa == bb:
                if a < b:
                    return -1
                if a > b:
                    return 1
            return 0
        nums.sort(key=cmp_to_key(cmp))
        return nums

        
            