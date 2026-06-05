class Solution:
    def minNumberOfFrogs(self, croakOfFrogs: str) -> int:
        charToIdx = {
            char : i for i, char in enumerate('croak')
        }
        idxToChar = {
            charToIdx[char] : char for char in charToIdx
        }

        res = 0
        size = 0
        counts = Counter()
        for char in croakOfFrogs:
            if char == 'c':
                counts['c'] += 1
                size += 1
            else:
                prevChar = idxToChar[charToIdx[char] - 1]
                if not counts[prevChar]:
                    return -1
                counts[prevChar] -= 1
                size -= 1
                if not counts[prevChar]:
                    del counts[prevChar]
                if char != 'k':
                    counts[char] += 1
                    size += 1
            res = max(res, size)

        return res if not counts else -1


