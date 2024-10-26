# https://leetcode.com/problems/minimum-operations-to-make-array-equal/
# difficulty: medium
# tags: math

# Problem
# You have an array arr of length n where arr[i] = (2 * i) + 1 for all valid values of i (i.e., 0 <= i < n).

# In one operation, you can select two indices x and y where 0 <= x, y < n and subtract 1 from arr[x] and add 1 to arr[y] (i.e., perform arr[x] -=1 and arr[y] += 1). The goal is to make all the elements of the array equal. It is guaranteed that all the elements of the array can be made equal using some operations.

# Given an integer n, the length of the array, return the minimum number of operations needed to make all the elements of arr equal.

# Solution, O(1) time and space, reduces to a closed form solution

class Solution:
    def minOperations(self, n: int) -> int:
        # 1 3 5 7 9 11 13 15

        # 1 3 5 7 9, pair up (3, 7), (1, 9), etv

        # 1 3 5 7 9 11

        if n % 2 == 0:
           nth = int(n / 2) # nth square
           return nth * nth
        else:
            nth = int((n-1) / 2) # nth square
            return nth * nth + nth


        # 1 3 5 7 9 11 13


        # 1->0
        #           2->1
        # 3->2
        #           4->1+3
        # 5->2+4
        #           6->1+3+5
        # 7-> 2+4+6=12



