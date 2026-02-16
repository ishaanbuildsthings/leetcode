class Solution:
    def countPermutations(self, complexity: List[int]) -> int:
        small = min(complexity)
        if small != complexity[0]:
            return 0
        c = Counter(complexity)
        if c[small] > 1:
            return 0
        sz = len(complexity) - 1
        MOD = 10**9 + 7
        modFac = [1]
        for power in range(1, len(complexity) + 1):
            modFac.append((modFac[-1] * power) % MOD)
        
        return modFac[sz]