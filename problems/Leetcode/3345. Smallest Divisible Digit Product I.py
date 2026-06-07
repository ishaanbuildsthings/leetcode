class Solution:
    def smallestNumber(self, n: int, t: int) -> int:
        start = n
        while True:
            string = str(start)
            product = 1
            for c in string:
                product *= int(c)
            if product % t == 0:
                return start
            start += 1
        
        