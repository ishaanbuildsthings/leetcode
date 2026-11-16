// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/batch-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd rectSum
// @data-structure-type: offline-sweep
// @input: batch
// @complexities:
//   pointAdd: log^2(N) amortized
//   rectSum: log^2(N) amortized
//   build: 1
// @memory:
//   layout: none
//   node: bit[1*N]
//   tags: none
//   other: events[1*N] items[4*N] merged[4*N] ys[1*N] answers[1*N]
//   note: N = how many calls were recorded; in solve a rectSum becomes four items (its corners), and merged is the merge buffer

// Sanitizers are skipped inside this template (its methods start with LEETCODE_NO_SANITIZE): where they run, like on
// LeetCode, that is most of its speed. The drawback: a bad memory access inside the template goes unreported. Arguments
// are still checked and still throw. Constructors are left alone. It needs GCC or Clang and C++17.

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// min / max that still inline with sanitizers skipped (std::min and std::max do not)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }
// how many of the n sorted values at `first` are <= x (std::upper_bound as a count)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE int hotUpperBound(const A* first, int n, A x) {
    int lo = 0;
    while (n > 0) {
        int half = n >> 1;
        if (!(x < first[lo + half])) lo += half + 1, n -= half + 1;
        else n = half;
    }
    return lo;
}

// Point add and rectangle sum over any coordinates, answered all at once: linear memory, O(N log^2 N) in total. Call
// pointAdd and rectSum in the order they happen (they are only recorded: rectSum returns which query it is, 0, 1, 2,
// ...), then solve() returns every answer, answers[i] for query i. Use it only when no call depends on an earlier
// answer. A rectangle sum is four corner sums (how much was added at x <= X and y <= Y before this moment). The calls
// are split in half by time, again and again: the adds of an earlier half count for the corners of the later half,
// and with both halves sorted by x that is one sweep with a Fenwick tree over y. Rectangles are inclusive, x1..x2 by
// y1..y2; coordinates are any integers.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct OfflineRectSum {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Event {  // in call order: an add (query = -1) at (x1, y1), or a sum over x1..x2, y1..y2
        ll x1, y1, x2, y2;
        T v;
        int query;
    };
    HotVector<Event> events;
    int queries = 0;

    // O(1) -- nothing recorded yet
    OfflineRectSum() {}

    // O(1) now (O(log^2 N) amortized in solve) -- records: add v at (x, y)
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        events.push_back({x, y, 0, 0, v, -1});
    }

    // O(1) now (O(log^2 N) amortized in solve) -- records: sum of everything added so far at x1 <= x <= x2 and y1 <=
    // y <=
    // y2. Returns this query's number: its answer is solve()[that number]; needs x1 <= x2 and y1 <= y2, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE int rectSum(ll x1, ll y1, ll x2, ll y2) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        events.push_back({x1, y1, x2, y2, T(0), queries});
        return queries++;
    }

    // O(N log^2 N) -- every rectSum's answer, in the order they were asked (can be called again after more calls)
    LEETCODE_NO_SANITIZE vector<S> solve() const {
        HotVector<ll> ys;
        for (auto& e : events)
            if (e.query < 0) ys.push_back(e.y1);
        sort(ys.begin(), ys.end());
        ys.erase(unique(ys.begin(), ys.end()), ys.end());
        int m = (int)ys.size();
        // distinct add-y's <= y
        auto upTo = [&](ll y) LEETCODE_NO_SANITIZE { return m ? hotUpperBound(&ys[0], m, y) : 0; };
        // one item per add, four per sum (its corners)
        struct Item {
            ll x;
            int y;
            S amount;  // what an add adds; +1 / -1 for a corner
            int query;
        };
        int n = (int)events.size() + 3 * queries, filled = 0;
        HotVector<Item> items(n), merged(n);
        for (int e = 0; e < (int)events.size(); e++) {
            const Event& ev = events[e];
            if (ev.query < 0) {
                items[filled++] = {ev.x1, upTo(ev.y1), S(ev.v), -1};
            } else {
                int top = upTo(ev.y2), bot = upTo(ev.y1 - 1);
                items[filled++] = {ev.x2, top, 1, ev.query}, items[filled++] = {ev.x1 - 1, top, -1, ev.query};
                items[filled++] = {ev.x2, bot, -1, ev.query}, items[filled++] = {ev.x1 - 1, bot, 1, ev.query};
            }
        }
        HotVector<S> answers(queries, 0), bit(m + 1, 0);
        // blocks of `width` items, each already sorted by x; neighbors are an earlier and a later stretch of time
        for (int width = 1; width < n; width *= 2) {
            for (int l = 0; l + width < n; l += 2 * width) {
                int mid = l + width, r = hotMin(mid + width, n), i = l;
                for (int j = mid; j < r; j++) {
                    if (items[j].query < 0) continue;
                    // the earlier adds at or left of this corner go into the tree
                    for (; i < mid && items[i].x <= items[j].x; i++)
                        if (items[i].query < 0)
                            for (int k = items[i].y; k <= m; k += k & -k) bit[k] += items[i].amount;
                    S total = 0;
                    for (int k = items[j].y; k > 0; k &= k - 1) total += bit[k];
                    answers[items[j].query] += items[j].amount * total;
                }
                for (int t = l; t < i; t++)  // take them back out
                    if (items[t].query < 0)
                        for (int k = items[t].y; k <= m; k += k & -k) bit[k] -= items[t].amount;
                int a = l, b = mid, t = l;  // merge the two halves by x (the earlier one first on a tie)
                while (a < mid && b < r) merged[t++] = items[b].x < items[a].x ? items[b++] : items[a++];
                while (a < mid) merged[t++] = items[a++];
                while (b < r) merged[t++] = items[b++];
                for (t = l; t < r; t++) items[t] = merged[t];
            }
        }
        return vector<S>(std::move(answers));
    }
};
