from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import bisect
import collections
from collections import defaultdict, Counter
import sortedcontainers
import heapq
from heapq import nlargest, nsmallest
from functools import cache
import itertools

# example format
# """Input: s = "1001", k = 3
# Output: 4"""
testcases = [
    """Input: s = "abcabc", queries = [[1,1,3,5],[0,2,5,5]]
Output: [True,True]""",
    """Input: s = "abbcdecbba", queries = [[0,2,7,9]]
Output: [False]""",
"""Input: s = "acbcab", queries = [[1,2,4,5]]
Output: [True]"""
]
