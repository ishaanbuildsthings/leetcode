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
//   other: events[5*N] ys[1*N] answers[1*N]
//   note: N = how many calls were recorded; a rectSum is stored as its four corners

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
    vector<Event> events;
    int queries = 0;

    // O(1) -- nothing recorded yet
    OfflineRectSum() {}

    // O(1) now (O(log^2 N) amortized in solve) -- records: add v at (x, y)
    void pointAdd(ll x, ll y, T v) {
        events.push_back({x, y, 0, 0, v, -1});
    }

    // O(1) now (O(log^2 N) amortized in solve) -- records: sum of everything added so far at x1 <= x <= x2 and y1 <=
    // y <=
    // y2. Returns this query's number: its answer is solve()[that number]; needs x1 <= x2 and y1 <= y2, else throws
    // out_of_range
    int rectSum(ll x1, ll y1, ll x2, ll y2) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        events.push_back({x1, y1, x2, y2, T(0), queries});
        return queries++;
    }

    // O(N log^2 N) -- every rectSum's answer, in the order they were asked (can be called again after more calls)
    vector<S> solve() const {
        vector<ll> ys;
        for (auto& e : events)
            if (e.query < 0) ys.push_back(e.y1);
        sort(ys.begin(), ys.end());
        ys.erase(unique(ys.begin(), ys.end()), ys.end());
        // distinct add-y's <= y
        auto upTo = [&](ll y) { return (int)(upper_bound(ys.begin(), ys.end(), y) - ys.begin()); };
        // one item per add, four per sum (its corners)
        struct Item {
            ll x;
            int y;
            S amount;  // what an add adds; +1 / -1 for a corner
            int query;
        };
        vector<Item> items;
        for (auto& e : events) {
            if (e.query < 0) {
                items.push_back({e.x1, upTo(e.y1), S(e.v), -1});
            } else {
                int top = upTo(e.y2), bot = upTo(e.y1 - 1);
                items.push_back({e.x2, top, 1, e.query}), items.push_back({e.x1 - 1, top, -1, e.query});
                items.push_back({e.x2, bot, -1, e.query}), items.push_back({e.x1 - 1, bot, 1, e.query});
            }
        }
        vector<S> answers(queries, 0);
        int m = (int)ys.size(), n = (int)items.size();
        vector<S> bit(m + 1, 0);
        auto byX = [](const Item& a, const Item& b) { return a.x < b.x; };
        // blocks of `width` items, each already sorted by x; neighbors are an earlier and a later stretch of time
        for (int width = 1; width < n; width *= 2) {
            for (int l = 0; l + width < n; l += 2 * width) {
                int mid = l + width, r = min(mid + width, n), i = l;
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
                inplace_merge(items.begin() + l, items.begin() + mid, items.begin() + r, byX);
            }
        }
        return answers;
    }
};
