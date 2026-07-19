class Solution:
    def splitIntoFibonacci(self, num: str) -> List[int]:
        n = len(num)
        MAX_SIZE = 12
        MX = 2**31
        
        for i in range(n):
            v1 = int(num[:i+1])
            # leading 0 1st term
            if num[0] == '0' and i > 0:
                continue
            for j in range(i + 1, n - 1):
                v2 = int(num[i+1:j+1])

                # leading 0 2nd term
                if num[i + 1] == '0' and j > i + 1:
                    continue

                currIdx = j + 1
                bucket = [v1, v2]
                fail = False

                while currIdx < n:
                    req = str(bucket[-1] + bucket[-2])
                
                    # next term is overflow
                    if int(req) >= MX:
                        fail = True
                        break

                    # no string match
                    remain = num[currIdx:currIdx + MAX_SIZE]
                    if not remain.startswith(req):
                        fail = True
                        break
                        
                    bucket.append(int(req))
                    nextIdx = currIdx + len(req)
                    currIdx = nextIdx
                
                if not fail:
                    return bucket
                
        return []
                
                
                
                


                
