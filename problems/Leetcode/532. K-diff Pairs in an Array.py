class Solution:
    def findPairs(self, nums: List[int], k: int) -> int:
        unique = set()
        seen = set()
        for num in nums:
            target1 = num + k
            target2 = num - k
            if target1 in seen:
                unique.add( (min(target1, num), max(target1, num)) )
            if target2 in seen:
                unique.add( (min(target2, num), max(target2, num)) )
            seen.add(num)
        return len(unique)



            # 10 6 or 14    -> 4