# classic inverted sliding window (find the largest contiguous window we can remove)
# can also do take 0 from left, figure out how many to take from right, etc, for all possible amounts to take from left

class Solution:
    def takeCharacters(self, s: str, k: int) -> int:
        c = Counter(s)
        if any(c[key] < k for key in 'abc'):
            return -1

        curr = Counter()
        l = r = 0

        # res is the longest subarray where, when removed, all the tot-subarray counts are at least k
        res = float('-inf')
        while r < len(s):
            newChar = s[r]
            curr[newChar] += 1
            while any(c[key] - curr[key] < k for key in c):
                lostChar = s[l]
                curr[lostChar] -= 1
                l += 1
            res = max(res, r - l + 1)
            r += 1
        if res == 0:
            if all(c[key] >= k for key in 'abc'):
                return 3*k
            return -1
        
        return len(s) - res
        

        # s = 'aaaaa'

        # we have taken out 2: 'aa'

        # we need at least 4 on the edges, so we are invalid

        # while the count 5 - what we took out < required