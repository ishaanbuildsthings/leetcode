class Solution:
    def minimumSwap(self, s1: str, s2: str) -> int:
        x1 = sum(v == 'x' for v in s1)
        y1 = len(s1) - x1
        x2 = sum(v == 'x' for v in s2)
        y2 = len(s2) - x1
        if (x1 + x2) % 2 or (y1 + y2) % 2:
            return -1

        
        xy = 0
        yx = 0
        for i in range(len(s1)):
            if s1[i] == s2[i]:
                continue
            if s1[i] == 'x':
                xy += 1
            else:
                yx += 1
            
        base = (xy//2) + (yx//2)
        if xy % 2:
            base += 2
        return base        

        # requires 2 moves
        # x y
        # y x
        # to turn it into yy,xx

        # 1 MOVE
        # x x
        # y y
        # so pairs of xx, yy are fixable
        # pairs of yy, xx are fixable

