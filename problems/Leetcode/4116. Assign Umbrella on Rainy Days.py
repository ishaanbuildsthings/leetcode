class Solution:
    def assignUmbrella(self, rain: list[int]) -> list[str]:
        n = len(rain)
        res = [None] * n
        alice = bob = 0
        for i, v in enumerate(rain):
            if not v:
                res[i] = 'None'
                continue
            aliceNeeds = i + 1 < n and rain[i + 1]
            if not aliceNeeds:
                bob += 1
                res[i] = 'Bob'
                continue
            if alice == bob:
                res[i] = 'Alice'
                alice += 1
                continue
            if alice < bob:
                res[i] = 'Alice'
                alice += 1
                continue
            res[i] = 'Bob'
            bob += 1
            continue
        return res