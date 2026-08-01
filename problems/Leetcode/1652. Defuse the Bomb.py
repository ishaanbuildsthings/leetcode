class Solution:
    def decrypt(self, code: List[int], k: int) -> List[int]:
        prefix = []
        running = 0
        for num in code:
            running += num
            prefix.append(running)
        
        def query(l, r):
            right = prefix[r]
            left = prefix[l - 1] if l > 0 else 0
            return right - left
        
        res = []
        for i in range(len(code)):
            num = code[i]
            if k == 0:
                res.append(0)
            elif k > 0:
                rightAvail = len(code) - i - 1
                takeFromRight = min(k, rightAvail)
                missingFromRight = k - takeFromRight
            takeFromLeft = missingFromRight
                rightSum = query(i + 1, i + takeFromRight)
                leftSum = query(0, takeFromLeft - 1) if takeFromLeft else 0
                res.append(leftSum + rightSum)
            else:
                leftAvail = i
                takeFromLeft = min(abs(k), leftAvail)
                missingFromLeft = abs(k) - takeFromLeft
                takeFromRight = missingFromLeft
                leftSum = query(i - takeFromLeft, i - 1) if takeFromLeft else 0
                rightSum = query(len(code) - takeFromRight, len(code) - 1) if takeFromRight else 0
                res.append(leftSum + rightSum)
        
        return res