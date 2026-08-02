class Solution:
    def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
        # could use sweep line + coordinate compression
        # could use a sweep line + `events` array
        # could use lazy prop tree :P

        sweep = [0] * (2 + (max(tup[1] for tup in ranges)))
        for l, r in ranges:
            sweep[l] += 1
            sweep[r + 1] -= 1
        
        if left >= len(sweep):
            return False

        curr = 0
        for i in range(left):
            curr += sweep[i]
        
        for i in range(left, right + 1):
            curr += sweep[i]
            if curr == 0:
                return False
        
        return True