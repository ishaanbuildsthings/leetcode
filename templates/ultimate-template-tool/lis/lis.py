# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/lis/lis.py

# Longest increasing / decreasing subsequence, O(n log n). Each function returns (length, one longest subsequence):
#   nums = [3, 1, 2, 2, 5, 4]
#   strictlyIncreasingLis(nums)  -> (3, [1, 2, 4])       each value > the one before
#   monoIncreasingLis(nums)      -> (4, [1, 2, 2, 4])    each value >= the one before
#   strictlyDecreasingLis(nums)  -> (2, [5, 4])          each value < the one before
#   monoDecreasingLis(nums)      -> (3, [3, 2, 2])       each value <= the one before
# Empty nums gives (0, []). Values can be any numbers.

from bisect import bisect_left, bisect_right


def _lis(nums, sign, allowEqual):
    # tails[k] = smallest possible last value (times sign) of a subsequence of length k + 1 seen so far
    find = bisect_right if allowEqual else bisect_left
    tails, tailsIndex = [], []
    prevIndex = [-1] * len(nums)
    for i, val in enumerate(nums):
        key = sign * val
        pos = find(tails, key)
        if pos == len(tails):
            tails.append(key)
            tailsIndex.append(i)
        else:
            tails[pos] = key
            tailsIndex[pos] = i
        if pos > 0:
            prevIndex[i] = tailsIndex[pos - 1]
    seq = []
    idx = tailsIndex[-1] if tailsIndex else -1
    while idx != -1:
        seq.append(nums[idx])
        idx = prevIndex[idx]
    seq.reverse()
    return len(seq), seq


# O(n log n) -- (length, subsequence) where each value is > the one before
def strictlyIncreasingLis(nums):
    return _lis(nums, 1, False)


# O(n log n) -- (length, subsequence) where each value is >= the one before
def monoIncreasingLis(nums):
    return _lis(nums, 1, True)


# O(n log n) -- (length, subsequence) where each value is < the one before
def strictlyDecreasingLis(nums):
    return _lis(nums, -1, False)


# O(n log n) -- (length, subsequence) where each value is <= the one before
def monoDecreasingLis(nums):
    return _lis(nums, -1, True)
