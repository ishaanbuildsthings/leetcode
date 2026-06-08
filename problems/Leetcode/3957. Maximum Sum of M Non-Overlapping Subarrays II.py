fmax = lambda x, y: x if x > y else y
fmin = lambda x, y: x if x < y else y
class Solution:
    def maximumSum(self, nums: List[int], m: int, l: int, r: int) -> int:
        n = len(nums)
        
        suffSum = [None] * n
        suff = 0
        for i in range(n - 1, -1, -1):
            suff += nums[i]
            suffSum[i] = suff
        suffSum.append(0)
        
        pfSum = []
        curr = 0
        for v in nums:
            curr += v
            pfSum.append(curr)

        def withPenalty(y):
            # max score to partition 0...i with a subarray ending at i, into any amount of subarrays
            arr = [None] * n # the data at each index (maxPrefixScore + current exclusive suffix sum, max partitions used)

            # sl = SortedList() # holds (maxPrefixScore + exclusive suffix sum, maxPartitionsUsed)
            dq = deque() # will hold indices

            dp = [None] * n # the actual answer for each index, the max score we can get with a partition ending at i

            maxScore = 0
            maxParts = 0
            
            for i in range(n):
                LEFT = i - r # the leftmost possible previous right edge
                RIGHT = i - l
                # we would take some previous partition ending anywhere from [LEFT...RIGHT]

                if RIGHT >= 0:
                    # sl.add((arr[RIGHT]))
                    while dq and arr[dq[-1]] <= arr[RIGHT]:
                        dq.pop()
                    dq.append(RIGHT)
                if LEFT - 1 >= 0:
                    while dq and dq[0] < LEFT:
                        dq.popleft()
                    # sl.remove((arr[LEFT - 1]))
                
                # if sl:
                if dq:
                    # maxBefore, maxPartitions = sl[-1]
                    maxBefore, maxPartitions = arr[dq[0]]
                else:
                    maxBefore, maxPartitions = -inf, -inf
                
                entry = maxBefore - suffSum[i + 1] - y

                # if i can be the first subarray this is also an option
                if l - 1 <= i <= r - 1:
                    c = pfSum[i] - y
                    if c > entry:
                        entry, maxPartitions = c, 0

                if entry > maxScore:
                    maxScore = entry
                    maxParts = maxPartitions + 1
                elif entry == maxScore:
                    maxParts = fmax(maxParts, 1 + maxPartitions)
                
                
                arr[i] = maxScore + suffSum[i+1], maxParts
                dp[i] = entry, maxPartitions + 1

            mx = -inf
            parts = -inf
            for maxScore, partitionsUsed in dp:
                if maxScore > mx:
                    mx = maxScore
                    parts = partitionsUsed
                elif maxScore == mx:
                    parts = partitionsUsed
            
            return mx, parts
        
        maxSubarraySum = -inf
        pf = 0
        for v in nums:
            nsum = v + pf
            maxSubarraySum = fmax(maxSubarraySum, nsum)
            pf = fmax(0, pf + v)
            
        # binary search for the largest penalty where we still take >= m subarrays
        L = 0
        R = fmax(maxSubarraySum, 0)
        res = inf
        while L <= R:
            y = (L + R) // 2
            score, subarrays = withPenalty(y)
            trueScore = score + (m * y)
            res = fmin(res, trueScore)
            if subarrays >= m:
                L = y + 1
            else:
                R = y - 1
        
        return res