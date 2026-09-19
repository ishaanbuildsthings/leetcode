class Solution:
    def checkOverlap(self, radius: int, xCenter: int, yCenter: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        if x1 <= xCenter <= x2:
            x = xCenter
        else:
            d1 = abs(xCenter - x1)
            d2 = abs(xCenter - x2)
            if d2 <= d1:
                x = x2
            else:
                x = x1
        
        if y1 <= yCenter <= y2:
            y = yCenter
        else:
            d1 = abs(yCenter - y1)
            d2 = abs(yCenter - y2)
            if d2 <= d1:
                y = y2
            else:
                y = y1
        
        dist = math.sqrt(abs(x - xCenter)**2 + abs(y - yCenter)**2)
        return dist <= radius
        
