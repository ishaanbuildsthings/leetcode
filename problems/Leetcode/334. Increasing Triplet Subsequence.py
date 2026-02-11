class Solution:
    def increasingTriplet(self, nums: List[int]) -> bool:
        smallest = inf
        smallTwo = inf
        for num in nums:
            if num > smallTwo:
                return True
            newSmallest = min(smallest, num)
            if num > smallest:
                smallTwo = min(smallTwo, num)
            smallest = newSmallest
        return False
            
            