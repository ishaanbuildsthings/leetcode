// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-seq-xor-and-or/template.cpp
// @operations: andGtX andGteX andInValRange andLtX andLteX append appendLeft countGtX countGteX countInValRange countLtX countLteX countOccurrences cut getAll insertAt insertCopiesAt kthGtX kthGteX kthLtX kthLteX kthSmallest largestLtX largestLteX leftmostIndexOf leftmostIndexOfInRange merge orGtX orGteX orInValRange orLtX orLteX paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeMax rangeMin rangeOrQuery rangeRotateLeft rangeRotateRight rangeXorQuery rightmostIndexOf rightmostIndexOfInRange smallestGtX smallestGteX split trisect xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: sqrt
// @complexities:
//   andGtX: sqrt(N)*log(N)
//   andGteX: sqrt(N)*log(N)
//   andInValRange: sqrt(N)*log(N)
//   andLtX: sqrt(N)*log(N)
//   andLteX: sqrt(N)*log(N)
//   append: sqrt(N)*log(N) amortized
//   appendLeft: sqrt(N)*log(N) amortized
//   countGtX: sqrt(N)*log(N)
//   countGteX: sqrt(N)*log(N)
//   countInValRange: sqrt(N)*log(N)
//   countLtX: sqrt(N)*log(N)
//   countLteX: sqrt(N)*log(N)
//   countOccurrences: sqrt(N)*log(N)
//   cut: sqrt(N)*log(N) amortized
//   getAll: N
//   insertAt: sqrt(N)*log(N) amortized
//   insertCopiesAt: sqrt(N)*log(N) amortized
//   kthGtX: sqrt(N)*log(N)
//   kthGteX: sqrt(N)*log(N)
//   kthLtX: sqrt(N)*log(N)
//   kthLteX: sqrt(N)*log(N)
//   kthSmallest: sqrt(N)*log(N)*log(U)
//   largestLtX: sqrt(N)*log(N)
//   largestLteX: sqrt(N)*log(N)
//   leftmostIndexOf: sqrt(N)*log(N)
//   leftmostIndexOfInRange: sqrt(N)*log(N)
//   merge: sqrt(N)*log(N) amortized
//   orGtX: sqrt(N)*log(N)
//   orGteX: sqrt(N)*log(N)
//   orInValRange: sqrt(N)*log(N)
//   orLtX: sqrt(N)*log(N)
//   orLteX: sqrt(N)*log(N)
//   paste: sqrt(N)*log(N) amortized
//   pointAdd: sqrt(N)*log(N)
//   pointAssign: sqrt(N)*log(N)
//   pointChmax: sqrt(N)*log(N)
//   pointChmin: sqrt(N)*log(N)
//   pointGet: sqrt(N)
//   rangeAndQuery: sqrt(N)*log(N)
//   rangeMax: sqrt(N)*log(N)
//   rangeMin: sqrt(N)*log(N)
//   rangeOrQuery: sqrt(N)*log(N)
//   rangeRotateLeft: sqrt(N)*log(N) amortized
//   rangeRotateRight: sqrt(N)*log(N) amortized
//   rangeXorQuery: sqrt(N)*log(N)
//   rightmostIndexOf: sqrt(N)*log(N)
//   rightmostIndexOfInRange: sqrt(N)*log(N)
//   smallestGtX: sqrt(N)*log(N)
//   smallestGteX: sqrt(N)*log(N)
//   split: sqrt(N)*log(N) amortized
//   trisect: sqrt(N)*log(N) amortized
//   xorGtX: sqrt(N)*log(N)
//   xorGteX: sqrt(N)*log(N)
//   xorInValRange: sqrt(N)*log(N)
//   xorLtX: sqrt(N)*log(N)
//   xorLteX: sqrt(N)*log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: vals[1*N] srt[1*N] px[1*N] ta[2*N] to[2*N]
//   tags: none
//   other: none
//   note: blocks of about sqrt(N log N) values, each kept in array order and sorted (N here is the current length); C++ also keeps ord[1*N], each sorted value's position, so edits merge instead of sorting again

