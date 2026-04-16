class Solution:
    def waysToPartition(self, nums: List[int], k: int) -> int:
        n = len(nums)
        tot = sum(nums)

        # first check if we dont change any
        noChanges = 0
        pf = 0
        for i, v in enumerate(nums):
            pf += v
            rightRegion = tot - pf
            if pf == rightRegion and i < n - 1:
                noChanges += 1
        

        # now if I change a number we get a new left range surplus
        # how many prefixes >= i have some old diff

        # how many prefixes < i have some old diff

        leftSurplus = [0] * n
        pf = 0
        for i, v in enumerate(nums):
            pf += v
            rightRegion = tot - pf
            leftAbove = pf - rightRegion
            leftSurplus[i] = leftAbove
        
        leftSurplus[-1] = inf # this would never be valid so setting it to some sentinel

        rightSurplus = [0] * n
        pf = 0
        for i, v in enumerate(nums):
            leftRegion = pf
            rightRegion = tot - pf
            rightAbove = rightRegion - leftRegion
            rightSurplus[i] = rightAbove
            pf += v

        rightSurplus[0] = inf  # i=0 means empty left, invalid

        res = noChanges

        rightWindow = Counter(leftSurplus)
        leftWindow = Counter()

        for i, v in enumerate(nums):
            newGain = k - v
            # say old left surplus was 10
            # after changing this to k, its now 15
            # previously we wanted old left surplus of 0 somewhere
            # now we want a left surplus of -5, somewhere >= i
            # find how many (oldSurplus - newSurplus) are >= i
            count1 = 0
            if i < n - 1:
                oldSurplus = leftSurplus[i]
                
                newSurplus = oldSurplus + newGain
                findRight = oldSurplus - newSurplus
                count1 = rightWindow[findRight]

                rightWindow[oldSurplus] -= 1

            # now imagine we change i but its on the right
            # say old right surplus was 10
            # after changing this to k, its now 15
            # previously we wanted old right surplus of 0 somewhere
            # now we want a right surplus of -5, somewhere < i
            # find how many (oldSurplus - newSurplus) are < i
            count2 = 0
            if i:
                leftWindow[rightSurplus[i]] += 1
                oldSurplus = rightSurplus[i]
                newSurplus = oldSurplus + newGain
                findLeft = oldSurplus - newSurplus
                count2 = leftWindow[findLeft]

            res = max(res, count1 + count2)
        
        return res