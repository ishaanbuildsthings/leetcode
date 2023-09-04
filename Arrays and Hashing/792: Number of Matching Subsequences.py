# https://leetcode.com/problems/number-of-matching-subsequences/description/
# Difficulty: Medium
# tags: prefix

# Problem
# Given a string s and an array of strings words, return the number of words[i] that is a subsequence of s.

# A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

# For example, "ace" is a subsequence of "abcde".

# Solution, O(26n + words * len(word)) time and O(26n) space
# Start from the right, for each index record the closest to the right letter for each letter. Then, for each word, we do an O(len(word)) check by jumping to the closest relevant letter.

class Solution:
    def numMatchingSubseq(self, s: str, words: List[str]) -> int:
        # for each index, we need to know the closest index to the right that contains a letter, for every letter
        on_right = {} # maps an index to a {} closest to the right map

        closest_letters = collections.defaultdict(lambda: -1)
        n = len(s)
        for i in range(n - 1, -1, -1):
            on_right[i] = copy.copy(closest_letters)
            char = s[i]
            closest_letters[char] = i

        result = 0

        for word in words:
            index = 0 # where we are in s
            letters_found_in_word = 0
            # edge case
            if len(word) > len(s):
                continue
            for char in word:
                # edge case, it is possible our index went out of bounds
                if index == len(s):
                    break
                # if the letter we are at in s is the letter we desire, we can increment our index by 1, and go to the next letter
                if s[index] == char:
                    index += 1
                    letters_found_in_word += 1
                    continue

                # if there is an available letter to the right, move 1 index to the right of that
                mapping = on_right[index]
                if mapping[char] != -1:
                    index = mapping[char] + 1
                    letters_found_in_word += 1
                else:
                    break


            if letters_found_in_word == len(word):
                result += 1


        return result

