# https://leetcode.com/problems/employee-importance/
# difficulty: medium
# tags: dfs

# # problem
# You have a data structure of employee information, including the employee's unique ID, importance value, and direct subordinates' IDs.

# You are given an array of employees employees where:

# employees[i].id is the ID of the ith employee.
# employees[i].importance is the importance value of the ith employee.
# employees[i].subordinates is a list of the IDs of the direct subordinates of the ith employee.
# Given an integer id that represents an employee's ID, return the total importance value of this employee and all their direct and indirect subordinates.

# Solution, O(n) time and space
# First, map each id to an index in the employee array. Then dfs down on the each id and get the sum.

"""
# Definition for Employee.
class Employee:
    def __init__(self, id: int, importance: int, subordinates: List[int]):
        self.id = id
        self.importance = importance
        self.subordinates = subordinates
"""

class Solution:
    def getImportance(self, employees: List['Employee'], id: int) -> int:
        idToIndex = {}
        for i in range(len(employees)):
            employee = employees[i]
            idToIndex[employee.id] = i

        def dfs(id):
            rootIndex = idToIndex[id]
            employee = employees[rootIndex]
            children = employee.subordinates
            sumForThis = employee.importance
            for childId in children:
                sumForThis += dfs(childId)
            return sumForThis

        return dfs(id)