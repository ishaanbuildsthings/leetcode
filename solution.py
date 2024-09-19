from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import bisect
import collections
from collections import defaultdict, Counter
# import sortedcontainers
import heapq
from heapq import nlargest, nsmallest
from functools import cache
import itertools
from math import inf


testcases = ["""Input: nums = [-2,0,1,3], target = 2
Output: 2"""]


class Solution:
    def threeSumSmaller(self, nums: List[int], target: int) -> int:
        if len(nums) < 3:
            return 0
        c = Counter(nums)
        big = max(nums)
        small = min(nums)

        pf = {} # maps a number to the amount of numbers <= to that
        curr = 0
        for num in range(small, big + 1):
            curr += c[num]
            pf[num] = curr

        print(f'pf is: {pf}')

        def query(l, r):
            print(f'querying l={l} r={r}')
            if l - 1 in pf:
                return pf[r] - pf[l - 1]
            return pf[r]

        res = 0
        for smallest in range(small, big + 1):
            for medium in range(smallest, big + 1):
                if not c[smallest] or not c[medium]:
                    continue
                print(f'_____')
                print(f'iter on smallest={smallest} medium={medium}')
                biggestAllowedThird = target - (smallest + medium) - 1
                print(f'biggest allowed third: {biggestAllowedThird}')
                if biggestAllowedThird > big or biggestAllowedThird < medium:
                    print(f'too big, breaking')
                    continue
                countAtMedium = 1 if smallest != medium else 2
                availableThird = query(medium, biggestAllowedThird) - countAtMedium
                print(f'availableThird is: {availableThird}')
                cSmallest = c[smallest]
                cMedium = c[medium]

                firstTwo = cSmallest * cMedium if smallest != medium else cSmallest * (cSmallest - 1)
                thirdMult = firstTwo * availableThird
                res += thirdMult
                print(f'added: {thirdMult} to res')

        return res

        # solution 0
        # n^3

        # solution 1
        # t^3 complexity

        # solution 2
        # n^2 loop, sum those two, range query prefix for t, so n^2 time

        # solution 3
        # t^2 loop, range query for third t = t^2 time?

        # solution 4
        # sort + 2 p = n^3 time

        # solution 5
        #
