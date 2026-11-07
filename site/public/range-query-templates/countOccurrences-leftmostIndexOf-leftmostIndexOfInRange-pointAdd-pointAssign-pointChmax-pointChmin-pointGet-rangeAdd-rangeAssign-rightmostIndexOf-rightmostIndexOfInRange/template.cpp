// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: sqrt
// @complexities:
//   countOccurrences: sqrt(N)
//   getAll: N
//   leftmostIndexOf: sqrt(N)
//   leftmostIndexOfInRange: sqrt(N)
//   pointAdd: sqrt(N)
//   pointAssign: sqrt(N)
//   pointChmax: sqrt(N)
//   pointChmin: sqrt(N)
//   pointGet: 1
//   rangeAdd: sqrt(N)
//   rangeAssign: sqrt(N)
//   rightmostIndexOf: sqrt(N)
//   rightmostIndexOfInRange: sqrt(N)
//   build: N
// @memory:
//   layout: none
//   node: vals[1*N] cnt[1*N]
//   tags: add[1*sqrt(N)] asg[1*sqrt(N)]
//   other: none
//   note: sqrt(N) blocks; cnt[b] counts the block's stored values, and the block tag (assign, then add) is applied on read

// "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?", with range add, range
// assign and point updates. 0-based, inclusive.
// Sqrt decomposition: each block keeps its stored values, a value -> count table of them, and one pending tag
// "value = (asg if assigned else stored) + add". A whole block answers a count from its table in O(1): look up
// x - add (or compare x to asg + add when the block is assigned). A partial block bakes its tag in, edits the few
// slots it covers, and patches its table one slot at a time. A first / last search skips every block whose table
// lacks x and scans only the first block that has it. T: int, long long, ... (an integer type: the tables hash it).
template <typename T>
struct SqrtOccurrences {
    // splitmix64 with a random per-run offset: anti-hash tests can't predict buckets, so tables stay O(1)
    struct SafeHash {
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    int n, B, nb;
    vector<T> vals, add, asg;
    vector<char> hasAsg;
    vector<unordered_map<T, int, SafeHash>> cnt;

    // O(N)
    explicit SqrtOccurrences(const vector<T>& a) : n((int)a.size()), vals(a) {
        B = max(1, (int)sqrtl(n));
        while ((long long)(B + 1) * (B + 1) <= n) B++;
        nb = (n + B - 1) / B;
        add.assign(nb, 0), asg.assign(nb, 0), hasAsg.assign(nb, 0), cnt.resize(nb);
        for (int i = 0; i < n; i++) cnt[i / B][a[i]]++;
    }

    int lo(int b) const { return b * B; }
    int hi(int b) const { return min(n, (b + 1) * B) - 1; }

    // O(sqrt N) -- bake block b's tag into its stored values and clear it
    void push(int b) {
        if (!add[b] && !hasAsg[b]) return;
        if (hasAsg[b]) {
            T v = asg[b] + add[b];
            for (int i = lo(b); i <= hi(b); i++) vals[i] = v;
            cnt[b].clear(), cnt[b][v] = hi(b) - lo(b) + 1;
        } else {
            for (int i = lo(b); i <= hi(b); i++) vals[i] += add[b];
            unordered_map<T, int, SafeHash> shifted;
            shifted.reserve(cnt[b].size());
            for (auto& [k, c] : cnt[b]) shifted[k + add[b]] = c;
            cnt[b].swap(shifted);
        }
        add[b] = 0, hasAsg[b] = 0;
    }

    // O(1) -- a[i] = v inside an untagged block, keeping its table in sync
    void set(int b, int i, T v) {
        auto it = cnt[b].find(vals[i]);
        if (--it->second == 0) cnt[b].erase(it);
        cnt[b][v]++;
        vals[i] = v;
    }

    // whole blocks get a tag; the partial ends are pushed and edited slot by slot
    template <class Tag, class Edit>
    void apply(int l, int r, const Tag& tag, const Edit& edit) {
        for (int b = l / B; b <= r / B; b++) {
            if (l <= lo(b) && hi(b) <= r) { tag(b); continue; }
            push(b);
            for (int i = max(l, lo(b)); i <= min(r, hi(b)); i++) set(b, i, edit(vals[i]));
        }
    }

    // O(sqrt N) -- a[i] += x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        if (l <= r) apply(l, r, [&](int b) { add[b] += x; }, [&](T v) { return v + x; });
    }

    // O(sqrt N) -- a[i] = x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        if (l <= r) apply(l, r, [&](int b) { asg[b] = x, hasAsg[b] = 1, add[b] = 0; }, [&](T) { return x; });
    }

    // O(sqrt N) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else throws out_of_range
    int countOccurrences(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countOccurrences: needs 0 <= l <= r < n");
        int res = 0;
        for (int b = l / B; l <= r && b <= r / B; b++) {
            if (l <= lo(b) && hi(b) <= r) {
                if (hasAsg[b]) res += asg[b] + add[b] == x ? hi(b) - lo(b) + 1 : 0;
                else {
                    auto it = cnt[b].find(x - add[b]);
                    if (it != cnt[b].end()) res += it->second;
                }
            } else {
                for (int i = max(l, lo(b)); i <= min(r, hi(b)); i++) res += (hasAsg[b] ? asg[b] : vals[i]) + add[b] == x;
            }
        }
        return res;
    }

    // O(sqrt N) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(T x) const { return search(0, n - 1, x, false); }

    // O(sqrt N) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(T x) const { return search(0, n - 1, x, true); }

    // O(sqrt N) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else
    // throws out_of_range
    int leftmostIndexOfInRange(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < n");
        return search(l, r, x, false);
    }

    // O(sqrt N) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    int rightmostIndexOfInRange(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < n");
        return search(l, r, x, true);
    }

    // the first (rev: last) i in [l, r] with a[i] == x, or -1
    int search(int l, int r, T x, bool rev) const {
        if (l > r) return -1;
        for (int k = 0, nbk = r / B - l / B + 1; k < nbk; k++) {
            int b = rev ? r / B - k : l / B + k, s = max(l, lo(b)), e = min(r, hi(b));
            if (hasAsg[b]) {
                if (asg[b] + add[b] == x) return rev ? e : s;
                continue;
            }
            T want = x - add[b];
            if (!cnt[b].count(want)) continue;  // (a partial block too: x isn't anywhere in it)
            if (rev) {
                for (int i = e; i >= s; i--) if (vals[i] == want) return i;
            } else {
                for (int i = s; i <= e; i++) if (vals[i] == want) return i;
            }
        }
        return -1;
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int b = i / B;
        return (hasAsg[b] ? asg[b] : vals[i]) + add[b];
    }

    // O(N) -- the whole array (each a[i] is O(1))
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // O(sqrt N) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int b = i / B;
        push(b);
        set(b, i, v);
    }

    // O(sqrt N) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(sqrt N) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(sqrt N) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
