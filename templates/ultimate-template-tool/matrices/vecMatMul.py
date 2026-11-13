# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/vecMatMul.py

# vec[1, x] @ M[x, y] = res[1, y], every entry mod mod: res[j] = vec times column j of M
# len(vec) must equal M's row count. Entries may be any ints (negative ones come back reduced into [0, mod))
# vecMatMul([1, 2], [[5, 6], [7, 8]], 10**9 + 7) -> [19, 22]
# O(x * y)
def vecMatMul(vec, M, mod):
    if len(vec) != len(M):
        raise ValueError(f"vecMatMul: vec has {len(vec)} entries but M has {len(M)} rows")
    return [sum(v * m for v, m in zip(vec, colM)) % mod for colM in zip(*M)]
