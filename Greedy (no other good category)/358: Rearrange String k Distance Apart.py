# https://leetcode.com/problems/rearrange-string-k-distance-apart/description/
# Difficulty: Hard
# Tags: Greedy

# Problem
# Given a string s and an integer k, rearrange s such that the same characters are at least distance k from each other. If it is not possible to rearrange the string, return an empty string "".

# Solution, O(26n) time, O(26n) space
# Get a count of each letter. Track the latest occurence of each letter. Pick the most common letter, update the occurence, and repeat. We use space since the array exists which is not the result.

class Solution:
    def rearrangeString(self, s: str, k: int) -> str:
        counts = collections.Counter(s)
        most_recent = collections.defaultdict(lambda: None) # maps a letter to the latest index it was used

        result_arr = []

        # each iteration we should take the most common letter that has not been used
        for i in range (len(s)):
            change_found = False
            for letter, count in counts.most_common():
                # if that letter is at least k away and has enough, remove and update
                if (most_recent[letter] == None or i - most_recent[letter] >= k) and counts[letter] > 0:
                    counts[letter] -= 1
                    most_recent[letter] = i
                    result_arr.append(letter)
                    change_found = True
                    break
            if not change_found:
                return ''

        return ''.join(result_arr)

