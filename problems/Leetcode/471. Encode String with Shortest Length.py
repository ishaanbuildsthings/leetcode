class Solution:
    def encode(self, s: str) -> str:
        n = len(s)
        
        # returns min length, encoding
        @cache
        def dp(i, j):
            if i > j:
                return ''
            # leave as is
            best = s[i:j+1]

            # append two together
            for k in range(i, j):
                left = dp(i, k)
                right = dp(k + 1, j)
                together = left + right
                if len(together) < len(best):
                    best = together
            
            # is our string some periodic thing? if so we can do say 10[<periodic representation>]
            # where <periodic representation> can be another nested thing

            # s="abbbabbbc abbbabbbc" - 2 periodic
            # "2[2[abbb]c]"

            width = j - i + 1

            for sz in range(1, width):
                if width % sz:
                    continue
                pieces = set()
                for k in range(i, j + 1, sz):
                    piece = s[k:k+sz]
                    pieces.add(piece)
                    if len(pieces) > 1:
                        break
                if len(pieces) > 1:
                    continue
                
                option = f'{width // sz}[{dp(i, i + sz - 1)}]'
                if len(option) < len(best):
                    best = option
            
            return best
        
        return dp(0, n - 1)
                
