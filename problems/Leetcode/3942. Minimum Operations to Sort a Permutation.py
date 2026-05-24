class Solution:
    def minOperations(self, numsIn: List[int]) -> int:

        def process(nums):
            z = nums.index(0)
    
            s = sorted(nums)
            rev = s[::-1]
    
            res = inf
    
            
            # option 1, bring 0 to front
            ops1 = z
            arr1 = nums[z:] + nums[:z]
            if arr1 == s:
                res = ops1
            # print(f'res after bring 0 to front: {res}')
    
            # option 2, bring 0 to back
            ops2 = z + 1 if z != len(nums) - 1 else 0
            arr2 = nums[z+1:] + nums[:z+1]
            if arr2 == rev:
                ops2 += 1
                res = min(res, ops2)
            # print(f'res after bring 0 to back: {res}')
            return res

        A = process(numsIn)
        B = 1 + process(numsIn[::-1])
        ans = min(A, B)
        if ans == inf:
            return -1

        return ans


        # option 3, reverse first then repeat
            
        
            

        

        # arr1 = nums[z:] + nums[:z]

        # # print(f'{arr1=}')

        # arr2 = nums[:z+1][::-1] + nums[z+1:][::-1]

        # # print(f'{arr2=}')

        # s = sorted(nums)

        # if arr1 != s and arr2 != s:
        #     # print('impossible')
        #     return -1

        # res = inf

        # if arr1 == s:
        #     ops = z
        #     res = ops

        # if arr2 == s:
        #     ops = z + 2
        #     res = min(res, ops)
    
        #     rev = nums[::-1]
        #     z = rev.index(0)
        #     ops = z + 1
        #     res = min(res, ops)
        

        # # print(f'{res=}')

        # return res