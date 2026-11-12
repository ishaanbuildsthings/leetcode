// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countDistinct getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: BIT
// @letters: same
// @complexities:
//   countDistinct: log^2(N)
//   getAll: N
//   pointAdd: log^2(N) amortized
//   pointAssign: log^2(N) amortized
//   pointChmax: log^2(N) amortized
//   pointChmin: log^2(N) amortized
//   pointGet: log(N)
//   rangeAssign: log^2(N) amortized
//   build: N*log^2(N)
// @memory:
//   layout: none
//   node: sets[1*N*log(N)] last[1*N]
//   tags: none
//   other: nxt[1*N] end[1*N] val[1*N] starts[1*N] chains[1*N]
//   note: the array is kept as runs of equal values; Fenwick node j keeps an ordered set of the nxt values in its lowbit(j) positions, at most N*log(N)/2 keys in all (fewer once assigns merge runs); those are balanced-tree / bucket entries, several times heavier than a plain int

// Range count distinct with range assign, online. All indices 0-based, ranges inclusive [l, r].
// The array is kept as runs: run s covers s..end[s], all holding val[s] (at first every element is its own run; an
// assign makes l..r one run). starts holds every run start, chains[v] the starts of the runs holding v.
// Only a run's last position e has a point: nxt[e] = the start of the next run holding the same value, else n (every
// other position has nxt = -1: its next equal value is right after it). A value is counted once in a[l..r] at its last
// occurrence there, so countDistinct(l, r) = [the run holding r continues past r] + #{run ends e in [l, r] : nxt[e] >
// r}.
// Points with nxt == n always count, so a plain Fenwick tree tracks them; every other nxt is a distinct run start < n,
// kept in a Fenwick tree of order-statistics sets (GCC pb_ds): node j holds the nxt values of the lowbit(j) positions
// it covers, so a prefix
// count of "nxt > r" visits log N nodes with one order_of_key each.
// An assign removes the runs it covers (each one was made by an earlier op, so that is O(1) amortized of them) and
// changes O(1) points per run added or removed. No two positions may share an nxt value < n at any moment (the C++
// version keeps them in sets, not multisets), so a point is always cleared before its value is handed on.
// T: any type usable as a std::map key.
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct DynamicDistinctAssign {
    using OrderedSet = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>, __gnu_pbds::rb_tree_tag,
        __gnu_pbds::tree_order_statistics_node_update>;
    int n;
    vector<int> nxt, last;    // nxt[e] at run ends, -1 elsewhere; last: Fenwick tree counting positions with nxt == n
    vector<OrderedSet> sets;  // 1-indexed Fenwick tree of nxt values in [0, n)
    vector<int> end;          // end[s] = last index of the run starting at s
    vector<T> val;            // val[s] = the value of the run starting at s
    set<int> starts;          // every run start
    map<T, set<int>> chains;  // value -> starts of the runs holding it

    // O(N log^2 N)
    explicit DynamicDistinctAssign(const vector<T>& arr)
        : n((int)arr.size()), nxt(n, n), last(n + 1), sets(n + 1), end(n), val(arr) {
        map<T, int> prev;
        for (int i = 0; i < n; i++) {
            auto it = prev.find(arr[i]);
            if (it != prev.end()) nxt[it->second] = i;
            prev[arr[i]] = i;
            set<int>& c = chains[arr[i]];
            c.emplace_hint(c.end(), i);
            starts.emplace_hint(starts.end(), i);
            end[i] = i;
        }
        for (int i = 1; i <= n; i++) {
            last[i] += nxt[i - 1] == n;
            int j = i + (i & -i);
            if (j <= n) last[j] += last[i];
            for (int k = i - (i & -i); k < i; k++)
                if (nxt[k] < n) sets[i].insert(nxt[k]);
        }
    }

    void lastAdd(int i, int d) {
        for (i++; i <= n; i += i & -i) last[i] += d;
    }

    // how many i in [0, x] have nxt[i] > r (x = -1 gives 0)
    int countPast(int x, int r) const {
        int res = 0;
        for (int j = x + 1; j > 0; j &= j - 1) res += last[j] + int(sets[j].size() - sets[j].order_of_key(r + 1));
        return res;
    }

    // O(log^2 N) -- nxt[i] = v (-1: no point)
    void setNxt(int i, int v) {
        int old = nxt[i];
        if (old == v) return;
        if (old == n) lastAdd(i, -1);
        else if (old >= 0) for (int j = i + 1; j <= n; j += j & -j) sets[j].erase(old);
        if (v == n) lastAdd(i, 1);
        else if (v >= 0) for (int j = i + 1; j <= n; j += j & -j) sets[j].insert(v);
        nxt[i] = v;
    }

    // O(logN) -- the start of the run holding i
    int runOf(int i) const { return *prev(starts.upper_bound(i)); }

    // O(log^2 N) -- make a run start at x (0 < x < n): the left part's new last position x - 1 points at x
    void split(int x) {
        int p = runOf(x);
        if (p == x) return;
        end[x] = end[p], val[x] = val[p], end[p] = x - 1;
        starts.insert(x);
        chains.find(val[x])->second.insert(x);
        setNxt(x - 1, x);
    }

    // O(log^2 N) -- # of distinct values in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    int countDistinct(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countDistinct: needs 0 <= l <= r < n");
        int tail = end[runOf(r)] > r;  // a[r]'s run goes on past r: count it here
        return tail + countPast(r, r) - countPast(l - 1, r);
    }

    // O(log^2 N) amortized -- a[i] = v for every i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        split(l);
        if (r + 1 < n) split(r + 1);
        for (auto it = starts.lower_bound(l); it != starts.end() && *it <= r;) {  // drop every run inside l..r
            int s = *it;
            auto cit = chains.find(val[s]);
            set<int>& c = cit->second;
            auto jt = c.find(s);
            int q = jt == c.begin() ? -1 : *prev(jt);
            auto nx = next(jt);
            int after = nx == c.end() ? n : *nx;
            setNxt(end[s], -1);  // clear s's point first, so the value it held is free for q
            c.erase(jt);
            if (c.empty()) chains.erase(cit);
            if (q != -1) setNxt(end[q], after);
            if (s != l) it = starts.erase(it);
            else ++it;
        }
        end[l] = r, val[l] = v;
        set<int>& c = chains[v];
        auto jt = c.insert(l).first;
        auto nx = next(jt);
        if (jt != c.begin()) setNxt(end[*prev(jt)], l);  // move q off `after` first, then hand `after` to the new run
        setNxt(r, nx == c.end() ? n : *nx);
    }

    // O(log^2 N) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return val[runOf(i)];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s : starts) out.insert(out.end(), end[s] - s + 1, val[s]);
        return out;
    }

    // O(log^2 N) amortized -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAssign(i, i, pointGet(i) + delta);
    }

    // O(log^2 N) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) rangeAssign(i, i, v);
    }

    // O(log^2 N) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) rangeAssign(i, i, v);
    }
};
