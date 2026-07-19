class Solution:
    def distinctNames(self, ideas: List[str]) -> int:
        # coffee can have any starting letter that isn't t or c
        # or we have a whitelist of starting letters we can take for this

        # of those, how many words can actually be swapped in?
        # for instance say we are swapping in an `a` to the start of coffee
        # how many words starting with `a` can take a c? we need this information

        s = set(ideas)
        ABC = 'abcdefghijlkmnopqrstuvwxyz'

        safeCounts = Counter() # maps (startingLetter, incomingLetter) -> how many words can safely take that incoming
        for w in ideas:
            start = w[0]
            end = w[1:]
            for alpha in ABC:
                nword = alpha + end
                if nword in s:
                    continue
                safeCounts[(start, alpha)] += 1
        
        res = 0
        for w in ideas:
            start = w[0]
            end = w[1:]
            for alpha in ABC:
                nword = alpha + end
                if nword in s:
                    continue
                # this word can take in this incoming letter
                # we are giving away start, how many words starting with alpha can take in start?
                res += safeCounts[(alpha, start)]
        
        return res

