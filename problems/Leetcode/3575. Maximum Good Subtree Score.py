fmax = lambda x, y: x if x > y else y
class Solution:
    def goodSubtreeSum(self, vals: List[int], par: List[int]) -> int:
        
        children = defaultdict(list)
        MOD = 10**9 + 7
        n = len(vals)
        for i in range(n):
            node = i
            parent = par[i]
            if parent != -1:
                children[parent].append(node)
        banned = set()

        def toMask(node, v):
            mask = 0
            seen = set()
            for d in str(v):
                if d in seen:
                    banned.add(node)
                seen.add(d)
                mask |= (1 << int(d))
            return mask

        masks = [toMask(i, v) for i, v in enumerate(vals)]
        
        
        # returns a map of bitmask -> best scores for this subtree
        @cache # literally just for the summing at the very end, could avoid this caching
        def dp(node):
            if not children[node]:
                out = {0 : 0}
                if node not in banned:
                    out[masks[node]] = vals[node]
                return out
            
            before = {0 : 0} # can always use nothing
            if node not in banned:
                before[masks[node]] = vals[node]
            
            for child in children[node]:
                after = {}
                childMp = dp(child)
                for childMask, childSum in childMp.items():
                    for beforeMask, beforeSum in before.items():
                        if childMask & beforeMask:
                            continue
                        nmask = childMask | beforeMask
                        nsum = childSum + beforeSum
                        after[nmask] = fmax(after.get(nmask, 0), nsum)
                before = after
            
            return before
        
        res = 0
        for node in range(n):
            best = max(dp(node).values(),default=0)
            res += best
            res %= MOD
        
        return res
