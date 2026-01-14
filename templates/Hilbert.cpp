// O(21)
// Maps [L, R] -> some ordering
// 2^pow must be > max(R)
// 21: 2e6, 22: 4e6, etc.
/*
Use like:
struct Q { ... };
sort(queries.begin(), queries.end(), [](const Q& a, const Q& b) {
    return a.ord < b.ord;
});

Using mo's on hilbert order gives O(N * root Q) which is always better than O(N + Q) root N from normal Mo's. O(N * root Q) is also doable with normal Mo's using some other techniques.
*/
// ⚠️ Not optimized
long long hilbertOrder(int l, int r, int pow = 21, int rot = 0) {
    if (!pow) return 0;
    int hpow = 1 << (pow - 1);
    int seg = (l < hpow) ? ((r < hpow) ? 0 : 3) : ((r < hpow) ? 1 : 2);
    seg = (seg + rot) & 3;
    int rotateDelta[] = {3, 0, 0, 1};
    int nx = l & (hpow - 1), ny = r & (hpow - 1);
    int nrot = (rot + rotateDelta[seg]) & 3;
    long long subSize = 1LL << (2 * pow - 2);
    long long ord = seg * subSize;
    long long add = hilbertOrder(nx, ny, pow - 1, nrot);
    ord += (seg == 1 || seg == 2) ? add : (subSize - add - 1);
    return ord;
}