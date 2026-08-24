class Solution:
    def findStrobogrammatic(self, n: int) -> List[str]:
        res = []

        def backtrack(curr, i):
            if not n % 2 and i >= n // 2:
                res.append(curr[:])
                return
            if n % 2 and i == n // 2:
                curr[n//2] = '1'
                res.append(curr[:])
                curr[n//2] = '0'
                res.append(curr[:])
                curr[n//2] = '8'
                res.append(curr[:])
                return
            right = n - i - 1
            curr[i] = '1'
            curr[right] = '1'
            backtrack(curr, i + 1)
            curr[i] = '6'
            curr[right] = '9'
            backtrack(curr, i + 1)
            curr[i] = '9'
            curr[right] = '6'
            backtrack(curr, i + 1)
            if i != 0 or n == 1:
                curr[i] = '0'
                curr[right] = '0'
                backtrack(curr, i + 1)
            curr[i] = '8'
            curr[right] = '8'
            backtrack(curr, i + 1)
        
        backtrack([None] * n, 0)
        return [''.join(arr) for arr in res if int(''.join(arr)) != 0 or ''.join(arr) == '0']