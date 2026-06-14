from sortedcontainers import SortedList

class Solution:
    def findMaxSum(self, nums1: List[int], nums2: List[int], k: int) -> List[int]:
        zipped = [(nums1[i], nums2[i], i) for i in range(len(nums1))]
        zipped.sort() # nums1[i], nums2[i], i
        
        results = {}
        
        bigK = SortedList()
        tot = 0
        
        solvedNums = set()
        
        # print(f'zipped: {zipped}')
        
        for i in range(len(zipped)):
            
            num1, num2, index = zipped[i]
            
            if not num1 in solvedNums:
                results[num1] = tot
                solvedNums.add(num1)
                
            bigK.add(num2)
            tot += num2
            if len(bigK) > k:
                tot -= bigK[0]
                bigK.pop(0)
            
        # print(f'results: {results}')
        
        res = [None] * len(nums1)
        for i in range(len(nums1)):
            num = nums1[i]
            res[i] = results[num]
            # res[i] = results[i]
        return res
            
            