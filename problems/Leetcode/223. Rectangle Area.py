class Solution:
    def computeArea(self, ax1: int, ay1: int, ax2: int, ay2: int, bx1: int, by1: int, bx2: int, by2: int) -> int:
        def intersect(l1, r1, l2, r2):
            w1 = r1 - l1
            w2 = r2 - l2
            # case 1, one is inside two
            if l1 >= l2 and r1 <= r2:
                return w1
            # case 2, one contains two
            if l1 <= l2 and r1 >= r2:
                return w2
            # case 3, one is on the left of two
            if r1 <= l2:
                return 0
            # case 4, one is on the right of two
            if l1 >= r2:
                return 0
            # case 5, one is on the left of two w/ intersection
            if l1 <= l2:
                return r1 - l2
            # case 6, one is on the right of two w/ intersection
            return r2 - l1
        
        xintersection = intersect(ax1, ax2, bx1, bx2)
        yintersection = intersect(ay1, ay2, by1, by2)
        a1 = (ax2 - ax1) * (ay2 - ay1)
        a2 = (bx2 - bx1) * (by2 - by1)
        return a1 + a2 - (xintersection * yintersection)