class Solution:
    def gcdOfStrings(self, str1: str, str2: str) -> str:
        sz = min(len(str1), len(str2))

        for size in range(sz, 0, -1):
            if len(str1) % size or len(str2) % size:
                continue
            if str1[:size] != str2[:size]:
                continue
            dupe1 = (len(str1) // size) * str1[:size]
            dupe2 = (len(str2) // size) * str2[:size]
            if dupe1 == str1 and dupe2 == str2:
                return str1[:size]
        
        return ''