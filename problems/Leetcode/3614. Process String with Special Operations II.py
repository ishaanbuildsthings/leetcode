class Solution:
    def processStr(self, s: str, inputK: int) -> str:
        
        size = 0
        for i, v in enumerate(s):
            if v == '*':
                size = max(0, size - 1)
            elif v == '#':
                size *= 2
            elif v.isalpha():
                size += 1
        
        if inputK >= size:
            return '.'

        # this is the state after the operation ran, like size is after the i-th operation
        def recurse(i, size, k):
            if i == -1:
                return '.'

            op = s[i]
            if op.isalpha():
                if k == size - 1:
                    return op
                return recurse(i - 1, size - 1, k)

            elif op == '#':
                if k < size // 2:
                    return recurse(i - 1, size // 2, k)
                return recurse(i - 1, size // 2, k - size // 2)
            
            elif op == '%':
                return recurse(i - 1, size, size - 1 - k)
            
            elif op == '*':
                return recurse(i - 1, size + 1, k)
        
        return recurse(len(s) - 1, size, inputK)
            