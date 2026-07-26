# can use bucket sorting also
class Solution:
    def hasGroupsSizeX(self, deck: List[int]) -> bool:
        c = Counter(deck)
        # maybe factorizing ahead of time is faster

        for size in range(2, len(deck) + 1):
            failFound = False
            for key in c:
                if c[key] % size:
                    failFound = True
                    break
            if not failFound:
                return True
            
        return False


            