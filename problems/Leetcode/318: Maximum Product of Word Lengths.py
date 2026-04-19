# https://leetcode.com/problems/maximum-product-of-word-lengths/description/
# difficulty: medium
# tags: functional

# Problem
# Given a string array words, return the maximum value of length(word[i]) * length(word[j]) where the two words do not share common letters. If no such two words exist, return 0.

# Solution
# First get the letters that appear in each word since a word is long, we could probably manually write a loop to terminate early if all 26 were found. Then for every two words, update result if the intersection of the two sets is empty. # O(chars) time for the hashmap creation and O(26*words length) for the space, O(words^2 * 26) time for the set interesctions

class Solution:
    def maxProduct(self, words: List[str]) -> int:
        letters = {
            i : set(words[i]) for i in range(len(words))
        }

        res = 0
        for i in range(len(words) - 1):
            for j in range(i + 1, len(words)):
                res = max(
                    res,
                    len(words[i]) * len(words[j])
                    if len(letters[i] & letters[j]) == 0
                    else 0
                )
        return res