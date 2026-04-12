class Solution:
    def internalAngles(self, sides: list[int]) -> list[float]:
        def get(s1, s2, s3):
            v = acos((s1**2 + s2**2 - s3**2)/(2*s1*s2))
            return v
        sides.sort()
        if sides[0] + sides[1] > sides[2]:
            a, b, c = sides
            a1 = get(a, b, c)
            a2 = get(c, a, b)
            a3 = get(b, c, a)
            return sorted([a1 * 180 / pi, a2 * 180 / pi, a3 * 180 / pi])
            
        else:
            return []