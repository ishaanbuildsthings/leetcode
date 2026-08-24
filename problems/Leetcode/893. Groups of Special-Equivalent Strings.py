class Solution:
    def numSpecialEquivGroups(self, words: List[str]) -> int:
        def hashW(w):
            oddC = [0] * 26
            evenC = [0] * 26
            for i in range(len(w)):
                c = w[i]
                pos = ord(c) - ord('a')
                if i % 2 == 0:
                    evenC[pos] += 1
                else:
                    oddC[pos] += 1
            return (tuple(oddC), tuple(evenC))
        
        seen = set()
        for w in words:
            hashed = hashW(w)
            seen.add(hashed)
            
        return len(seen)