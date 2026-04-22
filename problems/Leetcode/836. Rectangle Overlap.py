class Solution:
    def isRectangleOverlap(self, rec1: List[int], rec2: List[int]) -> bool:

        # x1 <= x2, x3 <= x4
        def intersect(x1, x2, x3, x4):
            w1 = x2 - x1
            w2 = x4 - x3
            # left contains right
            if x1 <= x3 and x2 >= x4:
                return w2
            # left contained in right
            if x1 >= x3 and x2 <= x4:
                return w1
            # left is fully on the left
            if x2 <= x3:
                return 0
            # left is fully on the right
            if x1 >= x4:
                return 0
            # left partially intersects
            if x1 <= x3:
                return x2 - x3
            return x4 - x1
        
        return (intersect(rec1[0], rec1[2], rec2[0], rec2[2]) * intersect(rec1[1], rec1[3], rec2[1], rec2[3])) > 0
            
