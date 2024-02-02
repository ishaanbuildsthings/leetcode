# https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters/description/?envType=daily-question&envId=2024-01-23
# difficulty: medium
# tags: backtracking

# I'm just adding this later won't analyze there might be optimizations

class Solution:
    def maxLength(self, arr: List[str]) -> int:
        def backtrack(seenChars, length, i):
            # base
            if i == len(arr):
                return length

            # if we skip this
            res = backtrack(seenChars, length, i + 1)

            # if we take this
            if all(char not in seenChars for char in arr[i]) and len(set(arr[i])) == len(arr[i]):
                for char in arr[i]:
                    seenChars.add(char)
                newLength = length + len(arr[i])
                res = max(res, backtrack(seenChars, newLength, i + 1))
                for char in arr[i]:
                    seenChars.remove(char)

            return res

        return backtrack(set(), 0, 0)
