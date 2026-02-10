class Solution:
    def canTransform(self, start: str, result: str) -> bool:
        def make(string):
            return [x for x in string if x != 'X']
        if make(start) != make(result):
            return False
        # if we encounter an R in result before start, it is not good
        # if we encounter an L in start before result, it is not good

        rStart = 0
        lResult = 0
        for i in range(len(start)):
            s = start[i]
            r = result[i]
            if r == 'R':
                if not rStart and s != 'R':
                    return False
            if s == 'L':
                if not lResult and r != 'L':
                    return False
            rStart += s == 'R'
            lResult += r == 'L'
            rStart -= r == 'R'
            lResult -= s == 'L'
        
        return True
