import random

class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        l = 0
        r = len(nums) - 1

        def quickSelect(arr, k):
            
            randomIndex = random.randint(0, len(arr) - 1)
            randPivot = arr[randomIndex]

            left = [num for num in arr if num < randPivot]
            mid = [num for num in arr if num == randPivot]
            right = [num for num in arr if num > randPivot]
            
            
            if len(right) >= k:
                return quickSelect(right, k)
            elif len(right) + len(mid) >= k:
                return randPivot
            return quickSelect(left, k - len(right) - len(mid))
                    
        return quickSelect(nums, k)

        # 1 2 3 4 5 5 5 | 6 7 8 9