# https://leetcode.com/problems/sort-the-people/description/
# difficulty: easy

# Problem
# You are given an array of strings names, and an array heights that consists of distinct positive integers. Both arrays are of length n.

# For each index i, names[i] and heights[i] denote the name and height of the ith person.

# Return names sorted in descending order by the people's heights.

# Solution, O(n log n) time, O(n) space
# zip and sort!

class Solution:
    def sortPeople(self, names: List[str], heights: List[int]) -> List[str]:
        zipped = [[heights[i], names[i]] for i in range(len(names))]
        zipped.sort(reverse=True)
        return [tup[1] for tup in zipped]