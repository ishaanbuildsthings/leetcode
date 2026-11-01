// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointAssign-pointGet-rangeFlip/template.cpp
// @operations: getAll isRBS pointAssign pointGet rangeFlip
// @data-structure-type: lazy-seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   isRBS: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeFlip: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: sm[4*N] mn[4*N] mx[4*N]
//   tags: flp[4*N]
//   other: none
//   note: the characters aren't stored: a node's +-1s say them

// Bracket sequence with RANGE FLIP (every open becomes a close and vice versa): isRBS(l, r) asks whether s[l..r] is a
// regular (balanced) bracket sequence. With open = +1 and close = -1, s[l..r] is regular iff its total is 0 and no
// prefix of it dips below 0. Each node keeps (sum, min prefix sum, max prefix sum) of its range, prefixes including
// the empty one; two halves combine as sum = L.sum + R.sum, minPre = min(L.minPre, L.sum + R.minPre), maxPre
// likewise. A flip negates every value: sum -> -sum, and min / max prefix swap and change sign. Recursive lazy tree
// over 4N slots; the characters themselves are not stored (a +1 reads back as openChar, a -1 as closeChar). All
// indices 0-based, ranges inclusive.
// T: char (or any type: openChar / closeChar are the ones that open / close).
template <typename T>
struct LazyBracketTree {
    int n;
    T oc, cc;
    vector<int> sm, mn, mx;  // per node: sum of its +-1s, min / max prefix sum (the empty prefix counts)
    vector<char> flp;  // pending flip

    // O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar / closeChar: the characters
    // that open / close ('(' / ')' unless you pass e.g. '[' / ']'); a character that isn't openChar counts as (and
    // reads back as) closeChar
    explicit LazyBracketTree(const vector<T>& brackets, T openChar = T('('), T closeChar = T(')'))
        : n((int)brackets.size()), oc(openChar), cc(closeChar) {
        sm.assign(4 * max(1, n), 0);
        mn.assign(4 * max(1, n), 0);
        mx.assign(4 * max(1, n), 0);
        flp.assign(4 * max(1, n), 0);
        if (n) build(1, 0, n - 1, brackets);
    }

    // O(N) -- the whole sequence, as characters
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        if (n) collect(1, 0, n - 1, out);
        return out;
    }

    // O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    bool isRBS(int l, int r) {
        int s = 0, m = 0;
        fold(1, 0, n - 1, l, r, s, m);
        return s == 0 && m >= 0;
    }

    // O(logN) -- brackets[i] = ch
    void pointAssign(int i, T ch) { set(1, 0, n - 1, i, ch == oc ? 1 : -1); }

    // O(logN) -- brackets[i]
    T pointGet(int i) {
        int x = 1, lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            push(x, lo, mid, hi);
            if (i <= mid) x = 2 * x, hi = mid;
            else x = 2 * x + 1, lo = mid + 1;
        }
        return sm[x] > 0 ? oc : cc;
    }

    // O(logN) -- every open in brackets[l..r] becomes a close and vice versa
    void rangeFlip(int l, int r) { update(1, 0, n - 1, l, r, 0); }

    // ---- internals ----

    void build(int x, int lo, int hi, const vector<T>& s) {
        if (lo == hi) {
            int v = s[lo] == oc ? 1 : -1;
            sm[x] = v, mn[x] = min(v, 0), mx[x] = max(v, 0);
            return;
        }
        int mid = (lo + hi) / 2;
        build(2 * x, lo, mid, s), build(2 * x + 1, mid + 1, hi, s);
        pull(x);
    }

    void pull(int x) {
        int l = 2 * x, r = 2 * x + 1;
        sm[x] = sm[l] + sm[r], mn[x] = min(mn[l], sm[l] + mn[r]), mx[x] = max(mx[l], sm[l] + mx[r]);
    }

    void flip(int x) {  // every value of node x negated
        sm[x] = -sm[x];
        swap(mn[x], mx[x]), mn[x] = -mn[x], mx[x] = -mx[x];
        flp[x] ^= 1;
    }

    void push(int x, int lo, int mid, int hi) {  // hand x's pending tags to its children
        if (flp[x]) flip(2 * x), flip(2 * x + 1), flp[x] = 0;  // (after the assign: assign, then flip)
    }

    void update(int x, int lo, int hi, int l, int r, int v) {  // v: assign +-1, or 0 for a flip
        if (l <= lo && hi <= r) {
            flip(x);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) update(2 * x, lo, mid, l, r, v);
        if (r > mid) update(2 * x + 1, mid + 1, hi, l, r, v);
        pull(x);
    }

    void set(int x, int lo, int hi, int i, int v) {
        if (lo == hi) {
            sm[x] = v, mn[x] = min(v, 0), mx[x] = max(v, 0);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (i <= mid) set(2 * x, lo, mid, i, v);
        else set(2 * x + 1, mid + 1, hi, i, v);
        pull(x);
    }

    // s, m: sum and min prefix of everything left of this part; this part gets folded in
    void fold(int x, int lo, int hi, int l, int r, int& s, int& m) {
        if (l <= lo && hi <= r) {
            m = min(m, s + mn[x]), s += sm[x];
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) fold(2 * x, lo, mid, l, r, s, m);
        if (r > mid) fold(2 * x + 1, mid + 1, hi, l, r, s, m);
    }

    void collect(int x, int lo, int hi, vector<T>& out) {
        if (lo == hi) {
            out.push_back(sm[x] > 0 ? oc : cc);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        collect(2 * x, lo, mid, out), collect(2 * x + 1, mid + 1, hi, out);
    }
};
