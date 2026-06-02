class Solution:
    def equalFrequency(self, word: str) -> bool:
        c = Counter(word)
        if len(c.keys()) == 1:
            return True

        vals = list(c.values())
        if len(set(vals)) > 2:
            return False
        if len(set(vals)) == 1 and vals[0] != 1:
            return False
        # all letters occur once
        if len(set(vals)) == 1:
            return True
        
        smallSize = min(vals)
        bigSize = max(vals)
        c2 = Counter(vals)

        if bigSize - 1 != smallSize:
            if smallSize == 1 and c2[smallSize] == 1:
                return True
            return False
        
        
        if c2[smallSize] == 1 and smallSize == 1:
            return True

        if c2[bigSize] > 1:
            return False
        
        return True