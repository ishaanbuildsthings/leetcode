class Solution:
    def pathInZigZagTree(self, label: int) -> List[int]:
        # figure out which layer its in
        layer = label.bit_length() - 1

        if layer % 2 == 0:
            leftToRight = True
        else:
            leftToRight = False

        def flip(val, layer):
            width = 2**layer
            small = width
            big = small + width - 1
            diffFromBig = big - val
            fromSmall = small + diffFromBig
            return fromSmall
        
        if not leftToRight:
            originalPos = flip(label, layer)
        else:
            originalPos = label

        path = [] # holds (modifiedLabel, layer)
        curr = originalPos
        currLayer = layer
        while curr:
            if currLayer % 2:
                modifiedLabel = flip(curr, currLayer)
                path.append(modifiedLabel)
            else:
                path.append(curr)
            curr //= 2
            currLayer -= 1

        return path[::-1]


