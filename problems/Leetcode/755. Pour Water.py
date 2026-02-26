class Solution:
    def pourWater(self, heights: List[int], volume: int, k: int) -> List[int]:
        heights = [inf] + heights + [inf]
        k = k + 1
        for _ in range(volume):
            l = k
            while heights[l - 1] <= heights[l]:
                l -= 1
            if l != k and heights[l] < heights[k]:
                while heights[l + 1] == heights[l]:
                    l += 1
                heights[l] += 1
                continue
            r = k
            while heights[r + 1] <= heights[r]:
                r += 1
            if r != k and heights[r] < heights[k]:
                while heights[r] == heights[r - 1]:
                    r -= 1
                heights[r] += 1
                continue
            heights[k] += 1
        return heights[1:-1]

            
            