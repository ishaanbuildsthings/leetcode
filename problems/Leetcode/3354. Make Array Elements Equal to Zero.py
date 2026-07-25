class Solution:
    def countValidSelections(self, nums: List[int]) -> int:
        def simulate(pos, direction):
            dupe = nums[:]
            currPos = pos
            currD = direction
            while True:
                # print(f'curr pos: {currPos}, currD: {currD}, dupe: {dupe}')
                if currPos < 0 or currPos >= len(dupe):
                    # print(f'out of bounds, dupe now: {dupe}')
                    return all(n == 0 for n in dupe)
                if dupe[currPos] == 0:
                    if currD == 1:
                        currPos += 1
                    else:
                        currPos -= 1
                elif dupe[currPos] > 0:
                    dupe[currPos] -= 1
                    if currD == 1:
                        currD = 0
                    else:
                        currD = 1
                    if currD == 1:
                        currPos += 1
                    else:
                        currPos -= 1
        
        # simulate(2, 0)
        # return
        res = 0
        for pos in range(len(nums)):
            if nums[pos] != 0:
                continue
            # print(f'pos={pos}')
            if simulate(pos, 1):
                res += 1
            if simulate(pos, 0):
                res += 1
            # print(f'res now: {res} for pos={pos}')
        return res
                    
                        
            