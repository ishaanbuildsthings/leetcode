class Solution:
    def minimumCost(self, s: str, t: str, flipCost: int, swapCost: int, crossCost: int) -> int:

        zeroTop = 0 # mismatches with a 0 on top
        oneTop = 0
        for i in range(len(s)):
            up = s[i]
            down = t[i]
            if up == '0' and down == '1':
                zeroTop += 1
            elif up == '1' and down == '0':
                oneTop += 1
        
        # flip can fix 1
        # swap can fix 1 of each
        # cross + swap can neutralize

        # option 1, use cross as many as possible
        per = (zeroTop + oneTop) // 2
        crosses = per - min(zeroTop, oneTop)
        print(f'{crosses=}')

        withCrosses = (crosses * crossCost) + (per * swapCost) + (flipCost if (zeroTop + oneTop) % 2 else 0)

        print(f'{withCrosses=}')

        flipsOnly = (zeroTop + oneTop) * flipCost

        bottle = min(zeroTop, oneTop)
        swapAndFlipOnly = (bottle * swapCost) + (max(zeroTop, oneTop) - bottle) * flipCost

        return min([flipsOnly, withCrosses, swapAndFlipOnly])
