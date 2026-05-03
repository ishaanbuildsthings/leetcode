// SOLUTION 0, seg tree walk
#include <bits/stdc++.h>
using namespace std;
struct Node {
    int alive = 0;
};
struct Seg {
    vector<Node> tree;
    int n;
    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1);
    }
    Node _combine(Node& a, Node& b) {
        return {a.alive + b.alive};
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2*nodeI],tree[2*nodeI+1]);
    }
    void _build(int nodeI, int tl, int tr) {
        if (tl == tr) {
            tree[nodeI] = {1};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm);
        _build(2 * nodeI + 1, tm + 1, tr);
        _pull(nodeI);
    }

    int _removeKthAndReturnOriginalIndex(int nodeI, int tl, int tr, int kLeft) {
        if (kLeft > tree[nodeI].alive) {
            return -1;
        }
        if (tl == tr) {
            tree[nodeI].alive = 0;
            return tl;
        }
        int left = tree[2*nodeI].alive;
        int tm = (tl + tr) / 2;
        int ans;
        if (kLeft <= left) {
            ans = _removeKthAndReturnOriginalIndex(2*nodeI, tl, tm, kLeft);
        } else {
            int right = tree[2*nodeI + 1].alive;
            ans = _removeKthAndReturnOriginalIndex(2*nodeI + 1, tm + 1, tr, kLeft - left);
        }
        tree[nodeI].alive = tree[2*nodeI].alive + tree[2*nodeI+1].alive;
        return ans;
    }

    // returns -1 if kth doesn't exist (but it always does for this problem)
    int removeKthAndReturnOriginalIndex(int k) {
        return _removeKthAndReturnOriginalIndex(1, 0, n - 1, k);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    Seg seg(A);
    for (int i = 0; i < n; i++) {
        int p; cin >> p;
        int idx = seg.removeKthAndReturnOriginalIndex(p);
        int val = A[idx];
        cout << val << " ";
    }
}
// SOLUTION 1, sorted container
// #include <bits/stdc++.h>
// using namespace std;
// // Used for sliding windows where we add & remove elements, find the k-th sorted element, and get the sum of the smallest X elements.
// // It is built on values so as we slide around we add or remove values. To find k-th we do a walk (we store counts in a node, think like a seg tree). To find sum we add up sums stored in prefixes.
// // Could support more things like sum of all numbers X <= ? <= Y by diffing.
// // Various implementations, this one takes in a vector of all the starting values and compresses them so we can use sparse numbers. Query numbers don't get compressed so we binary search on a query range to find the nearest compressed range for the query.
// // Could pre-compress all the query values too. Could also make the tree a dynamic segment tree on values so no compression is needed but then things become log(U).
// // ⚠️ Not optimized
// // Used in https://leetcode.com/problems/minimum-operations-to-equalize-subarrays/description/
// struct OrderStatisticFenwick {
//     int n;
//     vector<long long> bitCnt, bitSum;
//     vector<int> compToVal; // id -> original value (1-indexed)
//     unordered_map<int,int> valToComp; // original value -> id (1-indexed)

//     int totalCount = 0;
//     long long totalSum = 0;

//     OrderStatisticFenwick(const vector<int>& allValues) {
//         vector<int> vals = allValues;
//         sort(vals.begin(), vals.end());
//         vals.erase(unique(vals.begin(), vals.end()), vals.end());

//         n = (int)vals.size();
//         bitCnt.assign(n + 1, 0);
//         bitSum.assign(n + 1, 0);
//         compToVal.assign(n + 1, 0);

//         valToComp.reserve(n * 2);
//         valToComp.max_load_factor(0.7f);

//         for (int i = 0; i < n; i++) {
//             compToVal[i + 1] = vals[i];
//             valToComp[vals[i]] = i + 1;
//         }
//     }

//     void _add(vector<long long>& bit, int i, long long v) {
//         for (; i <= n; i += i & -i) bit[i] += v;
//     }

//     long long _sum(const vector<long long>& bit, int i) const {
//         long long s = 0;
//         for (; i > 0; i -= i & -i) s += bit[i];
//         return s;
//     }

//     // Returns smallest id such that prefixCount(id) >= k. (k is 1-indexed)
//     int _kthId(long long k) const {
//         int idx = 0;
//         int pw = 1;
//         while ((pw << 1) <= n) pw <<= 1; // highest power of two <= n

//         for (; pw; pw >>= 1) {
//             int nxt = idx + pw;
//             if (nxt <= n && bitCnt[nxt] < k) {
//                 k -= bitCnt[nxt];
//                 idx = nxt;
//             }
//         }
//         return idx + 1;
//     }

//     void add(int x) {
//         int id = valToComp[x];
//         totalCount++;
//         totalSum += x;
//         _add(bitCnt, id, 1);
//         _add(bitSum, id, x);
//     }

//     void remove(int x) {
//         int id = valToComp[x];
//         totalCount--;
//         totalSum -= x;
//         _add(bitCnt, id, -1);
//         _add(bitSum, id, -x);
//     }

//     int kth(long long k) const { // k is 1-indexed
//         int id = _kthId(k);
//         return compToVal[id];
//     }

//     int median() const { // lower median
//         return kth((totalCount + 1) / 2);
//     }

//     // Sum of the smallest k elements (counting duplicates). k can be 0..totalCount.
//     // O(log N)
//     long long sumSmallest(long long k) const {
//         if (k <= 0) return 0;
//         if (k >= totalCount) return totalSum;

//         int id = _kthId(k); // id where the kth element lives
//         long long cntBefore = _sum(bitCnt, id - 1);
//         long long sumBefore = _sum(bitSum, id - 1);

//         long long need = k - cntBefore; // how many copies from this value
//         long long val = compToVal[id];

//         return sumBefore + need * val;
//     }

//     int size() const { return totalCount; }
//     long long sumAll() const { return totalSum; }
//     // Number of elements with value <= x. O(log N).
//     long long countLTEX(int x) const {
//         int lo = 1, hi = n, id = 0;
//         while (lo <= hi) {
//             int mid = (lo + hi) / 2;
//             if (compToVal[mid] <= x) {
//                 id = mid;
//                 lo = mid + 1;
//             } else {
//                 hi = mid - 1;
//             }
//         }
//         if (id == 0) return 0;
//         return _sum(bitCnt, id);
//     }

//     // Number of elements with value < x. O(log N).
//     long long countLTX(int x) const {
//         return countLTEX(x - 1);
//     }

//     // Number of elements with value >= x. O(log N).
//     long long countGTEX(int x) const {
//         return totalCount - countLTX(x);
//     }

//     // Number of elements with value > x. O(log N).
//     long long countGTX(int x) const {
//         return totalCount - countLTEX(x);
//     }

//     // Number of elements with value in [lo, hi]. O(log N).
//     long long countInRange(int lo, int hi) const {
//         if (lo > hi) return 0;
//         return countLTEX(hi) - countLTX(lo);
//     }
// };

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n; cin >> n;
//     vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
//     vector<int> rem(n); for (int i = 0; i < n; i++) cin >> rem[i];
//     for (int i = 0; i < n; i++) rem[i]--;
//     vector<int> positions(n);
//     for (int i = 0; i < n; i++) positions[i] = i;
//     OrderStatisticFenwick os(positions);
//     for (int i = 0; i < n; i++) os.add(i);
//     for (auto i : rem) {
//         int idx = os.kth(i + 1);
//         cout << A[idx] << " ";
//         os.remove(idx);
//     }
// }