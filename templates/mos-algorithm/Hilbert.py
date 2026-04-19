# O(21)
# Maps [L, R] -> some ordering
# 2^pow must be > max(R)
# 21: 2e6, 22: 4e6, etc.
# Use like:
# queries.sort(key=lambda q: hilbertOrder(q[0], q[1])), safe as the hilbert is computed once and cached, not re-ran per sort comparison
# Using mo's on hilbert order gives O(N * root Q) which is always better than O(N + Q) root N from normal Mo's. O(N * root Q) is also doable with normal Mo's using some other techniques.
# ⚠️ Not optimized
def hilbertOrder(l: int, r: int, pow: int = 21, rot: int = 0) -> int:
    if pow == 0:
        return 0
    hpow = 1 << (pow - 1)

    if l < hpow:
        seg = 0 if r < hpow else 3
    else:
        seg = 1 if r < hpow else 2

    seg = (seg + rot) & 3
    rotateDelta = (3, 0, 0, 1)

    nx = l & (hpow - 1)
    ny = r & (hpow - 1)
    nrot = (rot + rotateDelta[seg]) & 3

    subSize = 1 << (2 * pow - 2)
    ordv = seg * subSize

    add = hilbertOrder(nx, ny, pow - 1, nrot)
    ordv += add if (seg == 1 or seg == 2) else (subSize - add - 1)
    return ordv