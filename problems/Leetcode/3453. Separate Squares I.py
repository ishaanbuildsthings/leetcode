class Solution:
    def separateSquares(self, squares: List[List[int]]) -> float:
        totalArea = 0
        for x, y, l in squares:
            totalArea += l**2
        
        def isUpMoreArea(line):
            aboveArea = 0
            for x, y, l in squares:
                area = l**2
                bot = y
                top = y + l
                if top <= line:
                    continue
                if bot >= line:
                    aboveArea += l**2
                    continue
                aboveY = top - line
                areaAboveHere = aboveY * l
                aboveArea += areaAboveHere
            return aboveArea > totalArea/2
                
                
        down = 0
        up = 10**18
        # res = None
        while down + (10**-5) <= up:
            middle = (down+up)/2
            if isUpMoreArea(middle):
                down = middle
            else:
                up = middle
        
        return down
            
            