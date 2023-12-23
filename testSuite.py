from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import collections

outputs = {
#   ((2,3,3,2,2), 2, 2): 11,
#   # (4, 5, 6): 15,
}

class Solution:
   pass
    # def countDistinct(self, nums: List[int], k: int, p: int) -> int:
    #     pf = [] # number of elements divisible by p
    #     count = 0
    #     for num in nums:
    #         count += (num / p) == math.floor(num / p)
    #         pf.append(count)
    #     print(pf)

    #     def queryDivis(l, r):
    #         if l == 0:
    #             return pf[r]
    #         return pf[r] - pf[l - 1]

    #     seen = set() # stores hashes

    #     res = 0
    #     for l in range(len(nums)):
    #         hash = 0
    #         for r in range(l, len(nums)):
    #             hash *= 200
    #             hash += nums[r]
    #             countDivis = queryDivis(l, r)
    #             res += countDivis <= k and not hash in seen
    #             seen.add(hash)
    #     return res


sol = Solution()

def find_solution_method(sol):
    for attr_name in dir(sol):
        if callable(getattr(sol, attr_name)) and not attr_name.startswith("__"):
            return getattr(sol, attr_name)
    return None

def main(arguemnts):
  return find_solution_method(sol)(*arguemnts)


for arguments in outputs:
  print(f'result: {main(arguments)}, expected: {outputs[arguments]}')



