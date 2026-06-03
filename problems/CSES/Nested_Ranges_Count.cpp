#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Used for sliding windows where we add & remove elements, find the k-th sorted element, and get the sum of the smallest X elements.
// It is built on values so as we slide around we add or remove values. To find k-th we do a walk (we store counts in a node, think like a seg tree). To find sum we add up sums stored in prefixes.
// Could support more things like sum of all numbers X <= ? <= Y by diffing.
// Various implementations, this one takes in a vector of all the starting values and compresses them so we can use sparse numbers. Query numbers don't get compressed so we binary search on a query range to find the nearest compressed range for the query.
// Could pre-compress all the query values too. Could also make the tree a dynamic segment tree on values so no compression is needed but then things become log(U).
// ⚠️ Not optimized
// Used in https://leetcode.com/problems/minimum-operations-to-equalize-subarrays/description/
struct OrderStatisticFenwick {
    int n;
    vector<long long> bitCnt, bitSum;
    vector<int> compToVal; // id -> original value (1-indexed)
    unordered_map<int,int> valToComp; // original value -> id (1-indexed)

    int totalCount = 0;
    long long totalSum = 0;

    OrderStatisticFenwick(const vector<int>& allValues) {
        vector<int> vals = allValues;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());

        n = (int)vals.size();
        bitCnt.assign(n + 1, 0);
        bitSum.assign(n + 1, 0);
        compToVal.assign(n + 1, 0);

        valToComp.reserve(n * 2);
        valToComp.max_load_factor(0.7f);

        for (int i = 0; i < n; i++) {
            compToVal[i + 1] = vals[i];
            valToComp[vals[i]] = i + 1;
        }
    }

    void _add(vector<long long>& bit, int i, long long v) {
        for (; i <= n; i += i & -i) bit[i] += v;
    }

    long long _sum(const vector<long long>& bit, int i) const {
        long long s = 0;
        for (; i > 0; i -= i & -i) s += bit[i];
        return s;
    }

    // Returns smallest id such that prefixCount(id) >= k. (k is 1-indexed)
    int _kthId(long long k) const {
        int idx = 0;
        int pw = 1;
        while ((pw << 1) <= n) pw <<= 1; // highest power of two <= n

        for (; pw; pw >>= 1) {
            int nxt = idx + pw;
            if (nxt <= n && bitCnt[nxt] < k) {
                k -= bitCnt[nxt];
                idx = nxt;
            }
        }
        return idx + 1;
    }

    void add(int x) {
        int id = valToComp[x];
        totalCount++;
        totalSum += x;
        _add(bitCnt, id, 1);
        _add(bitSum, id, x);
    }

    void remove(int x) {
        int id = valToComp[x];
        totalCount--;
        totalSum -= x;
        _add(bitCnt, id, -1);
        _add(bitSum, id, -x);
    }

    int kth(long long k) const { // k is 1-indexed
        int id = _kthId(k);
        return compToVal[id];
    }

    int median() const { // lower median
        return kth((totalCount + 1) / 2);
    }

    // Sum of the smallest k elements (counting duplicates). k can be 0...totalCount.
    // O(log N)
    long long sumSmallest(long long k) const {
        if (k <= 0) return 0;
        if (k >= totalCount) return totalSum;

        int id = _kthId(k); // id where the kth element lives
        long long cntBefore = _sum(bitCnt, id - 1);
        long long sumBefore = _sum(bitSum, id - 1);

        long long need = k - cntBefore; // how many copies from this value
        long long val = compToVal[id];

        return sumBefore + need * val;
    }

    int size() const { return totalCount; }
    long long sumAll() const { return totalSum; }
    // Number of elements with value <= x. O(log N).
    long long countLTEX(int x) const {
        int lo = 1, hi = n, id = 0;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (compToVal[mid] <= x) {
                id = mid;
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        if (id == 0) return 0;
        return _sum(bitCnt, id);
    }

    // Number of elements with value < x. O(log N).
    long long countLTX(int x) const {
        return countLTEX(x - 1);
    }

    // Number of elements with value >= x. O(log N).
    long long countGTEX(int x) const {
        return totalCount - countLTX(x);
    }

    // Number of elements with value > x. O(log N).
    long long countGTX(int x) const {
        return totalCount - countLTEX(x);
    }

    // Number of elements with value in [lo, hi]. O(log N).
    long long countInRange(int lo, int hi) const {
        if (lo > hi) return 0;
        return countLTEX(hi) - countLTX(lo);
    }

    // Sum of elements with value <= x. O(log N).
    long long sumLTEX(int x) const {
        int lo = 1, hi = n, id = 0;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (compToVal[mid] <= x) { id = mid; lo = mid + 1; }
            else hi = mid - 1;
        }
        if (id == 0) return 0;
        return _sum(bitSum, id);
    }

    // Sum of elements with value < x.
    long long sumLTX(int x) const { return sumLTEX(x - 1); }

    // Sum of elements with value > x.
    long long sumGTX(int x) const { return totalSum - sumLTEX(x); }

    // Sum of elements with value >= x.
    long long sumGTEX(int x) const { return totalSum - sumLTX(x); }

    // Sum of elements with value in [lo, hi].
    long long sumInRange(int lo, int hi) const {
        if (lo > hi) return 0;
        return sumLTEX(hi) - sumLTX(lo);
    }

    bool empty() const { return totalCount == 0; }

    int minVal() const { return kth(1); }            // smallest (1-indexed)
    int maxVal() const { return kth(totalCount); }   // largest

    // Cost to make every element equal to target t (sum of |element - t|).
    long long costToTarget(long long t) const {
        long long cntLE = countLTEX((int)t);
        long long sumLE = sumLTEX((int)t);
        long long cntGt = totalCount - cntLE;
        long long sumGt = totalSum - sumLE;
        return t * cntLE - sumLE + sumGt - t * cntGt;
    }

    long long costToMedian() const {
        return costToTarget(median());
    }

    // Largest value present <= x, or -1 if none.
    int largestValLTE(int x) const {
        long long c = countLTEX(x);
        if (c == 0) return -1;
        return kth(c);
    }

    // Largest value present < x, or -1 if none.
    int largestValLT(int x) const {
        long long c = countLTX(x);
        if (c == 0) return -1;
        return kth(c);
    }

    // Smallest value present >= x, or -1 if none.
    int smallestValGTE(int x) const {
        long long below = countLTX(x);
        if (below >= totalCount) return -1;
        return kth(below + 1);
    }

    // Smallest value present > x, or -1 if none.
    int smallestValGT(int x) const {
        long long below = countLTEX(x);
        if (below >= totalCount) return -1;
        return kth(below + 1);
    }
};

