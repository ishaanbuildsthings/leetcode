class Solution:
    def matchReplacement(self, s: str, sub: str, mappings: List[List[str]]) -> bool:
        canBecome = defaultdict(int) # maps a character in s to a set of indices in sub
        # so if there is an 'a' in s, which positions in sub can accept an a?

        replacements = defaultdict(set) # what each character is allowed to turn into
        for a, b in mappings:
            replacements[a].add(b)

        for i, v in enumerate(sub):
            canBecome[v] |= (1 << i)
            for newChar in replacements[v]:
                canBecome[newChar] |= (1 << i)


        bitset = 0 # indices in sub that are the last matched character of some alignment
        # so if the 0-th bit was set it means we match the prefix 0...0 in sub

        fbit = 1 << (len(sub) - 1) # if we hit this bit we matched the entire sub

        for i, v in enumerate(s):
            shifted = (bitset << 1) | 1
            bitset = shifted & canBecome[v]
            if bitset & fbit:
                return True
        
        return False