# nums =
# [3,2,1]
# locked =
# [0,1,0]
# k =
# 0
# Use Testcase
# Output
# 3
# Expected
# -1



# Wrong Answer
# 517 / 614 testcases passed
# Input
# nums =
# [3,2,1]
# locked =
# [0,1,0]
# k =
# 1
# Use Testcase
# Output
# -1
# Expected
# 4





# Wrong Answer
# 553 / 614 testcases passed
# Input
# nums =
# [2,1,3,4,6,5]
# locked =
# [0,0,1,1,0,0]
# k =
# 0
# Use Testcase
# Output
# 9
# Expected
# 2



class Solution:
    def minOperations(self, nums: list[int], locked: list[int], k: int) -> int:
        unlockOps = 0
        n = len(nums)
        for i in range(n):
            v = nums[i]
            if v != i + 1 and locked[i]:
                unlockOps += 1
                locked[i] = 0

        # print(f'{unlockOps=}')

        # print(f'{locked=}')

        if unlockOps > k:
            # print(f'too many unlock ops, fail')
            return -1
               

        # print(f'{unlockOps=}')

        def repair(piece, l, r):
            # print('-------------')
            # print(f'piece is: {piece}')
            # print(f'{l=} {r=}')
            if not piece:
                return 0
                
            s = list(range(l + 1, r + 2))
            # print(f'{s=}')
            # print(f's={s}')
            if set(piece) != set(s):
                return inf

            swapsHere = 0
            nextToSort = l + 1
            # print(f'sorting: {nextToSort}')
            while piece != s:
                # print(f'piece now: {piece}')
                # print(f'piece is: {piece}')
                # print(f'sorting with: {nextToSort}')
                idx = piece.index(nextToSort)
                # print(f'idx={idx}')
                desiredIdx = nextToSort - 1 - l
                # print(f'{desiredIdx=}')
                swapsHere += abs(idx - desiredIdx)
                piece.pop(idx)
                piece.insert(desiredIdx, nextToSort)
                nextToSort += 1

            return swapsHere

        swaps = 0

        extraUnlocks = k - unlockOps

        # print(f'locked={locked}')

        pieces = []
        piece = []
        for i in range(n):
            # print('----')
            v = nums[i]
            if locked[i]:
                pieceSz = len(piece)
                prevR = i - 1
                prevL = prevR - pieceSz + 1
                # print(f'{prevL=} {prevR=}')
                # print(f'{piece=}')
                if set(piece) != set(list(range(prevL + 1, prevR + 2))):
                    # print(f'we do not equal req piece')
                    if extraUnlocks == 0:
                        return -1
                    extraUnlocks -= 1
                    unlockOps += 1
                    piece.append(v)
                    continue
                
                swaps += repair(piece, prevL, prevR)
                # print(f'swaps now: {swaps}')
                piece = []
                continue
            piece.append(v)

        # print(f'swaps before final: {swaps}')
        pieceSz = len(piece)
        prevR = len(nums) - 1
        prevL = prevR - pieceSz + 1
        # print(f'final piece: {piece}')
        # print(f'unlock ops used: {unlockOps}')
        # print(f'{prevL=} {prevR=}')
        swaps += repair(piece, prevL, prevR)

        # print(f'very last swaps: {swaps}')

        if swaps == inf:
            return -1

        return swaps + unlockOps
        
            
            

        

        # s = sorted(nums)
        # nextToSort = 1
        # swaps = 0
        # while nums != s:
        #     print(f'nums is: {nums}')
        #     idx = nums.index(nextToSort)
        #     desiredIdx = nextToSort - 1
        #     swaps += abs(idx - desiredIdx)
        #     nums.pop(idx)
        #     nums.insert(desiredIdx, nextToSort)
        #     nextToSort += 1

        # return unlockOps + swaps
            
            
            

        # unsorted = SortedList() # holds values
        # for i in range(n):
        #     unsorted.add(i)

        # vToI = 

        # while nums != s:
            

        