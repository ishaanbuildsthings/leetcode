class Solution:
    def minRange(self, a: int, b: int, c: int) -> int:
        def xyz(x,y,z):
            arr = sorted([y+z,y,z])
            return arr[-1]-arr[0]
        return min(min(xyz(a,b,c),xyz(a,c,b),xyz(b,a,c),xyz(b,c,a),xyz(c,a,b),xyz(c,b,a)),max(a,b,c)-min(a,b,c))