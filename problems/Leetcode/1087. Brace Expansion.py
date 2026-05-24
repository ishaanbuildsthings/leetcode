class Solution:
    def expand(self, s: str) -> List[str]:
        arr = []
        i = 0
        while i < len(s):
            if s[i] != '{':
                arr.append([s[i]])
                i += 1
                continue
            bucket = []
            while i < len(s) and s[i] != '}':
                if s[i].isalpha():
                    bucket.append(s[i])
                i += 1
            arr.append(sorted(bucket))
            i += 1
        
        res = []
        def backtrack(curr, i):
            if i == len(arr):
                res.append(''.join(curr))
                return
            bucket = arr[i]
            for option in bucket:
                curr.append(option)
                backtrack(curr, i + 1)
                curr.pop()
        backtrack([],0)
        return res

            