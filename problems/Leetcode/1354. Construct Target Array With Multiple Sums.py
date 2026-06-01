class Solution:
    def isPossible(self, target: List[int]) -> bool:
        if len(target) == 1:
            return target[0] == 1
            
        sl = SortedList(target)
        tot = sum(target)
        while True:
            mx = sl[-1]
            if mx == 1:
                return True
            
            lost = sl.pop(-1)
            tot -= lost
            rest = tot

            # largest number is smaller than the rest, not constructable
            if rest > lost:
                return False

            # normally we keep adding the rest over and over until we drop below it
            # but if the rest is 1 we don't want to drop to 0, but we can return true here instead
            if rest == 1:
                return True

            prevValue = lost % rest

            # say [1, 1, 1, 3] that 3 must have come from a 0 which is not valid
            if prevValue == 0:
                return False
            sl.add(prevValue)
            tot += prevValue

