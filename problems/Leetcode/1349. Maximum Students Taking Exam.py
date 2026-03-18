class Solution:
    def maxStudents(self, seats: List[List[str]]) -> int:
        height = len(seats)
        width = len(seats[0])

        @cache
        def isNoTwoAdj(mask):
            string = str(bin(mask)[2:])
            for i in range(len(string) - 1):
                if string[i] == '1' and string[i + 1] == '1':
                    return False
            return True
        
        @cache
        def canFitInRow(row, mask):
            for offset in range(width):
                isSat = mask >> offset & 1
                if not isSat:
                    continue
                colIndex = width - offset - 1
                if seats[row][colIndex] == '#':
                    return False
            return True

        @cache
        def canSeeAbove(aboveMask, mask):
            for offset in range(1, width - 1):
                if not (mask >> offset) & 1:
                    continue
                if (aboveMask >> (offset + 1)) & 1:
                    return True
                if (aboveMask >> (offset - 1)) & 1:
                    return True
            if mask & 1 and aboveMask >> 1 & 1:
                return True
            if (mask >> (width - 1)) & 1 and (aboveMask >> (width - 2)) & 1:
                return True
            return False

        @cache
        def dp(r, aboveMask):
            if r == height:
                return 0
            resHere = -inf
            for mask in range(1 << width):
                if not isNoTwoAdj(mask):
                    continue
                if not canFitInRow(r, mask):
                    continue
                if canSeeAbove(aboveMask, mask):
                    continue
                resHere = max(resHere, mask.bit_count() + dp(r + 1, mask))
            return resHere
        
        return dp(0, 0)
                

            
            