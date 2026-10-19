// @operations: countMax countMin leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: seg-tree
// @complexities:
//   countMax: log(N)
//   countMin: log(N)
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: mx[4*N] cntMx[4*N] mn[4*N] cntMn[4*N]
//   tags: none
//   other: none
//   note: four flat arrays of 2*size slots (size = next power of two >= n); padding leaves are -inf/+inf with count 0

// Range max / min, how many times each appears, and leftmost / rightmost index with a[i] >= x or <= x, with
// point updates. All indices 0-based, ranges inclusive [l, r]. Searches return -1 when nothing qualifies.
// Iterative over a power-of-two layout so the searches can descend; every field is its own flat array.
// T: int, long long, ...; padding leaves use min(T) / max(T).
template <typename T>
struct MaxMinCountTree {
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n, size;
    vector<T> mx, mn;
    vector<int> cntMx, cntMn;

    void pull(int x) {
        int a = 2 * x, b = 2 * x + 1;
        if (mx[a] != mx[b]) {
            int w = mx[a] > mx[b] ? a : b;
            mx[x] = mx[w], cntMx[x] = cntMx[w];
        } else {
            mx[x] = mx[a], cntMx[x] = cntMx[a] + cntMx[b];
        }
        if (mn[a] != mn[b]) {
            int w = mn[a] < mn[b] ? a : b;
            mn[x] = mn[w], cntMn[x] = cntMn[w];
        } else {
            mn[x] = mn[a], cntMn[x] = cntMn[a] + cntMn[b];
        }
    }

    // O(N)
    explicit MaxMinCountTree(const vector<T>& a) : n((int)a.size()), size(1) {
        while (size < n) size <<= 1;
        mx.assign(2 * size, NINF), mn.assign(2 * size, INF), cntMx.assign(2 * size, 0), cntMn.assign(2 * size, 0);
        for (int i = 0; i < n; i++) mx[size + i] = mn[size + i] = a[i], cntMx[size + i] = cntMn[size + i] = 1;
        for (int x = size - 1; x > 0; x--) pull(x);
    }

    // O(logN) -- (max of a[l..r], how many times it appears)
    pair<T, int> maxCount(int l, int r) const {
        T best = NINF;
        int cnt = 0;
        auto take = [&](int x) {
            if (mx[x] > best) best = mx[x], cnt = cntMx[x];
            else if (mx[x] == best) cnt += cntMx[x];
        };
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) take(l++);
            if (r & 1) take(--r);
        }
        return {best, cnt};
    }

    // O(logN) -- (min of a[l..r], how many times it appears)
    pair<T, int> minCount(int l, int r) const {
        T best = INF;
        int cnt = 0;
        auto take = [&](int x) {
            if (mn[x] < best) best = mn[x], cnt = cntMn[x];
            else if (mn[x] == best) cnt += cntMn[x];
        };
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) take(l++);
            if (r & 1) take(--r);
        }
        return {best, cnt};
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) const { return maxCount(l, r).first; }

    // O(logN) -- how many i in [l, r] have a[i] == max of a[l..r]
    int countMax(int l, int r) const { return maxCount(l, r).second; }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) const { return minCount(l, r).first; }

    // O(logN) -- how many i in [l, r] have a[i] == min of a[l..r]
    int countMin(int l, int r) const { return minCount(l, r).second; }

    // O(logN) -- first i in [l, r] with a[i] >= x, or -1; climbs from l, then descends into the first hit
    int leftmostGteX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (mx[p] >= x) {
                while (p < size) {
                    p <<= 1;
                    if (!(mx[p] >= x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- first i in [l, r] with a[i] > x, or -1; climbs from l, then descends into the first hit
    int leftmostGtX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (mx[p] > x) {
                while (p < size) {
                    p <<= 1;
                    if (!(mx[p] > x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- first i in [l, r] with a[i] <= x, or -1; climbs from l, then descends into the first hit
    int leftmostLteX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (mn[p] <= x) {
                while (p < size) {
                    p <<= 1;
                    if (!(mn[p] <= x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- first i in [l, r] with a[i] < x, or -1; climbs from l, then descends into the first hit
    int leftmostLtX(int l, int r, T x) const {
        int p = l + size;
        for (;;) {
            while (!(p & 1)) p >>= 1;
            if (mn[p] < x) {
                while (p < size) {
                    p <<= 1;
                    if (!(mn[p] < x)) p++;
                }
                return p - size <= r ? p - size : -1;
            }
            p++;
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] >= x, or -1; climbs from r, then descends into the last hit
    int rightmostGteX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (mx[p] >= x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(mx[p] >= x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] > x, or -1; climbs from r, then descends into the last hit
    int rightmostGtX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (mx[p] > x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(mx[p] > x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] <= x, or -1; climbs from r, then descends into the last hit
    int rightmostLteX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (mn[p] <= x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(mn[p] <= x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- last i in [l, r] with a[i] < x, or -1; climbs from r, then descends into the last hit
    int rightmostLtX(int l, int r, T x) const {
        int p = r + size + 1;
        for (;;) {
            p--;
            while (p > 1 && (p & 1)) p >>= 1;
            if (mn[p] < x) {
                while (p < size) {
                    p = 2 * p + 1;
                    if (!(mn[p] < x)) p--;
                }
                return p - size >= l ? p - size : -1;
            }
            if (!(p & (p - 1))) return -1;
        }
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = size + i;
        mx[p] = mn[p] = v;
        for (p >>= 1; p; p >>= 1) pull(p);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return mx[size + i]; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > mx[size + i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < mx[size + i]) pointAssign(i, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, mx[size + i] + delta); }
};
