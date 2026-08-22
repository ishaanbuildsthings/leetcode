class Solution:
    def maxTotalFruits(self, fruits: List[List[int]], startPos: int, k: int) -> int:
        fruitMap = defaultdict(int) # maps position to how many fruits are there
        for pos, amount in fruits:
            fruitMap[pos] += amount

        prefixLeft = [0] # prefixLeft[steps] tells us how much fruit we gain going that many steps left, except for if we have fruits at our index
        runningLeft = 0
        for leftPos in range(startPos - 1, startPos - k - 1, -1):
            runningLeft += fruitMap[leftPos]
            prefixLeft.append(runningLeft)
        
        prefixRight = [0]
        runningRight = 0
        for rightPos in range(startPos + 1, startPos + k + 1):
            runningRight += fruitMap[rightPos]
            prefixRight.append(runningRight)

        res = 0
        for walkLeft in range(k + 1):
            doubledLeft = walkLeft * 2
            remainingSteps = max(0, k - doubledLeft)
            fruitsFromLeft = prefixLeft[walkLeft]
            fruitsFromRight = prefixRight[remainingSteps]
            totalFruits = fruitsFromLeft + fruitsFromRight
            res = max(res, totalFruits)
        for walkRight in range(k + 1):
            doubledRight = walkRight * 2
            remainingSteps = max(0, k - doubledRight)
            fruitsFromRight = prefixRight[walkRight]
            fruitsFromLeft = prefixLeft[remainingSteps]
            totalFruits = fruitsFromRight + fruitsFromLeft
            res = max(res, totalFruits)
        res += fruitMap[startPos]
        return res