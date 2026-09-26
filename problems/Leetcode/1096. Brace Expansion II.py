class Solution:
    def braceExpansionII(self, expression: str) -> list[str]:
        pf = [] # holds count of braces
        curr = 0
        for v in expression:
            curr += v in '{}'
            pf.append(curr)
        
        def query(l, r):
            return pf[r] - (pf[l - 1] if l else 0)
        
        lToR = {} # maps index of opening brace to closing brace
        open = 0
        stack = []
        for i, v in enumerate(expression):
            if v == '{':
                open += 1
                stack.append(i)
            elif v == '}':
                poppedI = stack.pop()
                lToR[poppedI] = i
        
        def create(l, r):
            # handle leading letters
            if expression[l] != '{':
                goRight = -1 # find plain letter option
                for L in range(l, r + 1):
                    char = expression[L]
                    if char == '{':
                        break
                    goRight = L
                # entire chain of just letters
                if goRight == r:
                    answer = set()
                    answer.add(expression[l:r+1])
                    return answer

                insideOptions = create(goRight + 1, r)
                leftString = expression[l:goRight + 1]
                newOptions = set()
                for v in insideOptions:
                    newOptions.add(leftString + v)
                return newOptions
            
            # handle suffix letters
            if expression[r] != '}':
                goLeft = r + 1 # find plain letter option
                for R in range(r, l - 1, -1):
                    char = expression[R]
                    if char == '}':
                        break
                    goLeft = R
                insideOptions = create(l, goLeft - 1)
                rightString = expression[goLeft:r + 1]
                newOptions = set()
                for v in insideOptions:
                    newOptions.add(v + rightString)
                return newOptions
            
            # now we start and end with { }

            numBraces = query(l, r)
            # base case 
            if numBraces == 2:
                options = expression[l+1:r].split(',')
                return set(options)
            

            
            r1 = lToR[l]
            # split into 2, cartesian product
            if r1 != r:
                l2 = r1 + 1
                r2 = r
                LEFT = create(l, r1)
                RIGHT = create(l2, r2)
                final = set()
                for left in LEFT:
                    for right in RIGHT:
                        final.add(left + right)
                return final
            
            # some case like {{a, b}, {c, d}}
            
            openBraces = 0
            options = set()
            L = l + 1 # running left
            for i in range(l + 1, r):
                v = expression[i]
                if v == ',' and openBraces == 0:
                    pieceOptions = create(L, i - 1)
                    options |= pieceOptions
                    L = i + 1
                else:
                    if v == '{':
                        openBraces += 1
                    elif v == '}':
                        openBraces -= 1
            
            options |= create(L, r - 1) # add in the very last piece which does not have a trailing comma
            return options
        
        return sorted(create(0, len(expression) - 1))
            

            

