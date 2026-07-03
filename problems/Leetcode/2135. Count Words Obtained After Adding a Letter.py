class Solution:
    def wordCount(self, startWords: List[str], targetWords: List[str]) -> int:

        def wToMask(w):
            msk = 0
            for c in w:
                msk |= (1 << (ord(c) - ord('a')))
            return msk
        
        masks = set()
        for w in startWords:
            masks.add(wToMask(w))
        
        res = 0

        for w in targetWords:
            mask = wToMask(w)
            for bit in range(26):
                if (1 << bit) & mask:
                    nmask = mask ^ (1 << bit)
                    if nmask in masks:
                        res += 1
                        break
        
        return res