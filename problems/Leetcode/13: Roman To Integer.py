VALS = { 'I' : 1, 'V' : 5, 'X' : 10, 'L' : 50, 'C' : 100, 'D' : 500, 'M' : 1000 }

class Solution:
    def romanToInt(self, s: str) -> int:
        result = 0
        i = 0
        while i < len(s):
            if i == len(s) - 1:
                return result + VALS[s[i]]
            # if the next value is bigger than the current one, we add the difference
            next_val = VALS[s[i + 1]]
            curr_val = VALS[s[i]]
            if next_val > curr_val:
                result += next_val - curr_val
                i += 1
            else:
                result += curr_val
            i += 1        
        return result