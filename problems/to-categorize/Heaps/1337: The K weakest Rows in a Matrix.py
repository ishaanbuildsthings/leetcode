# https://leetcode.com/problems/the-k-weakest-rows-in-a-matrix/description/?envType=daily-question&envId=2023-09-18
# Difficulty: Easy
# Tags: Heaps

# Problem
# You are given an m x n binary matrix mat of 1's (representing soldiers) and 0's (representing civilians). The soldiers are positioned in front of the civilians. That is, all the 1's will appear to the left of all the 0's in each row.

# A row i is weaker than a row j if one of the following is true:

# The number of soldiers in row i is less than the number of soldiers in row j.
# Both rows have the same number of soldiers and i < j.
# Return the indices of the k weakest rows in the matrix ordered from weakest to strongest.

# Solution, O(n*m + n*logk) time, O(n) space
# Iterate over n * m cells, getting a count and row index for each row. We then heapify the rows, and pop k times.

class Solution:
    def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
        HEIGHT = len(mat)
        WIDTH = len(mat[0])

        # create an array of tuples [number of soldiers, index]
        counts = []

        for r in range(HEIGHT):
            soldierCount = 0
            for c in range(WIDTH):
                if mat[r][c] == 1:
                    soldierCount += 1
            counts.append([soldierCount, r])

        heapq.heapify(counts)

        result = []
        for i in range(k):
            tup = heapq.heappop(counts)
            count, index = tup
            result.append(index)

        return result