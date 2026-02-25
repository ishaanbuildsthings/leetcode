class Solution:
    def supersequences(self, words: List[str]) -> List[List[int]]:
        g = defaultdict(list) # index -> idxs
        letters = set()
        for w in words:
            a = w[0]
            b = w[1]
            letters.add(a)
            letters.add(b)
        letters = sorted(letters)
        vToI = {
            letter : i for i, letter in enumerate(letters)
        }
        for w in words:
            a = w[0]
            b = w[1]
            g[vToI[a]].append(vToI[b])
        
        N = len(letters)
        resMasks = []

        

        def hasCycle(letterI, path, doubledMask):
            seen.add(letterI)
            path.add(letterI)
            for adjLetterI in g[letterI]:
                if doubledMask & (1 << adjLetterI):
                    continue
                if adjLetterI in path:
                    return True
                # not needed
                # if adjLetterI in seen:
                #     continue
                if hasCycle(adjLetterI, path, doubledMask):
                    return True
            path.remove(letterI) # imagine a>b a>c and c>d b>d, no cycle it is a dag
            return False
            
        # mask is doubled
        for mask in range(1 << N):
            seen = set()
            # all of the non-doubled letters need to be cycle free

            hadCycle = False

            for i in range(N):
                # ignore doubles
                if mask & (1 << i):
                    continue
                if i in seen:
                    continue
                path = set()
                if hasCycle(i, path, mask):
                    hadCycle = True
                    break

            
            if not hadCycle:
                resMasks.append(mask)
        
        res = []
        for dmask in resMasks:
            o = [0] * 26
            for letter in letters:
                pos = ord(letter) - ord('a')
                o[pos] += 1
            for bit in range(len(letters)):
                if dmask & (1 << bit):
                    actualLetter = letters[bit]
                    o[ord(actualLetter) - ord('a')] += 1
            res.append(o)
        
        sums = [sum(x) for x in res]
        mn = min(sums)
        res = [x for x in res if sum(x) == mn]
        
        return res
            


            

