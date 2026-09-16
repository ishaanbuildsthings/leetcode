// TEMPLATE BY https://github.com/agrawalishaan

// ========================
// COMPLEXITIES

// O(n log n) build

// O(root n * log n) for:
// range add
// range chmin
// range chmax
// range sum
// range assign
// range count values in value range a...b

// O(1) point get

// ========================
// Templated on the value type. SqrtBlocks_PERFORMANT sb(vec) deduces it, so int stays
// int arithmetic and double stays double -- no boxing, no conversions in the hot loops.
// The sum accumulator widens on its own (long long for integral T, double for floating),
// so rangeSum on a vector<int> cannot overflow.
// POSINF / NEGINF are the type's own infinities when it has them, otherwise its numeric
// limits, and they are treated as absorbing under rangeAdd so a sentinel never overflows.

#include <algorithm>
#include <cmath>
#include <limits>
#include <type_traits>
#include <vector>

template <typename T>
struct SqrtBlocks_PERFORMANT {
    using SumT = std::conditional_t<std::is_floating_point_v<T>, double, long long>;

    static constexpr T POSINF = std::numeric_limits<T>::has_infinity
        ? std::numeric_limits<T>::infinity() : std::numeric_limits<T>::max();
    static constexpr T NEGINF = std::numeric_limits<T>::has_infinity
        ? -std::numeric_limits<T>::infinity() : std::numeric_limits<T>::lowest();

    int n, blockSize, numBlocks;
    std::vector<T> valsBeforeTags;
    std::vector<std::vector<T>> sortedBeforeTags;
    std::vector<std::vector<SumT>> pfSum;
    std::vector<int> blockEnd, blockSz;
    bool sumReady = false; // prefix sums cost O(root N) per rebuild; don't pay until rangeSum is used
    std::vector<T> lazyAdd, lazyChmin, lazyChmax;

    // O(N log N)
    explicit SqrtBlocks_PERFORMANT(const std::vector<T>& arr) {
        n = (int)arr.size();
        blockSize = std::max(1, (int)std::sqrt((double)std::max(1, n)));
        numBlocks = (n + blockSize - 1) / blockSize;
        valsBeforeTags = arr;
        sortedBeforeTags.resize(numBlocks);
        pfSum.resize(numBlocks);
        blockEnd.resize(numBlocks);
        blockSz.resize(numBlocks);
        lazyAdd.assign(numBlocks, T(0));
        lazyChmin.assign(numBlocks, POSINF);  // the ceiling
        lazyChmax.assign(numBlocks, NEGINF);  // the floor
        for (int b = 0; b < numBlocks; b++) {
            int lo = b * blockSize, hi = std::min((b + 1) * blockSize, n) - 1;
            blockEnd[b] = hi;
            blockSz[b] = hi - lo + 1;
            sortedBeforeTags[b].assign(arr.begin() + lo, arr.begin() + hi + 1);
            std::sort(sortedBeforeTags[b].begin(), sortedBeforeTags[b].end());
        }
    }

    void buildPf(int b) {
        const auto& srt = sortedBeforeTags[b];
        auto& pf = pfSum[b];
        pf.resize(srt.size());
        SumT run = 0;
        for (size_t k = 0; k < srt.size(); k++) { run += (SumT)srt[k]; pf[k] = run; }
    }

    // O(root N log N) -- re-sort one block after its slots were edited directly
    void refresh(int b) {
        int lo = b * blockSize;
        auto& srt = sortedBeforeTags[b];
        srt.assign(valsBeforeTags.begin() + lo, valsBeforeTags.begin() + blockEnd[b] + 1);
        std::sort(srt.begin(), srt.end());
        if (sumReady) buildPf(b);
    }

    static inline bool isSentinel(T v) { return v == POSINF || v == NEGINF; }

