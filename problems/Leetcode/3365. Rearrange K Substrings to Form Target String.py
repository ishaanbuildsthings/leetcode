class Solution:
    def isPossibleToRearrange(self, s: str, t: str, k: int) -> bool:
        c = Counter() # holds tuples
        
        pieceLength = len(s) // k
        
        for start in range(0, len(s), pieceLength):
            hashed = s[start:start+pieceLength]
            c[hashed] += 1
            # tup = [0] * 26
            # for i in range(start, start+pieceLength):
                
                # hashed = s[start:start+pieceLength]
            #     character = s[i]
            #     order = ord(character) - ord('a')
            #     tup[order] += 1
            # c[tuple(tup)] += 1
        
        # print(f'{c=}')
        
        for start in range(0, len(s), pieceLength):
            hashed = t[start:start+pieceLength]
            if c[hashed] == 0:
                return False
            c[hashed] -= 1
            # tup = [0] * 26
            # for i in range(start,start+pieceLength):
            #     character = t[i]
            #     order = ord(character) - ord('a')
            #     tup[order] += 1
            # hashed = tuple(tup)
            # if c[hashed] == 0:
            #     return False
            # c[hashed] -= 1
        
        return True
        
        