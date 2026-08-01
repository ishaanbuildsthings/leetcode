# https://leetcode.com/problems/count-items-matching-a-rule/
# difficulty: easy

# problem
# You are given an array items, where each items[i] = [typei, colori, namei] describes the type, color, and name of the ith item. You are also given a rule represented by two strings, ruleKey and ruleValue.

# The ith item is said to match the rule if one of the following is true:

# ruleKey == "type" and ruleValue == typei.
# ruleKey == "color" and ruleValue == colori.
# ruleKey == "name" and ruleValue == namei.
# Return the number of items that match the given rule.

# Solution, O(n) time and O(1) space
class Solution:
    def countMatches(self, items: List[List[str]], ruleKey: str, ruleValue: str) -> int:
        res = 0
        for itemType, color, name in items:
            if ruleKey == 'type' and ruleValue == itemType:
                res += 1
            elif ruleKey == 'color' and ruleValue == color:
                res += 1
            elif ruleKey == 'name' and ruleValue == name:
                res += 1
        return res