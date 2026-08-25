# https://leetcode.com/problems/k-th-smallest-prime-fraction/
# difficulty: medium

# Problem
# You are given a sorted integer array arr containing 1 and prime numbers, where all the integers of arr are unique. You are also given an integer k.

# For every i and j where 0 <= i < j < arr.length, we consider the fraction arr[i] / arr[j].

# Return the kth smallest fraction considered. Return your answer as an array of integers of size 2, where answer[0] == arr[i] and answer[1] == arr[j].

# Solution, writing this long after solving it. I think I had a note that I wanted to try a different or faster solution maybe.

class Solution:
    def kthSmallestPrimeFraction(self, arr: List[int], k: int) -> List[int]:
        # stores tuples [fraction, arr[i], arr[j]]
        data = []
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                frac = arr[i] / arr[j]
                data.append([frac, arr[i], arr[j]])
        data.sort()
        return [data[k - 1][1], data[k - 1][2]]



# each row is sorted, but not necessarily each column

# 1 a b c d
# 2 e f g h
# 3 i j k l
# 5 m n o p
#   1 2 3 5


# 1        0.5  0.33  0.2
# 2              0.66  0.4
# 3                    0.6
# 5
#       1    2    3    5