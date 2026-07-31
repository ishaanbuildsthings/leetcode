class Solution:
    def canBeEqual(self, target: List[int], arr: List[int]) -> bool:
        # target.sort()
        # arr.sort()
        # return all(t == a for t, a in zip(target, arr)) # can forego the zip and use O(1) space sort
        return Counter(target) == Counter(arr)