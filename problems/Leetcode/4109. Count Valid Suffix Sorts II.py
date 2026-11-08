# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

# Z-function: z[i] = length of the longest common prefix of the whole sequence and the suffix starting at i
# works on any indexable sequence of comparable items (string, list, tuple)


# zFunction("aabxaab") -> [7, 1, 0, 0, 3, 1, 0]   # z[0] is the full length
# zFunction([1, 2, 1, 2]) -> [4, 0, 2, 0]
# O(n) time, O(n) space
def zFunction(arrOrString):
    n = len(arrOrString)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and arrOrString[z[i]] == arrOrString[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


# For every index of text, the length of the longest prefix of pattern that starts there.
# longestPrefixMatches("xaabaa", "aab") -> [0, 3, 1, 0, 2, 1]
# O(n + m) time
def longestPrefixMatches(text, pattern):
    m = len(pattern)
    z = zFunction(pattern + text)
    return [min(z[m + i], m) for i in range(len(text))]


# Every start index in text where pattern occurs (overlaps included), ascending.
# findMatches("ababa", "aba") -> [0, 2]
# findMatches([1, 2, 1, 2], [1, 2]) -> [0, 2]
# O(n + m) time
def findMatches(text, pattern):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    z = zFunction(pattern + text)
    return [i for i in range(len(text)) if z[m + i] >= m]


class Solution:
    def countSuffix(self, nums: list[int], target: list[int]) -> list[int]:
        vToRand = {v : random.randint(1, 10**12) for v in set(nums + target)}
        pfNums = list(accumulate(vToRand[v] for v in nums))
        pfTarget = list(accumulate(vToRand[v] for v in target))
                
        def query(l, r, pf):
            return pf[r] - (pf[l - 1] if l else 0)
        
        @cache
        def incLeft(i):
            return i if not i or target[i - 1] < target[i] else incLeft(i - 1)
        
        z = longestPrefixMatches(target, nums)

        res = [0] * (len(target) - len(nums) + 1)
        for i in range(len(target) - len(nums) + 1):
            if query(i + z[i], i + len(nums) - 1, pfTarget) != query(z[i], len(nums) - 1, pfNums): continue
            hi = min(z[i], len(nums) - 1)
            sortedFrom = max(incLeft(i + len(nums) - 1), i) - i
            res[i] = max(0, hi - sortedFrom + 1)
        
        return res
        
