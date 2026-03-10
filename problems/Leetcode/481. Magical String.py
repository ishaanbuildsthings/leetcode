class Solution:
    def magicalString(self, n: int) -> int:
        res = [1, 2, 2]
        place = 1
        def swap():
            nonlocal place
            place = 2 if place == 1 else 1
        
        i = 2 # read pointer for how many we need to place
        
        while len(res) < n:
            res.extend([place] * res[i])
            swap()
            i += 1
        
        return sum(x == 1 for x in res[:n])

        
