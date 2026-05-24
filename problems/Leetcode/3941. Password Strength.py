class Solution:
    def passwordStrength(self, password: str) -> int:
        res = 0
        seen = set()
        for v in password:
            if v.isalpha() and v == v.lower() and v not in seen:
                res += 1
                seen.add(v)
                continue

            if v.isalpha() and v == v.upper() and v not in seen:
                res += 2
                seen.add(v)
                continue

            if v in '0123456789' and v not in seen:
                res += 3
                seen.add(v)
                continue

            if v not in seen:
                res += 5
                seen.add(v)
            
        return res