    // O(root N) -- bake the tags in and clear them. Branches on which tags are live:
    // a ceiling-only block clamps its sorted copy with one binary search plus a fill.
    void push(int b) {
        T add = lazyAdd[b], chmin = lazyChmin[b], chmax = lazyChmax[b];
        if (add == T(0) && chmin == POSINF && chmax == NEGINF) return;
        int lo = b * blockSize, hi = blockEnd[b];
        auto& vals = valsBeforeTags;
        auto& srt = sortedBeforeTags[b];
        int sz = (int)srt.size();
        if (chmin == chmax) { // assigned block
            std::fill(vals.begin() + lo, vals.begin() + hi + 1, chmin);
            std::fill(srt.begin(), srt.end(), chmin);
        } else if (add == T(0) && chmax == NEGINF) { // ceiling only
            for (int i = lo; i <= hi; i++) if (vals[i] > chmin) vals[i] = chmin;
            int cut = (int)(std::upper_bound(srt.begin(), srt.end(), chmin) - srt.begin());
            if (cut < sz) std::fill(srt.begin() + cut, srt.end(), chmin);
        } else if (add == T(0) && chmin == POSINF) { // floor only
            for (int i = lo; i <= hi; i++) if (vals[i] < chmax) vals[i] = chmax;
            int cut = (int)(std::lower_bound(srt.begin(), srt.end(), chmax) - srt.begin());
            if (cut) std::fill(srt.begin(), srt.begin() + cut, chmax);
        } else if (chmin == POSINF && chmax == NEGINF) { // add only
            for (int i = lo; i <= hi; i++) if (!isSentinel(vals[i])) vals[i] += add;
            for (int k = 0; k < sz; k++) if (!isSentinel(srt[k])) srt[k] += add;
        } else {
            for (int i = lo; i <= hi; i++) {
                T v = vals[i];
                if (!isSentinel(v)) v += add;
                if (v < chmax) v = chmax; else if (v > chmin) v = chmin;
                vals[i] = v;
            }
            for (int k = 0; k < sz; k++) {
                T v = srt[k];
                if (!isSentinel(v)) v += add;
                if (v < chmax) v = chmax; else if (v > chmin) v = chmin;
                srt[k] = v;
            }
        }
        if (sumReady) buildPf(b);
        lazyAdd[b] = T(0); lazyChmin[b] = POSINF; lazyChmax[b] = NEGINF;
    }

    //////////////// PUBLIC METHODS START HERE ////////////////

    // O(1)
    T pointGet(int i) const {
        int b = i / blockSize;
        T v = valsBeforeTags[i];
        if (!isSentinel(v)) v += lazyAdd[b];
        T cx = lazyChmax[b];
        if (v < cx) return cx;
        T cn = lazyChmin[b];
        if (v > cn) return cn;
        return v;
    }

    // O(root N) -- one element moves in the sorted copy, so erase + insert, no re-sort
    void pointAssign(int i, T newVal) {
        int b = i / blockSize;
        push(b);
        T oldVal = valsBeforeTags[i];
        if (oldVal == newVal) return;
        valsBeforeTags[i] = newVal;
        auto& srt = sortedBeforeTags[b];
        srt.erase(std::lower_bound(srt.begin(), srt.end(), oldVal));
        srt.insert(std::lower_bound(srt.begin(), srt.end(), newVal), newVal);
        if (sumReady) buildPf(b);
    }

    // O(root N log N) -- every slot in l...r becomes min(value, x)
    // A block fully covered by the range takes the O(1) tag path even when it is the
    // first or last block -- ranges anchored at 0 or n-1 are common.
    void rangeChmin(int l, int r, T x) {
        if (l > r) return;
        int B = blockSize, bl = l / B, br = r / B;
        auto& vals = valsBeforeTags;
        if (bl != br || l != bl * B || r != blockEnd[bl]) {
            if (l > bl * B) {
                push(bl);
                int end = (bl != br) ? blockEnd[bl] : r;
                for (int i = l; i <= end; i++) if (vals[i] > x) vals[i] = x;
                refresh(bl);
                if (bl == br) return;
                bl++;
            }
            if (br >= bl && r < blockEnd[br]) {
                push(br);
                for (int i = br * B; i <= r; i++) if (vals[i] > x) vals[i] = x;
                refresh(br);
                br--;
            }
        }
        for (int b = bl; b <= br; b++) {
            if (lazyChmin[b] > x) lazyChmin[b] = x; // drop the ceiling
            if (lazyChmax[b] > x) lazyChmax[b] = x; // and the floor, if the ceiling went below it
        }
    }

    // O(root N log N) -- every slot in l...r becomes max(value, x)
    void rangeChmax(int l, int r, T x) {
        if (l > r) return;
        int B = blockSize, bl = l / B, br = r / B;
        auto& vals = valsBeforeTags;
        if (bl != br || l != bl * B || r != blockEnd[bl]) {
            if (l > bl * B) {
                push(bl);
                int end = (bl != br) ? blockEnd[bl] : r;
                for (int i = l; i <= end; i++) if (vals[i] < x) vals[i] = x;
                refresh(bl);
                if (bl == br) return;
                bl++;
            }
            if (br >= bl && r < blockEnd[br]) {
                push(br);
                for (int i = br * B; i <= r; i++) if (vals[i] < x) vals[i] = x;
                refresh(br);
                br--;
            }
        }
        for (int b = bl; b <= br; b++) {
            if (lazyChmax[b] < x) lazyChmax[b] = x; // raise the floor
            if (lazyChmin[b] < x) lazyChmin[b] = x; // and the ceiling, if the floor went above it
        }
    }

