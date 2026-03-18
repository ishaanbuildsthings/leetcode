class Solution:
    def maxEqualFreq(self, nums: List[int]) -> int:
        counts = Counter()
        countFrqs = defaultdict(int)

        res = 0

        for i in range(len(nums)):
            counts[nums[i]] += 1
            oldFrq = counts[nums[i]] - 1
            newFrq = counts[nums[i]]
            # print(f'new frq: {newFrq}')
            if oldFrq > 0:
                countFrqs[oldFrq] -= 1
            if not countFrqs[oldFrq]:
                del countFrqs[oldFrq]
            countFrqs[newFrq] += 1
            uniqueFrqs = len(countFrqs)

            # one number appears N times
            if len(counts) == 1:
                res = i + 1

            if uniqueFrqs > 2:
                continue
            # if there is 1 unique frq, we can do it if that frq is 1 (every number appears once)
            # one unique frequency: 1, 1, 1, or 2, 2, 2, or ...
            if uniqueFrqs == 1:
                keys = list(countFrqs.keys())
                firstKey = keys[0]
                if counts[nums[0]] == 1:
                    res = i + 1
                    continue
                continue
            
            twoUniqueFrqs = list(countFrqs.keys())
            
            # if there are 2 unique frequencies, we can do this:

            # 1) we have a single number type that appeared once, delete it
            if 1 in twoUniqueFrqs:
                if countFrqs[1] == 1:
                    res = i + 1

            # 2) we have a single number type that appeared X+1 times, all others appeared X times, delete the X+1           
            bigger = max(twoUniqueFrqs)
            smaller = min(twoUniqueFrqs)
            if countFrqs[bigger] == 1 and bigger == smaller + 1:
                res = i + 1
        
        return res



            