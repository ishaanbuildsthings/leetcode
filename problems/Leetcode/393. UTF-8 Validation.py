class Solution:
    def validUtf8(self, data: List[int]) -> bool:
        count = 0
        for v in data:
            # new start
            if count == 0:
                if not (1 << 7) & v:
                    count = 0
                elif v >> 5 == 0b110:
                    count = 1
                elif v >> 4 == 0b1110:
                    count = 2
                elif v >> 3 == 0b11110:
                    count = 3
                else:
                    return False
                continue
            if v >> 6 != 0b10:
                return False
            count -= 1
        if not count:
            return True
        return False
