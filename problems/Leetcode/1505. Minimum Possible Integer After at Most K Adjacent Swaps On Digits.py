class Solution:
    def minInteger(self, num: str, k: int) -> str:
        n = len(num)
        
        # we want every digit stored in sorted order in one big SL, so we store:
        # [indexForKeepingSortedPositions, ...]
        sl = SortedList(list(range(n)))

        # now I will construct the answer one position at a time, trying smaller digits first
        # "can I bring a 1 to the front?"
        # we need the leftmost 1 that is still an option, and how many moves it takes to bring it to the left
        # its position in the big `sl` will literally tell us how far in the sl it is
        # sl.index(someValue) -> tells us the idx in the sl

        # to support these, we also bookkeep 10 deques for each digit, and the leftmost is just the active smallest one for that digit
        digitToDeque = [deque() for _ in range(10)]

        for i, v in enumerate(num):
            digitToDeque[int(v)].append(i)
        
        remainOps = k
        res = []
        for i in range(len(num)):
            for d in range(10):
                dq = digitToDeque[d]
                if not dq:
                    continue
                leftmostIdx = dq[0]
                posInBig = sl.index(leftmostIdx)
                if posInBig <= remainOps:
                    remainOps -= posInBig
                    sl.remove(leftmostIdx)
                    res.append(str(d))
                    dq.popleft()
                    break
                    
        return ''.join(res)