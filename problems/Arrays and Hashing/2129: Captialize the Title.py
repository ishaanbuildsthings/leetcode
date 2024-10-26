# https://leetcode.com/problems/capitalize-the-title/
# difficulty: easy

# problem
# You are given a string title consisting of one or more words separated by a single space, where each word consists of English letters. Capitalize the string by changing the capitalization of each word such that:

# If the length of the word is 1 or 2 letters, change all letters to lowercase.
# Otherwise, change the first letter to uppercase and the remaining letters to lowercase.
# Return the capitalized title.

# Solution, O(num words) time, O(title) space

class Solution:
    def capitalizeTitle(self, title: str) -> str:
        arr = title.split(' ')
        print(arr)
        res = []
        for word in arr:
            if len(word) <= 2:
                res.append(word.lower())
            else:
                res.append(word[0].upper() + word[1:].lower())
        return ' '.join(res)