class Solution:
    def minimumHammingDistance(self, source: List[int], target: List[int], allowedSwaps: List[List[int]]) -> int:
        adj = defaultdict(list)
        for a, b in allowedSwaps:
            adj[a].append(b)
            adj[b].append(a)

        seen = set()
        def gather(i, ibucket):
            seen.add(i)
            ibucket.add(i)
            for adjN in adj[i]:
                if adjN in seen:
                    continue
                gather(adjN, ibucket)
        
        res = 0
        for i in range(len(source)):
            if i in seen:
                continue
            bucket = set()
            gather(i, bucket)
            s = Counter()
            t = Counter()
            for index in bucket:
                s[source[index]] += 1
                t[target[index]] += 1
            for key in s:
                res += min(s[key], t[key])
        return len(source) - res