// List of sorted blocks: an array you can insert into anywhere, rotate, cut pieces out of (that is how to erase) and
// paste them back, and ask value questions about any range a[l..r]: how many values are below x, the k-th smallest,
// the nearest value above / below x, where x first / last appears, and the xors, ANDs, ORs of the values in a value
// range. Each op costs about sqrt(N log N): the array is a list of blocks, each kept both in array order and sorted.
// All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array.
// T: int, long long, ...
template <typename T>
struct SqrtSequence {
    // a run of the array: vals in array order and srt, the same values sorted, both raw (the tags apply on read);
    // ord[i] is the position in vals of srt[i], so an edit merges instead of sorting again
    struct Block {
        vector<T> vals, srt;
        vector<int> ord;
        vector<T> px;  // px[k] = xor of the k smallest
        vector<T> ta;  // AND tree over srt (leaves at m..2m-1)
        vector<T> to;  // OR tree over srt

        Block() = default;

        explicit Block(vector<T> v) : vals(std::move(v)) {  // O(B log B)
            ord.resize(vals.size());
            iota(ord.begin(), ord.end(), 0);
            sort(ord.begin(), ord.end(), [&](int x, int y) { return vals[x] < vals[y]; });
            srt.resize(vals.size());
            for (int i = 0; i < size(); i++) srt[i] = vals[ord[i]];
            refresh();
        }

        int size() const { return (int)vals.size(); }

        void refresh() {  // O(B) -- what is kept over srt
            int m = size();
            px.assign(m + 1, T(0));
            for (int i = 0; i < m; i++) px[i + 1] = px[i] ^ srt[i];
            ta.assign(2 * m, ~T(0));
            copy(srt.begin(), srt.end(), ta.begin() + m);
            for (int i = m - 1; i > 0; i--) ta[i] = ta[2 * i] & ta[2 * i + 1];
            to.assign(2 * m, T(0));
            copy(srt.begin(), srt.end(), to.begin() + m);
            for (int i = m - 1; i > 0; i--) to[i] = to[2 * i] | to[2 * i + 1];
            (void)m;
        }

        void bake() {}  // (no tags: nothing is ever pending)

        // O(B) -- the values at positions lo..hi become f(value), where f keeps their order (an add, an assign, a
        // single value): the changed and the unchanged entries of srt are each still sorted, so one merge restores it
        template <class F>
        void update(int lo, int hi, F f) {
            bake();
            for (int k = lo; k <= hi; k++) vals[k] = f(vals[k]);
            vector<int> in, out;
            for (int p : ord) (lo <= p && p <= hi ? in : out).push_back(p);
            std::merge(in.begin(), in.end(), out.begin(), out.end(), ord.begin(), [&](int x, int y) { return vals[x] < vals[y]; });
            for (int i = 0; i < size(); i++) srt[i] = vals[ord[i]];
            refresh();
        }

        void insert(int k, T v) {  // O(B) -- v goes in at position k
            bake();
            vals.insert(vals.begin() + k, v);
            for (int& p : ord) p += p >= k;
            int i = int(upper_bound(srt.begin(), srt.end(), v) - srt.begin());
            srt.insert(srt.begin() + i, v), ord.insert(ord.begin() + i, k);
            refresh();
        }

        Block cutTail(int k) {  // O(B) -- positions k.. as a block of their own (this one keeps 0..k-1)
            bake();
            Block t;
            t.vals.assign(vals.begin() + k, vals.end());
            vals.resize(k);
            vector<T> s;
            vector<int> o;
            for (int i = 0; i < (int)ord.size(); i++) {
                if (ord[i] < k) s.push_back(srt[i]), o.push_back(ord[i]);
                else t.srt.push_back(srt[i]), t.ord.push_back(ord[i] - k);
            }
            srt = std::move(s), ord = std::move(o);
            refresh(), t.refresh();
            return t;
        }

        void absorb(Block& o) {  // O(B) -- o's values appended after this block's (o is left empty)
            bake(), o.bake();
            int m = size();
            vals.insert(vals.end(), o.vals.begin(), o.vals.end());
            for (int& p : o.ord) p += m;
            vector<T> s(vals.size());
            vector<int> w(vals.size());
            int i = 0, j = 0, k = 0;
            while (i < m || j < o.size()) {
                if (j == o.size() || (i < m && srt[i] <= o.srt[j])) s[k] = srt[i], w[k++] = ord[i++];
                else s[k] = o.srt[j], w[k++] = o.ord[j++];
            }
            srt = std::move(s), ord = std::move(w);
            o.vals.clear(), o.srt.clear(), o.ord.clear();
            refresh();
        }

        void sortedPart(int a, int c, vector<T>& out) const {  // O(B) -- the values at positions a..c, sorted
            int lo = a, hi = c;
            out.clear();
            for (int i = 0; i < size(); i++)
                if (lo <= ord[i] && ord[i] <= hi) out.push_back(T(srt[i]));
        }

