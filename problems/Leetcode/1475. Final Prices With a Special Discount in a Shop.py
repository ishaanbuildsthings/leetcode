class Solution:
    def finalPrices(self, prices: List[int]) -> List[int]:
        # can probably do O(1) space by re-using stack and abusing integers lol
        
        stack = [0] # strictly increasing, holds indices only
        biggestOnRightLT = {} # maps index to value
        for i in range(1, len(prices)):            
            while stack and prices[i] <= prices[stack[-1]]:
                poppedI = stack.pop()
                biggestOnRightLT[poppedI] = prices[i]
            stack.append(i)

        res = []
        for i in range(len(prices)):
            if not i in biggestOnRightLT:
                res.append(prices[i])
                continue
            res.append(prices[i] - biggestOnRightLT[i])
        return res