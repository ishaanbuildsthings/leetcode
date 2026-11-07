class Solution:
    def canRemoveAll(self, types: list[int], colors: list[int], groupSize: list[int]) -> bool:
        stackT = [] # holds (type, streak)
        stackC = [] # holds (color, streak)

        for i in range(len(types)):
            t = types[i]
            c = colors[i]
            if not stackT:
                stackT.append((t, 1))
                stackC.append((c, 1))
            else:
                prevT, prevStreak = stackT[-1]
                nstreak = 1 if t != prevT else prevStreak + 1
                stackT.append((t, nstreak))

                prevC, prevStreak = stackC[-1]
                nstreak = 1 if c != prevC else prevStreak + 1
                stackC.append((c, nstreak))

            req = groupSize[t]
            if stackT[-1][1] >= req and stackC[-1][1] >= req:
                for _ in range(groupSize[t]):
                    stackT.pop()
                    stackC.pop()
        
        return not stackT and not stackC