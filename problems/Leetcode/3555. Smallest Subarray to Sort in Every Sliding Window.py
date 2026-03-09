class Solution:
    def minSubarraySort(self, nums: List[int], k: int) -> List[int]:
        def solve(arr):
            # edge case
            if len(arr) == 1:
                return 0

            suffMin = [inf] * len(arr)
            curr = inf
            for i in range(len(arr) - 1, -1, -1):
                curr = min(curr, arr[i])
                suffMin[i] = curr
            # find the first invalid L
            l = 0

            while l < len(arr):
                if l == 0:
                    if arr[l] <= suffMin[l+1]:
                        l += 1
                        continue
                    else:
                        break
                
                if arr[l] < arr[l-1]:
                    break
                
                if l < len(arr) - 1:
                    if arr[l] <= suffMin[l+1]:
                        l += 1
                        continue
                    else:
                        break
                # we reached the last element safely
                l += 1
                        
            pfMax = []
            curr = -inf
            for v in arr:
                curr = max(curr, v)
                pfMax.append(curr)
            
            # find the first invalid R
            r = len(arr) - 1
            while r >= 0:
                if r == len(arr) - 1:
                    if arr[r] >= pfMax[r - 1]:
                        r -= 1
                        continue
                    else:
                        break
                
                if arr[r] > arr[r + 1]:
                    break
                
                if r != 0:
                    if arr[r] <= arr[r+1] and arr[r] >= pfMax[r - 1]:
                        r -= 1
                        continue
                    break
                
                r -= 1
                        
            if l > r:
                return 0
            return r - l + 1

        


        return [solve(nums[i:i+k]) for i in range(len(nums) - k + 1)]