    // O(root N log N) -- every slot in l...r becomes x
    void rangeAssign(int l, int r, T x) {
        if (l > r) return;
        int B = blockSize, bl = l / B, br = r / B;
        auto& vals = valsBeforeTags;
        if (bl != br || l != bl * B || r != blockEnd[bl]) {
            if (l > bl * B) {
                push(bl);
                int end = (bl != br) ? blockEnd[bl] : r;
                for (int i = l; i <= end; i++) vals[i] = x;
                refresh(bl);
                if (bl == br) return;
                bl++;
            }
            if (br >= bl && r < blockEnd[br]) {
                push(br);
                for (int i = br * B; i <= r; i++) vals[i] = x;
                refresh(br);
                br--;
            }
        }
        for (int b = bl; b <= br; b++) {
            lazyAdd[b] = T(0);
            lazyChmin[b] = x;
            lazyChmax[b] = x;
        }
    }

    // O(root N log N) -- every slot in l...r becomes value + diff
    void rangeAdd(int l, int r, T diff) {
        if (l > r) return;
        int B = blockSize, bl = l / B, br = r / B;
        auto& vals = valsBeforeTags;
        if (bl != br || l != bl * B || r != blockEnd[bl]) {
            if (l > bl * B) {
                push(bl);
                int end = (bl != br) ? blockEnd[bl] : r;
                for (int i = l; i <= end; i++) if (!isSentinel(vals[i])) vals[i] += diff;
                refresh(bl);
                if (bl == br) return;
                bl++;
            }
            if (br >= bl && r < blockEnd[br]) {
                push(br);
                for (int i = br * B; i <= r; i++) if (!isSentinel(vals[i])) vals[i] += diff;
                refresh(br);
                br--;
            }
        }
        for (int b = bl; b <= br; b++) {
            lazyAdd[b] += diff;
            if (lazyChmin[b] != POSINF) lazyChmin[b] += diff;
            if (lazyChmax[b] != NEGINF) lazyChmax[b] += diff;
        }
    }

    // O(root N log N) -- count of slots in l...r whose value is in low...high
    long long countValsInRange(int l, int r, T low, T high) const {
        if (l > r) return 0;
        int B = blockSize, bl = l / B, br = r / B;
        const auto& vals = valsBeforeTags;
        long long res = 0;
        // partial ends, scanned slot by slot
        if (bl == br && (l > bl * B || r < blockEnd[bl])) {
            T add = lazyAdd[bl], cn = lazyChmin[bl], cx = lazyChmax[bl];
            if (add == T(0) && cn == POSINF && cx == NEGINF) {
                for (int i = l; i <= r; i++) if (vals[i] >= low && vals[i] <= high) res++;
            } else {
                for (int i = l; i <= r; i++) {
                    T v = vals[i];
                    if (!isSentinel(v)) v += add;
                    if (v < cx) v = cx; else if (v > cn) v = cn;
                    if (v >= low && v <= high) res++;
                }
            }
            return res;
        }
        if (l > bl * B) {
            T add = lazyAdd[bl], cn = lazyChmin[bl], cx = lazyChmax[bl];
            int end = blockEnd[bl];
            if (add == T(0) && cn == POSINF && cx == NEGINF) {
                for (int i = l; i <= end; i++) if (vals[i] >= low && vals[i] <= high) res++;
            } else {
                for (int i = l; i <= end; i++) {
                    T v = vals[i];
                    if (!isSentinel(v)) v += add;
                    if (v < cx) v = cx; else if (v > cn) v = cn;
                    if (v >= low && v <= high) res++;
                }
            }
            bl++;
        }
        if (r < blockEnd[br]) {
            T add = lazyAdd[br], cn = lazyChmin[br], cx = lazyChmax[br];
            int start = br * B;
            if (add == T(0) && cn == POSINF && cx == NEGINF) {
                for (int i = start; i <= r; i++) if (vals[i] >= low && vals[i] <= high) res++;
            } else {
                for (int i = start; i <= r; i++) {
                    T v = vals[i];
                    if (!isSentinel(v)) v += add;
                    if (v < cx) v = cx; else if (v > cn) v = cn;
                    if (v >= low && v <= high) res++;
                }
            }
            br--;
        }
        // whole blocks, inline -- a call per block costs more than the work
        for (int b = bl; b <= br; b++) {
            const auto& srt = sortedBeforeTags[b];
            int sz = blockSz[b];
            if (!sz) continue;
            auto lb = [&](T key) { return (long long)(std::lower_bound(srt.begin(), srt.end(), key) - srt.begin()); };
            auto ub = [&](T key) { return (long long)(std::upper_bound(srt.begin(), srt.end(), key) - srt.begin()); };
            T add = lazyAdd[b], cn = lazyChmin[b], cx = lazyChmax[b];
            if (add == T(0) && cn == POSINF && cx == NEGINF) { // untagged
                if (high >= srt[sz - 1]) res += (low <= srt[0]) ? sz : sz - lb(low);
                else if (low <= srt[0])  res += ub(high);
                else                     res += ub(high) - lb(low);
                continue;
            }
            if (add == T(0) && cx == NEGINF) { // ceiling only: value = min(stored, cn)
                if (cn < low) continue; // every value sits below the window
                if (high >= cn)         // the upper bound never binds
                    res += (low <= srt[0]) ? sz : sz - lb(low);
                else if (low <= srt[0]) // high < cn, so the clamp never binds either
                    res += ub(high);
                else
                    res += ub(high) - lb(low);
                continue;
            }
            if (add == T(0) && cn == POSINF) { // floor only: value = max(stored, cx)
                if (cx > high) continue; // every value sits above the window
                if (low <= cx)           // the lower bound never binds
                    res += (high >= srt[sz - 1]) ? sz : ub(high);
                else if (high >= srt[sz - 1])
                    res += sz - lb(low);
                else
                    res += ub(high) - lb(low);
                continue;
            }
            if (cn == cx) { // assigned
                if (low <= cn && cn <= high) res += sz;
                continue;
            }
            long long numLtFloor = (cx == NEGINF) ? 0 : lb(cx - add);
            long long numGtCeil = (cn == POSINF) ? 0 : sz - ub(cn - add);
            long long mid = sz - numLtFloor - numGtCeil;
            if (low <= cx && cx <= high) res += numLtFloor;
            if (low <= cn && cn <= high) res += numGtCeil;
            if (mid) {
                auto bg = srt.begin() + numLtFloor;
                auto en = bg + mid;
                res += (std::upper_bound(bg, en, (T)(high - add)) - bg)
                     - (std::lower_bound(bg, en, (T)(low - add)) - bg);
            }
        }
        return res;
    }

