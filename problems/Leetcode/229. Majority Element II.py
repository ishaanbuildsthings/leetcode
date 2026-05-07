class Solution:

    def majorityElement(self, nums):
        if not nums:
            return []
        
        cand1 = cand2 = None
        cnt1 = cnt2 = 0
        for v in nums:
            if v == cand1:
                cnt1 += 1
            elif v == cand2:
                cnt2 += 1
            elif cand1 is None or cnt1 == 0:
                cand1 = v
                cnt1 = 1
            elif cand2 is None or cnt2 == 0:
                cand2 = v
                cnt2 = 1
            else:
                cnt1 -= 1
                cnt2 -= 1
                if cnt1 < 0:
                    cand1 = v
                    cnt1 = 1
                if cnt2 < 0:
                    cand2 = v
                    cnt2 = 1
        countsCand1 = 0
        countsCand2 = 0
        for v in nums:
            countsCand1 += v == cand1
            countsCand2 += v == cand2
        res = []
        if countsCand1 > len(nums) / 3:
            res.append(cand1)
        if cand2 != cand1 and countsCand2 > len(nums) / 3:
            res.append(cand2)
        
        return res