# https://leetcode.com/problems/average-salary-excluding-the-minimum-and-maximum-salary/
# difficulty: easy

# Problem
# You are given an array of unique integers salary where salary[i] is the salary of the ith employee.

# Return the average salary of employees excluding the minimum and maximum salary. Answers within 10-5 of the actual answer will be accepted.

# Solution, O(n) time and O(1) space, can do in one pass
class Solution:
    def average(self, salary: List[int]) -> float:
        total = sum(salary) - max(salary) - min(salary) # can do in one pass lol
        return total / (len(salary) - 2)