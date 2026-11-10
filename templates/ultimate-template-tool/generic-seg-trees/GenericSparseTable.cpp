// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericSparseTable.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long mn;
    // long long mx;
};

Node baseFn(const RawVal& v, int i) {
    // Node res;
    // res.mn = v, res.mx = v;
    // return res;
}

// combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count)
Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.mn = min(left.mn, right.mn);
    // res.mx = max(left.mx, right.mx);
    // return res;
}

// A static array (no updates): O(N log N) build, O(1) rangeQuery (one combine call), O(N log N) Nodes of memory
struct SparseTable {
    int n, levels;
    vector<Node> t; // t[j * n + i]: the Node of a[i..i + 2^j - 1], for every i with i + 2^j <= n

    SparseTable(const vector<RawVal>& a) : n(a.size()), levels(n ? 32 - __builtin_clz(n) : 0) {
        t.resize((size_t)levels * n);
        for (int i = 0; i < n; i++) t[i] = baseFn(a[i], i);
        for (int j = 1; j < levels; j++)
            for (int i = 0; i + (1 << j) <= n; i++) t[j * n + i] = combine(t[(j - 1) * n + i],
                t[(j - 1) * n + i + (1 << (j - 1))]);
    }

    // how many elements
    int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return t[i];
    }

    // the Node of a[l..r]: the combine of the two largest power-of-two blocks starting at l and ending at r (they
    // overlap, which is why combine must be idempotent); needs 0 <= l <= r < n, else out_of_range
    Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        int j = 31 - __builtin_clz(r - l + 1);
        if (l + (1 << j) - 1 == r) return t[j * n + l];
        return combine(t[j * n + l], t[j * n + r - (1 << j) + 1]);
    }

    // the Node of the whole array; needs n >= 1, else out_of_range
    Node rangeQueryAll() {
        if (n == 0) throw out_of_range("rangeQueryAll: needs n >= 1");
        return rangeQuery(0, n - 1);
    }
};
