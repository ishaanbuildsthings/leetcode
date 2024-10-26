# https://leetcode.com/problems/reverse-words-in-a-string-iii/?envType=daily-question&envId=2023-10-01
# difficulty: easy

# problem
# Given a string s, reverse the order of characters in each word within a sentence while still preserving whitespace and initial word order.

# solution
class Solution:
    def reverseWords(self, s: str) -> str:
        words = s.split(' ')
        resArr = []
        for word in words:
            resArr.append(word[::-1])
        return ' '.join(resArr)
