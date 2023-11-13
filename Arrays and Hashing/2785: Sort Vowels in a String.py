# https://leetcode.com/problems/sort-vowels-in-a-string/description/?envType=daily-question&envId=2023-11-13
# difficulty: medium

# Problem
# Given a 0-indexed string s, permute s to get a new string t such that:

# All consonants remain in their original places. More formally, if there is an index i with 0 <= i < s.length such that s[i] is a consonant, then t[i] = s[i].
# The vowels must be sorted in the nondecreasing order of their ASCII values. More formally, for pairs of indices i, j with 0 <= i < j < s.length such that s[i] and s[j] are vowels, then t[i] must not have a higher ASCII value than t[j].
# Return the resulting string.

# The vowels are 'a', 'e', 'i', 'o', and 'u', and they can appear in lowercase or uppercase. Consonants comprise all letters that are not vowels.

# Solution, O(n) time, O(n) space as we hold an array. I placed the consonants, counted the vowels, then filled in the vowels in a sorted order.

VOWELS = set(['a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U'])
class Solution:
    def sortVowels(self, s: str) -> str:
        counts = defaultdict(int)
        res = []
        for char in s:
            if char not in VOWELS:
                res.append(char)
            else:
                res.append(None)
                counts[char] += 1

        sortedKeys = sorted(counts.keys())
        keyP = 0

        for i in range(len(res)):
            if res[i] != None:
                continue
            nextChar = sortedKeys[keyP]
            res[i] = nextChar
            counts[nextChar] -= 1
            if counts[nextChar] == 0:
                keyP += 1

        return ''.join(res)
