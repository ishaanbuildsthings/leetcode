# Wrong Answer
# 440 / 675 testcases passed
# Input
# position =
# [677,711,942,960]
# speed =
# [774,951,743,516]
# distance =
# 27
# Use Testcase
# Output
# 2
# Expected
# 1


# Given an array, returns a lis length + a lis in N log N time
# STRICTLY INCREASING LIS

from bisect import bisect_left

def strictlyIncreasingLisAndSequence(nums):
    n = len(nums)
    if n == 0:
        return 0, []

    tails = []
    tailsIndex = []
    prevIndex = [-1] * n

    for i, val in enumerate(nums):
        pos = bisect_left(tails, val)
        if pos == len(tails):
            tails.append(val)
            tailsIndex.append(i)
        else:
            tails[pos] = val
            tailsIndex[pos] = i
        if pos > 0:
            prevIndex[i] = tailsIndex[pos - 1]

    length = len(tails)
    seq = []
    idx = tailsIndex[-1]
    while idx != -1:
        seq.append(nums[idx])
        idx = prevIndex[idx]
    seq.reverse()

    return length, seq


from bisect import bisect_right

def monoIncreasingLisAndSequence(nums):
    n = len(nums)
    if n == 0:
        return 0, []

    tails = []
    tailsIndex = []
    prevIndex = [-1] * n

    for i, val in enumerate(nums):
        pos = bisect_right(tails, val)  # allow equals to extend
        if pos == len(tails):
            tails.append(val)
            tailsIndex.append(i)
        else:
            tails[pos] = val
            tailsIndex[pos] = i
        if pos > 0:
            prevIndex[i] = tailsIndex[pos - 1]

    length = len(tails)
    seq = []
    idx = tailsIndex[-1]
    while idx != -1:
        seq.append(nums[idx])
        idx = prevIndex[idx]
    seq.reverse()

    return length, seq
    
class Solution:
    def countGroups(self, position: list[int], speed: list[int], distance: int) -> int:
        n = len(position)
        speeds = []
        prevHead = speed[0]
        for i in range(1, n):
            prevPos = position[i-1]
            pos = position[i]
            diff = pos - prevPos
            join = diff <= distance
            if join:
                prevHead = speed[i]
                continue
            speeds.append(prevHead)
            prevHead = speed[i]

        speeds.append(prevHead)
        # print(speeds)

        # suffMin = [inf] * len(speeds)
        # curr = inf
        # for i in range(len(speeds) - 1, -1, -1):
        #     curr = min(curr, speeds[i])
        #     suffMin[i] = curr

        res = 0
        # keep walking left until we hit a lte value
        rightHead = speeds[-1]

        # speeds = [5]
        
        for i in range(len(speeds) - 2, -1, -1):
            curr = speeds[i]
            # print(f'{i=}, curr={curr}')
            if curr <= rightHead:
                res += 1
                rightHead = speeds[i]
                # print(f'inc res: {res}')

        return res + 1
       