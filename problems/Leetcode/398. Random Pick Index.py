class Solution:

    def __init__(self, nums: List[int]):
        self.indices = defaultdict(list) # maps a number to a list of its indices
        for i, num in enumerate(nums):
            self.indices[num].append(i)

    def pick(self, target: int) -> int:
        possibleIndices = self.indices[target]
        randInt = random.randint(0, len(possibleIndices) - 1)
        return possibleIndices[randInt]
        


# Your Solution object will be instantiated and called as such:
# obj = Solution(nums)
# param_1 = obj.pick(target)