class Solution:
    def findEvenNumbers(self, digits: List[int]) -> List[int]:
        c = Counter(digits)
        res = []
        curr = []
        def backtrack(curr):
            if len(curr) == 3:
                num = curr[0] * 100 + curr[1] * 10 + curr[2]
                if num % 2 == 0:
                    res.append(num)
                return
            
            for digit in sorted(c):
                if digit == 0 and not curr:
                    continue
                if c[digit]:
                    curr.append(digit)
                    c[digit] -= 1
                    backtrack(curr)
                    c[digit] += 1
                    curr.pop()
        
        backtrack(curr)
        return res
