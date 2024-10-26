# https://leetcode.com/problems/number-of-senior-citizens/
# Difficulty: easy

# Problem
# You are given a 0-indexed array of strings details. Each element of details provides information about a given passenger compressed into a string of length 15. The system is such that:

# The first ten characters consist of the phone number of passengers.
# The next character denotes the gender of the person.
# The following two characters are used to indicate the age of the person.
# The last two characters determine the seat allotted to that person.
# Return the number of passengers who are strictly more than 60 years old.

# Solution, O(n*detail) time and O(1) space

class Solution:
    def countSeniors(self, details: List[str]) -> int:
        res = 0
        for detail in details:
            age = int(detail[11:13])
            res += age > 60
        return res