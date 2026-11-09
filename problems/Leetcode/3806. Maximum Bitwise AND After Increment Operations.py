class Solution:
    def maximumAND(self, nums: List[int], k: int, m: int) -> int:
        LOG = 32
        pf = 0
        for b in range(LOG - 1, -1, -1):
            npf = pf | (1 << b)
            # can we pick numbers which start with npf?
            costs = []
            for v in nums:
                if v & npf == npf:
                    costs.append(0)
                    continue
                if v < npf:
                    costs.append(npf - v)
                    continue
                # v has a bigger prefix start than npf, e.g.
                # npf = 10010
                # v   = 10100
                # we want to increment v until those bits turn on
                # so we need the smallest larger than V number which matches npf
                # find the biggest index they disagree at

                cost = 0

                for b2 in range(LOG - 1, -1, -1):
                    if not npf & (1 << b2):
                        continue
                    if (npf & (1 << b2)) and (v & (1 << b2)):
                        continue
                    # set for npf, not v

                    npfBit = 1 << b2
                    suffixV = ((1 << b2) - 1) & v
                    step = npfBit - suffixV
                    cost += step
                    v += step
                
                costs.append(cost)

            costs.sort()
            if sum(costs[:m]) <= k:
                pf = npf
        return pf