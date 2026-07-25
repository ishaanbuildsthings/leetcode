class Solution:
    def sumGame(self, num: str) -> bool:
        n = len(num)

        surplus = 0
        gains = 0
        subtracts = 0
        for i in range(n // 2):
            if num[i] != '?':
                surplus += int(num[i])
            else:
                gains += 1
        for i in range(n // 2, n):
            if num[i] != '?':
                surplus -= int(num[i])
            else:
                subtracts += 1
        
        # odd operations obviously alice wins
        if (gains + subtracts) % 2 == 1:
            return True

        aliceOps = abs(gains - subtracts) // 2
        bobOps = aliceOps

        # alice basically gets this many operations to force val to not be a diff

        aliceMax = aliceOps * 9 # if alice increases as much as possible
        aliceMin = 0 # if alice doesn't gain anything

        if surplus > 0 and gains >= subtracts:
            # if we have a positive surplus but alice can just gain, alice wins
            return True
        # if we have a negative surplus and also can just subtract, alice wins
        if surplus < 0 and gains <= subtracts:
            return True
        if surplus == 0:
            return gains != subtracts
        
        # now 2 cases:
        # surplus > 0 and gains < subtracts
        # must forcibly go down

        if surplus > 0:
            # if alice doesn't subtract anything, and bob is out of range, alice wins
            if surplus > 9 * bobOps:
                return True
            # if alice max decreases she can win
            if 9 * aliceOps > surplus:
                return True
            return False
        
        # surplus < 0, gains > subtracts
        # must forcibly go up
        # just simplify the equation this time
        if 9 * aliceOps == abs(surplus):
            return False
        
        return True