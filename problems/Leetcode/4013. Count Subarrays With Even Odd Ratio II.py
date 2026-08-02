
class Solution:
    def countRatioSubarrays(self, nums: list[int], a: int, b: int) -> int:
        nums = [b if x % 2 == 0 else -a for x in nums]


        # a = 30
        # b = 100

        # want to stay below 10/100, only 10% evens

        # even gives +100
        # odd gives -10

        sl = SortedList()
        sl.add(0)
        curr = 0
        res = 0
        for v in nums:
            curr += v
            # need to cut off >= curr
            idx = len(sl) - sl.bisect_left(curr)
            res += idx
            sl.add(curr)

        return res
            
            
            

        
        