    // O(root N log N) -- sum of l...r. assumes finite values
    SumT rangeSum(int l, int r) {
        if (l > r) return SumT(0);
        if (!sumReady) { // first call: build every block's prefix sums
            sumReady = true;
            for (int b = 0; b < numBlocks; b++) buildPf(b);
        }
        int B = blockSize, bl = l / B, br = r / B;
        const auto& vals = valsBeforeTags;
        SumT res = 0;
        auto scan = [&](int b, int lo, int hi) {
            T add = lazyAdd[b], cn = lazyChmin[b], cx = lazyChmax[b];
            SumT acc = 0;
            if (add == T(0) && cn == POSINF && cx == NEGINF) {
                for (int i = lo; i <= hi; i++) acc += (SumT)vals[i];
                return acc;
            }
            for (int i = lo; i <= hi; i++) {
                T v = vals[i];
                if (!isSentinel(v)) v += add;
                if (v < cx) v = cx; else if (v > cn) v = cn;
                acc += (SumT)v;
            }
            return acc;
        };
        if (bl == br && (l > bl * B || r < blockEnd[bl])) return scan(bl, l, r);
        if (l > bl * B) { res += scan(bl, l, blockEnd[bl]); bl++; }
        if (r < blockEnd[br]) { res += scan(br, br * B, r); br--; }
        for (int b = bl; b <= br; b++) {
            const auto& srt = sortedBeforeTags[b];
            int sz = blockSz[b];
            if (!sz) continue;
            const auto& pf = pfSum[b];
            T add = lazyAdd[b], cn = lazyChmin[b], cx = lazyChmax[b];
            if (add == T(0) && cn == POSINF && cx == NEGINF) { res += pf[sz - 1]; continue; }
            if (cn == cx) { res += (SumT)sz * (SumT)cn; continue; }
            long long numLtFloor = (cx == NEGINF) ? 0
                : (long long)(std::lower_bound(srt.begin(), srt.end(), (T)(cx - add)) - srt.begin());
            long long numGtCeil = (cn == POSINF) ? 0
                : sz - (long long)(std::upper_bound(srt.begin(), srt.end(), (T)(cn - add)) - srt.begin());
            long long mid = sz - numLtFloor - numGtCeil;
            if (numLtFloor) res += (SumT)numLtFloor * (SumT)cx;
            if (numGtCeil) res += (SumT)numGtCeil * (SumT)cn;
            if (mid) {
                long long L = numLtFloor, R = L + mid - 1;
                res += pf[R] - (L ? pf[L - 1] : SumT(0)) + (SumT)add * (SumT)mid;
            }
        }
        return res;
    }
};

template <typename T>
SqrtBlocks_PERFORMANT(const std::vector<T>&) -> SqrtBlocks_PERFORMANT<T>;