        T get(int k) const {  // the value at position k of this block
            return T(vals[k]);
        }

        int below(T x, bool strict) const {  // how many values are < x (strict) or <= x
            const T& y = x;
            return int((strict ? lower_bound(srt.begin(), srt.end(), y) : upper_bound(srt.begin(), srt.end(), y)) - srt.begin());
        }

        T kth(int k) const {  // the k-th smallest value, k from 0
            return T(srt[k]);
        }

        T xorFirst(int k) const {  // the xor of the k smallest values
            return px[k];
        }

        T andRange(int i, int j) const {  // the AND of the i-th..(j-1)-th smallest (~0, every bit, if none)
            T res = ~T(0);
            for (i += size(), j += size(); i < j; i >>= 1, j >>= 1) {
                if (i & 1) res &= ta[i++];
                if (j & 1) res &= ta[--j];
            }
            return res;
        }

        T orRange(int i, int j) const {  // the OR of the i-th..(j-1)-th smallest (0 if none)
            T res = T(0);
            for (i += size(), j += size(); i < j; i >>= 1, j >>= 1) {
                if (i & 1) res |= to[i++];
                if (j & 1) res |= to[--j];
            }
            return res;
        }
    };

    // pieces (cut / split / trisect) are SqrtSequences of their own: paste / merge move their blocks over
    vector<Block> blocks;
    int n = 0, B = 16;

    // O(N log N) -- arr: the initial array (leave it out to start empty)
    explicit SqrtSequence(const vector<T>& arr = {}) { fill(arr); }

