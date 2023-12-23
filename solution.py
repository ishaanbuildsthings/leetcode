from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import bisect
import collections
from collections import defaultdict, Counter
import sortedcontainers
import heapq
from heapq import nlargest, nsmallest
from functools import cache


# PREPROCESSING OR TEMPLATES GO HERE



testcases = [
'Input: word1 = "sea", word2 = "eat"'
]

expectedResults = [
2,
]

class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        @cache
        def dp(i, j):
            # base
            if i == len(word1):
                return len(word2) - j
            if j == len(word2):
                return len(word1) - i

            if word1[i] == word2[j]:
                return dp(i + 1, j + 1)

            return min(
                dp(i + 1, j),
                dp(i, j + 1),
            ) + 1

        return dp(0, 0)