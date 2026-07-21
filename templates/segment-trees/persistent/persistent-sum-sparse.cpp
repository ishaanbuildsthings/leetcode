// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   VersionedSumSeg seg(1'000'000'000);                       // values (slots) in [0, 1e9]
//   seg.add(value, weight);                                   // current[value] += weight
//   int versionId = seg.snapshot();                           // freeze -> version id
//   long long s = seg.queryVersionSum(versionId, low, high);  // sum over [low, high], one version
//   long long d = seg.rangeSumDiff(vHi, vLo, low, high);      // sum over (vLo, vHi] items only
//
// Persistent sum segment tree over values [0, maxVal]. add() increments
// a slot; snapshot() freezes the live tree and returns a versionId
// (0, 1, 2, ... in call order); any past version stays queryable.
// Sparse: an update touches only O(log maxVal) nodes, so maxVal can be
// ~1e9 with raw values -- you pay log(maxVal) per op, so compress when
// you can enumerate the values up front.
//
// Unlike max/min, sum has an inverse, so two versions can be DIFFED:
// rangeSumDiff(vHi, vLo, low, high) gives the sum over values [low, high]
// among items inserted between version vLo and vHi. That is the classic
// persistent-segtree trick (count-in-range, kth-smallest). Max/min can't
// do this -- no inverse to subtract.
//
// An unset slot is 0, so a query over a range with nothing set returns 0.

#include <bits/stdc++.h>
using namespace std;

class VersionedSumSeg {
public:
    // O(1)
    VersionedSumSeg(int maxVal) : maxVal(maxVal) {
        left.push_back(0);          // node 0 = blank sentinel, sum 0
        right.push_back(0);
        total.push_back(0);
        cur = 0;                    // root of the live (unfrozen) tree
        versions.push_back(0);      // versions[versionId] -> frozen root; id 0 = blank
    }

    // O(log maxVal) -- current[value] += weight
    void add(int value, long long weight) {
        cur = _add(cur, 0, maxVal, value, weight);
    }

    // O(1) -- freezes the live tree, returns its versionId
    int snapshot() {
        versions.push_back(cur);
        return (int)versions.size() - 1;
    }

    // O(log maxVal) -- sum over values [low, high] in the live tree.
    // 0 if low > high or nothing set in range.
    long long queryCurrentSum(int low, int high) {
        if (low > high) return 0;
        return _query(cur, 0, maxVal, low, high);
    }

    // O(log maxVal) -- sum over values [low, high] in a frozen version.
    // 0 if low > high or nothing set in range.
    long long queryVersionSum(int versionId, int low, int high) {
        if (low > high) return 0;
        return _query(versions[versionId], 0, maxVal, low, high);
    }

    // O(log maxVal) -- sum over values [low, high] among items inserted in (vLo, vHi].
    // Requires vLo be an EARLIER version than vHi (vLo's items are a subset).
    // This is the inverse-only capability max/min lack. 0 if low > high.
    long long rangeSumDiff(int vHi, int vLo, int low, int high) {
        if (low > high) return 0;
        return _queryDiff(versions[vHi], versions[vLo], 0, maxVal, low, high);
    }

private:
    int maxVal;
    vector<int> left, right;
    vector<long long> total;
    int cur;
    vector<int> versions;

    // allocate a fresh node, return its index (this is what makes it persistent)
    int _new(int l, int r, long long t) {
        left.push_back(l);
        right.push_back(r);
        total.push_back(t);
        return (int)total.size() - 1;
    }

    // O(log maxVal) -- rebuilds only the root->value path, reuses the rest
    int _add(int node, int nodeLow, int nodeHigh, int value, long long weight) {
        if (nodeLow == nodeHigh)
            return _new(0, 0, total[node] + weight);
        int mid = (nodeLow + nodeHigh) >> 1;
        int lc = left[node], rc = right[node];
        if (value <= mid) lc = _add(lc, nodeLow, mid, value, weight);
        else              rc = _add(rc, mid + 1, nodeHigh, value, weight);
        return _new(lc, rc, total[lc] + total[rc]);
    }

    // O(log maxVal)
    long long _query(int node, int nodeLow, int nodeHigh, int low, int high) {
        if (node == 0 || nodeHigh < low || high < nodeLow)
            return 0;
        if (low <= nodeLow && nodeHigh <= high)
            return total[node];
        int mid = (nodeLow + nodeHigh) >> 1;
        return _query(left[node], nodeLow, mid, low, high) +
               _query(right[node], mid + 1, nodeHigh, low, high);
    }

    // O(log maxVal) -- descend both roots subtracting; the subtraction is what
    // recovers exactly the items in (vLo, vHi]. Only valid because sum inverts.
    long long _queryDiff(int hiNode, int loNode, int nodeLow, int nodeHigh, int low, int high) {
        if (nodeHigh < low || high < nodeLow)
            return 0;
        if (low <= nodeLow && nodeHigh <= high)
            return total[hiNode] - total[loNode];
        int mid = (nodeLow + nodeHigh) >> 1;
        return _queryDiff(left[hiNode], left[loNode], nodeLow, mid, low, high) +
               _queryDiff(right[hiNode], right[loNode], mid + 1, nodeHigh, low, high);
    }
};