    // O(1) -- the current length of the array
    int size() const { return n; }

    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (const Block& b : blocks)
            for (int k = 0; k < b.size(); k++) out.push_back(b.get(k));
        return out;
    }

    // O(sqrt(N)) -- a[i]
    T pointGet(int i) const {
        auto [j, k] = at(i);
        return blocks[j].get(k);
    }

    // O(sqrt(N log N)) -- a[i] = v
    void pointAssign(int i, T v) {
        auto [j, k] = at(i);
        Block& b = blocks[j];
        T nv = v;
        b.update(k, k, [&](T) { return nv; });
    }

    // O(sqrt(N log N)) -- a[i] += v
    void pointAdd(int i, T v) {
        auto [j, k] = at(i);
        Block& b = blocks[j];
        T nv = T(b.get(k) + v);
        b.update(k, k, [&](T) { return nv; });
    }

    // O(sqrt(N log N)) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        auto [j, k] = at(i);
        Block& b = blocks[j];
        T nv = max(b.get(k), v);
        b.update(k, k, [&](T) { return nv; });
    }

    // O(sqrt(N log N)) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        auto [j, k] = at(i);
        Block& b = blocks[j];
        T nv = min(b.get(k), v);
        b.update(k, k, [&](T) { return nv; });
    }


    // O(sqrt(N) log N) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        auto [j, k] = at(i);
        if (j == (int)blocks.size()) {  // (the end: onto the last block)
            if (!j || blocks.back().size() >= 2 * B) {
                blocks.emplace_back(vector<T>{v}), n++;
                return;
            }
            j--, k = blocks.back().size();
        }
        blocks[j].insert(k, v);
        if (blocks[j].size() > 2 * B) {  // (too long: two blocks)
            Block tail = blocks[j].cutTail(blocks[j].size() / 2);
            blocks.insert(blocks.begin() + j + 1, std::move(tail));
        }
        n++;
        if (idealB(n) > 2 * B) fill(getAll());  // (grown a lot: bigger blocks)
    }

    // O(sqrt(N) log N) amortized -- append v to the end
    void append(T v) { insertAt(n, v); }

    // O(sqrt(N) log N) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(k + sqrt(N) log N) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int j = splitAt(i);
        vector<Block> add;
        for (long long s = 0; s < k; s += B) add.emplace_back(vector<T>(min<long long>(B, k - s), v));
        blocks.insert(blocks.begin() + j, make_move_iterator(add.begin()), make_move_iterator(add.end()));
        n += (int)k;
        tidy();
    }

    // O(sqrt(N) log N) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        long long len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        int j1 = splitAt(l), j2 = splitAt(l + (int)k), j3 = splitAt(r + 1);
        rotate(blocks.begin() + j1, blocks.begin() + j2, blocks.begin() + j3);
        tidy();
    }

    // O(sqrt(N) log N) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(sqrt(N) log N) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0)
    SqrtSequence cut(int l, int r) {
        int j1 = splitAt(l), j2 = splitAt(r + 1);
        SqrtSequence piece;
        piece.blocks.assign(make_move_iterator(blocks.begin() + j1), make_move_iterator(blocks.begin() + j2));
        piece.n = r - l + 1, piece.B = B;
        blocks.erase(blocks.begin() + j1, blocks.begin() + j2);
        n -= r - l + 1;
        tidy(), piece.tidy();
        return piece;
    }

    // O(sqrt(N) log N) amortized -- insert all of other (any SqrtSequence, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, SqrtSequence& other) {
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()), make_move_iterator(other.blocks.end()));
        n += other.n;
        other.blocks.clear(), other.n = 0;
        tidy();
    }

    // O(sqrt(N) log N) amortized -- append all of other at the end; other is left empty
    void merge(SqrtSequence& other) { paste(n, other); }

    // O(sqrt(N) log N) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty
    pair<SqrtSequence, SqrtSequence> split(int k) {
        SqrtSequence left;
        left.blocks = std::move(blocks), left.n = n, left.B = B;
        blocks.clear(), n = 0;
        SqrtSequence right = k < left.n ? left.cut(k, left.n - 1) : SqrtSequence();
        return {std::move(left), std::move(right)};
    }

    // O(sqrt(N) log N) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    // left empty
    tuple<SqrtSequence, SqrtSequence, SqrtSequence> trisect(int l, int r) {
        auto [left, right] = split(r + 1);
        auto [first, mid] = left.split(l);
        return {std::move(first), std::move(mid), std::move(right)};
    }

    // O(sqrt(N) log N) -- # of values < x in a[l..r]
    int countLtX(int l, int r, T x) const { return count(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- # of values <= x in a[l..r]
    int countLteX(int l, int r, T x) const { return count(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- # of values > x in a[l..r]
    int countGtX(int l, int r, T x) const { return count(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- # of values >= x in a[l..r]
    int countGteX(int l, int r, T x) const { return count(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? count(l, r, lowVal, highVal, false, false) : 0;
    }

    // O(sqrt(N) log N) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, T x) const { return count(l, r, x, x, false, false); }

    // O(sqrt(N) log N log U) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else
    // throws out_of_range (a binary search over the values, each step a count)
    T kthSmallest(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        vector<const Block*> whole;
        vector<vector<T>> parts;  // (the values of the partial blocks, sorted)
        span(l, r, [&](const Block& b, int a, int c, bool all, int) {
            if (all) whole.push_back(&b);
            else parts.emplace_back(), b.sortedPart(a, c, parts.back());
            return false;
        });
        optional<T> lo, hi;
        for (const Block* b : whole) lo = lo ? min(*lo, b->kth(0)) : b->kth(0), hi = hi ? max(*hi, b->kth(b->size() - 1)) : b->kth(b->size() - 1);
        for (auto& p : parts) lo = lo ? min(*lo, p.front()) : p.front(), hi = hi ? max(*hi, p.back()) : p.back();
        while (*lo < *hi) {
            T mid = *lo + (*hi - *lo) / 2;
            int c = 0;
            for (auto& p : parts) c += int(upper_bound(p.begin(), p.end(), mid) - p.begin());
            for (const Block* b : whole) c += b->below(mid, false);
            if (c >= k) hi = mid;
            else lo = mid + 1;
        }
        return *lo;
    }

    // O(sqrt(N) log N) -- min of a[l..r]
    T rangeMin(int l, int r) const {
        optional<T> best;
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) best = best ? min(*best, b.kth(0)) : b.kth(0);
            else for (int k = lo; k <= hi; k++) best = best ? min(*best, b.get(k)) : b.get(k);
            return false;
        });
        return *best;
    }

    // O(sqrt(N) log N) -- max of a[l..r]
    T rangeMax(int l, int r) const {
        optional<T> best;
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) best = best ? max(*best, b.kth(hi)) : b.kth(hi);
            else for (int k = lo; k <= hi; k++) best = best ? max(*best, b.get(k)) : b.get(k);
            return false;
        });
        return *best;
    }

    // O(sqrt(N) log N) -- smallest value >= x in a[l..r], or nullopt
    optional<T> smallestGteX(int l, int r, T x) const { return nearest(l, r, x, true, false); }

    // O(sqrt(N) log N) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(int l, int r, T x) const { return nearest(l, r, x, true, true); }

    // O(sqrt(N) log N) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(int l, int r, T x) const { return nearest(l, r, x, false, false); }

    // O(sqrt(N) log N) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(int l, int r, T x) const { return nearest(l, r, x, false, true); }

    // O(sqrt(N) log N) -- the first i with a[i] == x, or -1
    int leftmostIndexOf(T x) const { return n ? leftmostIndexOfInRange(0, n - 1, x) : -1; }

    // O(sqrt(N) log N) -- the last i with a[i] == x, or -1
    int rightmostIndexOf(T x) const { return n ? rightmostIndexOfInRange(0, n - 1, x) : -1; }

    // O(sqrt(N) log N) -- the first i in [l, r] with a[i] == x, or -1
    int leftmostIndexOfInRange(int l, int r, T x) const { return kthWhere(l, r, 1, x, x, false, false); }

    // O(sqrt(N) log N) -- the last i in [l, r] with a[i] == x, or -1
    int rightmostIndexOfInRange(int l, int r, T x) const { return kthWhere(l, r, -1, x, x, false, false); }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] < x, or -1
    int kthLtX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, nullopt, x, false, true) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] <= x, or -1
    int kthLteX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, nullopt, x, false, false) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] > x, or -1
    int kthGtX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, x, nullopt, true, false) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] >= x, or -1
    int kthGteX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, x, nullopt, false, false) : -1; }

    // O(sqrt(N) log N) -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) const { return xorOf(l, r, nullopt, nullopt, false, false); }

    // O(sqrt(N) log N) -- xor of the values < x in a[l..r] (copies count); 0 if there are none
    T xorLtX(int l, int r, T x) const { return xorOf(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none
    T xorLteX(int l, int r, T x) const { return xorOf(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- xor of the values > x in a[l..r] (copies count); 0 if there are none
    T xorGtX(int l, int r, T x) const { return xorOf(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none
    T xorGteX(int l, int r, T x) const { return xorOf(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- xor of the a[i] in [l, r] with lowVal <= a[i] <= highVal (copies count); 0 if there are none
    T xorInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? xorOf(l, r, lowVal, highVal, false, false) : T(0);
    }

    T xorOf(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        T res = T(0);
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block& b, int i, int j) { res ^= b.xorFirst(j) ^ b.xorFirst(i); }, [&](T v) { res ^= v; });
        return res;
    }

    // O(sqrt(N) log N) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) const { return andOf(l, r, nullopt, nullopt, false, false); }

    // O(sqrt(N) log N) -- AND of the values < x in a[l..r]; ~0 (every bit) if there are none
    T andLtX(int l, int r, T x) const { return andOf(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- AND of the values <= x in a[l..r]; ~0 (every bit) if there are none
    T andLteX(int l, int r, T x) const { return andOf(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- AND of the values > x in a[l..r]; ~0 (every bit) if there are none
    T andGtX(int l, int r, T x) const { return andOf(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- AND of the values >= x in a[l..r]; ~0 (every bit) if there are none
    T andGteX(int l, int r, T x) const { return andOf(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- AND of the a[i] in [l, r] with lowVal <= a[i] <= highVal; ~0 (every bit) if there are none
    T andInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? andOf(l, r, lowVal, highVal, false, false) : ~T(0);
    }

    T andOf(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        T res = ~T(0);
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block& b, int i, int j) { res &= b.andRange(i, j); }, [&](T v) { res &= v; });
        return res;
    }

    // O(sqrt(N) log N) -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) const { return orOf(l, r, nullopt, nullopt, false, false); }

    // O(sqrt(N) log N) -- OR of the values < x in a[l..r]; 0 if there are none
    T orLtX(int l, int r, T x) const { return orOf(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- OR of the values <= x in a[l..r]; 0 if there are none
    T orLteX(int l, int r, T x) const { return orOf(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- OR of the values > x in a[l..r]; 0 if there are none
    T orGtX(int l, int r, T x) const { return orOf(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- OR of the values >= x in a[l..r]; 0 if there are none
    T orGteX(int l, int r, T x) const { return orOf(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- OR of the a[i] in [l, r] with lowVal <= a[i] <= highVal; 0 if there are none
    T orInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? orOf(l, r, lowVal, highVal, false, false) : T(0);
    }

    T orOf(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        T res = T(0);
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block& b, int i, int j) { res |= b.orRange(i, j); }, [&](T v) { res |= v; });
        return res;
    }

    // ---- internals ----

    // sqrt(n log n): a query reads n / B blocks (a binary search each) and two partial ones
    static int idealB(int n) { return max(16, (int)sqrt((double)n * (__lg(max(n, 1)) + 1))); }

    void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }

    // O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
    // split that made it), so any two neighbours hold more than B values; when the array has grown so much that B is
    // too small, rebuild into even blocks (O(N log N), after about N new values)
    void tidy() {
        if (idealB(n) > 2 * B) return fill(getAll());
        vector<Block> out;
        for (Block& b : blocks) {
            if (!b.size()) continue;
            if (!out.empty() && out.back().size() + b.size() <= B) out.back().absorb(b);
            else out.push_back(std::move(b));
        }
        blocks = std::move(out);
    }

    pair<int, int> at(int i) const {  // (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
        for (int j = 0; j < (int)blocks.size(); j++) {
            if (i < blocks[j].size()) return {j, i};
            i -= blocks[j].size();
        }
        return {(int)blocks.size(), 0};
    }

    int splitAt(int i) {  // make a block start at a[i] (0 <= i <= size()): that block's index
        auto [j, k] = at(i);
        if (!k) return j;
        Block tail = blocks[j].cutTail(k);
        blocks.insert(blocks.begin() + j + 1, std::move(tail));
        return j + 1;
    }

    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
    // it, the index of its first value), until f returns true
    template <class F>
    void span(int l, int r, F f) const {
        int i = 0;
        for (const Block& b : blocks) {
            int m = b.size();
            if (i + m > l) {
                int lo = max(l - i, 0), hi = min(r - i, m - 1);
                if (f(b, lo, hi, lo == 0 && hi == m - 1, i) || i + m > r) return;
            }
            i += m;
        }
    }

    static bool passes(T v, const optional<T>& lo, const optional<T>& hi, bool loStrict, bool hiStrict) {
        return (!lo || (loStrict ? *lo < v : *lo <= v)) && (!hi || (hiStrict ? v < *hi : v <= *hi));
    }

    // the values v of a[l..r] with lo <(=) v <(=) hi (a missing bound: none): whole(b, i, j) for a whole block (its
    // i-th..(j-1)-th smallest pass), part(v) for each passing value of a partial one
    template <class W, class P>
    void select(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict, W whole, P part) const {
        span(l, r, [&](const Block& b, int a, int c, bool all, int) {
            if (all) whole(b, lo ? b.below(*lo, !loStrict) : 0, hi ? b.below(*hi, hiStrict) : b.size());
            else
                for (int k = a; k <= c; k++)
                    if (T v = b.get(k); passes(v, lo, hi, loStrict, hiStrict)) part(v);
            return false;
        });
    }

    int count(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        int res = 0;
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block&, int i, int j) { res += j - i; }, [&](T) { res++; });
        return res;
    }

    optional<T> nearest(int l, int r, T x, bool up, bool strict) const {  // the smallest > (>=) x (up) or largest < (<=)
        optional<T> best;
        auto take = [&](T v) {
            if (!best || (up ? v < *best : v > *best)) best = v;
        };
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) {
                int k = up ? b.below(x, !strict) : b.below(x, strict) - 1;
                if (k >= 0 && k < b.size()) take(b.kth(k));
            } else {
                for (int k = lo; k <= hi; k++) {
                    T v = b.get(k);
                    if (up ? (strict ? v > x : v >= x) : (strict ? v < x : v <= x)) take(v);
                }
            }
            return false;
        });
        return best;
    }

    // the index of the k-th i in [l, r] (k = -1: the last one) with lo <(=) a[i] <(=) hi, or -1: whole blocks are
    // skipped by their counts, and only the block holding it is read
    int kthWhere(int l, int r, int k, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        vector<tuple<const Block*, int, int, bool, int>> spans;
        span(l, r, [&](const Block& b, int a, int c, bool whole, int start) {
            spans.emplace_back(&b, a, c, whole, start);
            return false;
        });
        if (k < 0) reverse(spans.begin(), spans.end());
        for (auto [b, a, c, whole, start] : spans) {
            if (whole) {
                int cnt = (hi ? b->below(*hi, hiStrict) : b->size()) - (lo ? b->below(*lo, !loStrict) : 0);
                if (max(k, 1) > cnt) {
                    k -= cnt;
                    continue;
                }
            }
            for (int p = 0; p <= c - a; p++) {
                int pos = k < 0 ? c - p : a + p;
                if (passes(b->get(pos), lo, hi, loStrict, hiStrict)) {
                    if (k == 1 || k == -1) return start + pos;
                    k > 0 ? k-- : k++;
                }
            }
        }
        return -1;
    }
};