struct Range {
    int l, r, idx;
};

struct Query {
    int l;
    int r;
    int threshold;
    int rangeIdx;
    int sign;
};

struct QueryContainMe { 
    int r;
    int threshold;
    int rangeIdx;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<Range> ranges(n);
    for (int i = 0; i < n; i++) {
        int l, r; cin >> l >> r;
        ranges[i] = {l, r, i};
    }
    sort(ranges.begin(), ranges.end(), [](Range& left, Range& right) {
        if (left.l < right.l) return true;
        if (right.l < left.l) return false;
        if (left.r <= right.r) return true;
        return false;
    });

    vector<Query> queries;
    vector<QueryContainMe> queriesContainMe;

    vector<vector<Query>> iToQueries(n);
    vector<vector<QueryContainMe>> iToQueriesContainMe(n);

    // for each range, we identify the leftmost and rightmost indices that have a valid start
    for (auto& range : ranges) {
        // find leftmost idx with a left edge >= our left edge (we contain it)
        int L = 0;
        int R = n - 1;
        int resI = -1;
        while (L <= R) {
            int m = (L + R) / 2;
            if (ranges[m].l >= range.l) {
                resI = m;
                R = m - 1;
            } else {
                L = m + 1;
            }
        }

        // find rightmost idx with a left edge <= our right edge
        L = 0;
        R = n - 1;
        int resI2 = -1;
        while (L <= R) {
            int m = (L + R) / 2;
            if (ranges[m].l <= range.r) {
                resI2 = m;
                L = m + 1;
            } else {
                R = m - 1;
            }
        }

        // how many elements in resI...resI2 have a right value <= range.r?
        Query gain = {0, resI2, range.r, range.idx, 1};
        iToQueries[resI2].push_back(gain);
        queries.push_back(gain);
        if (resI > 0) {
            Query lost = {0, resI - 1, range.r, range.idx, -1};
            queries.push_back(lost);
            iToQueries[resI - 1].push_back(lost);
        }

        L = 0; R = n - 1; int J = -1;
        while (L <= R) {
            int m = (L + R) / 2;
            if (ranges[m].l <= range.l) { J = m; L = m + 1; }
            else R = m - 1;
        }
        QueryContainMe containMe = {range.r, range.r, range.idx};
        iToQueriesContainMe[J].push_back(containMe);
    }

    vector<int> rightEdges;
    for (auto& range : ranges) {
        rightEdges.push_back(range.r);
    }

    vector<int> resContains(n, 0);
    vector<int> resContainMe(n, 0);

    OrderStatisticFenwick os(rightEdges);

    for (int i = 0; i < n; i++) {
        auto& range = ranges[i];
        os.add(range.r);
        for (auto& q : iToQueries[i]) {
            ll ans = os.countLTEX(q.threshold);
            resContains[q.rangeIdx] += (q.sign == 1 ? ans : -ans);
        }
        for (auto& q : iToQueriesContainMe[i]) {
            ll ans = os.countGTEX(q.r);
            resContainMe[q.rangeIdx] += ans;
        }
    }

    // cout << "printing contains: " << endl;
    for (int i = 0; i < n; i++) {
        cout << resContains[i] - 1 << " ";
    }
    cout << endl;
    for (int i = 0; i < n; i++) {
        cout << resContainMe[i] - 1 << " ";
    }
}