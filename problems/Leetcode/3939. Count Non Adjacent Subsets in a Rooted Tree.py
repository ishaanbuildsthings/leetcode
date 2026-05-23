class Solution:
    def countValidSubsets(self, parent: List[int], nums: List[int], k: int) -> int:
        MOD = 10**9 + 7

        children = defaultdict(list)
        for i in range(len(parent)):
            child = i
            par = parent[i]
            if par != -1:
                children[par].append(child)

        @cache
        def dp(node, take):
            val = nums[node] % k
            
            # base case
            if not children[node]:
                if take:
                    # out = [0] * k
                    # out[val] += 1
                    out = defaultdict(int)
                    out[val] += 1
                    return out
                # out = [0] * k
                # out[0] = 1
                out = defaultdict(int)
                out[0] = 1
                return out

            if take:
                # out = [0] * k
                # out[val] += 1
                out = defaultdict(int)
                out[val] += 1
                for child in children[node]:
                    # nout = [0] * k
                    nout = defaultdict(int)
                    childRes = dp(child, False)
                    for sz in childRes:
                    # for sz in range(k):
                        # for oldSz in range(k):
                        for oldSz in out:
                            nsz = (sz+oldSz) % k
                            ways = (childRes[sz] * out[oldSz]) % MOD
                            nout[nsz] += ways
                            nout[nsz] %= MOD
                    out = nout
                return out

            # out = [0] * k
            # out[0] += 1
            out = defaultdict(int)
            out[0] = 1
            for child in children[node]:
                # nout = [0] * k
                nout = defaultdict(int)
                childRes = dp(child, True)
                childRes2 = dp(child, False)
                allVals = defaultdict(int)
                for key in childRes:
                    allVals[key] += childRes[key]
                for key in childRes2:
                    allVals[key] += childRes2[key]
                # for sz in range(k):
                for sz in allVals:
                    for oldSz in out:
                        nsz = (sz+oldSz) % k
                        ways = ((childRes[sz]+childRes2[sz]) * out[oldSz]) % MOD
                        nout[nsz] += ways
                        nout[nsz] %= MOD
                out = nout
            return out

        ans = (((dp(0, True)[0] + dp(0, False)[0]) % MOD) - 1) % MOD
        return ans

            

            
                                
    
            
            