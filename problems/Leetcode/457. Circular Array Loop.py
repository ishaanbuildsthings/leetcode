class Solution:
    def circularArrayLoop(self, nums: List[int]) -> bool:
        n = len(nums)
        arr = [i for i in range(n)]
        for i in range(n):
            nextIdx = i + nums[i]
            if nextIdx < 0:
                nextIdx += n
            nextIdx %= n
            arr[i] = nextIdx
        
        seen = set()

        for i in range(n):
            if i in seen:
                continue
        
            path = set() # we need to know if we hit our current path
            # for instance 2->1<>1 if we visited 1 earlier and fail in a self loop, now visit 2, we cannot just check 1 is inside the seen path
            j = i
            while True:
                if j in path:
                    return True
                path.add(j)
                nxt = arr[j]
                if nxt == j:
                    break
                if (nums[j] >= 0 and nums[nxt] >= 0) or (nums[j] < 0 and nums[nxt] < 0):
                    j = nxt
                else:
                    break
                        
            for token in path:
                seen.add(token)
        
        return False
                