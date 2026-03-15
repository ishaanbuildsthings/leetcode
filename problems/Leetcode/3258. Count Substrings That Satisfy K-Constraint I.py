class Solution:
    def countKConstraintSubstrings(self, s: str, k: int) -> int:
        l = r = res = z = o = 0
        while r < len(s):
            z += s[r] == '0'
            o += s[r] == '1'
            while z > k and o > k:
                z -= s[l] == '0'
                o -= s[l] == '1'
                l += 1
            res += r - l + 1
            r += 1
        return res