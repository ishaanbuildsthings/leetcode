class Solution:
    def minSwaps(self, s: str) -> int:
        o = s.count('1')
        z = s.count('0')
        if max(o, z) - min(o, z) > 1:
            return -1
        
        if len(s) % 2:
            mx = 1 if o > z else 0
            mismatches = 0
            for i in range(len(s)):
                target = mx if i % 2 == 0 else mx^1
                mismatches += int(s[i]) != target
            return int(mismatches / 2)
        
        # assume 0 goes first, count mismatches
        mismatches = 0
        for i in range(len(s)):
            target = 0 if i % 2 == 0 else 1
            mismatches += int(s[i]) != target
        
        mismatches = min(mismatches, len(s) - mismatches)
        return int(mismatches / 2)
        