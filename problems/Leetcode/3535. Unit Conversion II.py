MOD = 10**9 + 7
def modInv(num):
    return pow(num, MOD - 2, MOD)
def madd(a, b):
    return (a + b) % MOD
def mmult(a, b):
    return ((a % MOD) * (b % MOD)) % MOD
def mdiv(a, b):
    return (a * modInv(b)) % MOD
class Solution:
    def queryConversions(self, conversions: List[List[int]], queries: List[List[int]]) -> List[int]:
        adj = defaultdict(list)
        for a, b, w in conversions:
            adj[a].append((b, w))
        n = len(conversions) + 1
        convert = [0] * n
        def dfs(node, converted):
            convert[node] = converted
            for adjN, adjW in adj[node]:
                nval = mmult(converted, adjW)
                dfs(adjN, nval)
        dfs(0, 1)
        res = []
        for a, b in queries:
            one = convert[a]
            two = convert[b]
            ratio = mdiv(two, one)
            res.append(ratio)
        return res