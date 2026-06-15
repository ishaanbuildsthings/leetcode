class Solution:
    def similarRGB(self, color: str) -> str:
        colors = []
        nxtUp = {'0':'1','1':'2','2':'3','3':'4','4':'5','5':'6','6':'7','7':'8','8':'9','9':'a','a':'b','b':'c','c':'d','d':'e','e':'f'}
        nxtDown = {'1':'0','2':'1','3':'2','4':'3','5':'4','6':'5','7':'6','8':'7','9':'8','a':'9','b':'a','c':'b','d':'c','e':'d','f':'e'}
        for i in range(1, len(color), 2):
            s = color[i:i+2]
            value = int(s, 16)
            candidates = [s[0]] # we can use the digit itself twice
            if s[0] != 'f':
                candidates.append(nxtUp[s[0]])
            if s[0] != '0':
                candidates.append(nxtDown[s[0]])

            best = min(candidates, key=lambda d: abs(int(d + d, 16) - value))
            colors.append(best + best)
        return '#' + ''.join(colors)