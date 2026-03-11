class Solution:
    def longestRepeatingSubstring(self, s: str) -> int:
        BASE = 26
        MOD = 10 ** 9 + 7
        arr = [ord(c) - 96 for c in s]

        def hasRepeat(length):
            if length == 0:
                return False
            currentHash = 0
            for i in range(length):
                currentHash = (currentHash * BASE + arr[i]) % MOD
            seen = {currentHash}
            maxPow = pow(BASE, length - 1, MOD)
            for left in range(1, len(arr) - length + 1):
                currentHash = (currentHash - arr[left - 1] * maxPow) % MOD
                currentHash = (currentHash * BASE + arr[left + length - 1]) % MOD
                if currentHash in seen:
                    return True
                seen.add(currentHash)
            return False

        l, r = 1, len(s) - 1
        while l <= r:
            m = (l + r) // 2
            if hasRepeat(m):
                l = m + 1
            else:
                r = m - 1
        return max(r, 0)