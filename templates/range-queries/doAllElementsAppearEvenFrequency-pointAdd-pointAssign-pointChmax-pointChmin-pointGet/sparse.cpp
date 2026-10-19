// @operations: doAllElementsAppearEvenFrequency pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   doAllElementsAppearEvenFrequency: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: 1
//   build: 1
// @memory:
//   layout: sparse
//   node: h[1*log(U)]
//   tags: none
//   other: links[2*log(U)] vals[1] tag[1]
//   note: per point write, the O(logU) entries above it; every value has a random 64-bit tag and position i stores tag(a[i]) ^ tag(0), so untouched positions store nothing and a range adds tag(0) once per odd length. Python: a Fenwick tree in a dict; C++: a dynamic prefix-xor tree in one shared node pool, call resetPool() between test cases

// Range "does every value appear an even number of times?" via xor hashing, with point updates, over any index
// range [lo, hi] (huge or negative is fine); every position starts at 0. Each distinct value gets a random 64-bit
// tag; xor over a range cancels tags in pairs, so an all-even range hashes to 0 (false positives ~q / 2^64).
// Sparse: position i stores tag(a[i]) ^ tag(0) in a dynamic prefix-xor tree (nothing for the untouched), so the xor
// of the real tags over [l, r] is the stored xor, plus tag(0) when the length is odd. Nodes live in one pool shared
// by every SparseXorEven<T>. T: any hashable type with == (0 must be a value).
template <typename T>
struct SparseXorEven {
    using U64 = unsigned long long;
    struct Node { U64 f; int l, r; };  // f: total of the stored changes under the node
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;

    // O(1) -- forget every node of every SparseXorEven<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- the change v at position i, added into every node on its root path
    void add(long long i, U64 v) {
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (true) {
            pool[y].f ^= v;
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
    }

    // O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    U64 prefix(long long i) const {
        U64 s = 0;
        int y = i < lo ? 0 : root;
        long long a = lo, b = hi;
        while (y) {
            if (b <= i) { s ^= pool[y].f; break; }
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s ^= pool[pool[y].l].f, y = pool[y].r, a = m + 1;
        }
        return s;
    }

    unordered_map<long long, T> vals;  // nonzero values only
    unordered_map<T, U64> tag;
    mt19937_64 rng;
    U64 zero;

    // O(1) -- all zeros over [lo, hi]. Seeded from the clock: a fixed seed is hackable.
    SparseXorEven(long long lo, long long hi) : lo(lo), hi(hi), rng(chrono::steady_clock::now().time_since_epoch().count()) {
        zero = tagOf(T(0));
    }

    // O(1) amortized -- random tag for a value, minted on first sight
    U64 tagOf(const T& v) {
        auto it = tag.find(v);
        if (it != tag.end()) return it->second;
        return tag[v] = rng();
    }

    // O(logU) -- true iff every value in a[l..r] appears an even number of times
    bool doAllElementsAppearEvenFrequency(long long l, long long r) const {
        U64 h = prefix(r) ^ prefix(l - 1);
        if ((r - l + 1) & 1) h ^= zero;
        return h == 0;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        U64 d = tagOf(pointGet(i)) ^ tagOf(v);
        if (v != T(0)) vals[i] = v;
        else vals.erase(i);
        if (d) add(i, d);
    }

    // O(1) expected -- a[i]
    T pointGet(long long i) const {
        auto it = vals.find(i);
        return it == vals.end() ? T(0) : it->second;
    }

    // a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
