// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   VersionedMinSeg seg(1'000'000'000);                       // values (slots) in [0, 1e9]
//   seg.chmin(value, score);                                  // lower current[value] to min(old, score)
//   int versionId = seg.snapshot();                           // freeze -> version id
//   long long m = seg.queryVersionMin(versionId, low, high);  // min over [low, high] of that version
//   long long c = seg.queryCurrentMin(low, high);             // same, on the live tree
//
// Persistent min segment tree over values [0, maxVal]. chmin lowers a
// slot; snapshot() freezes the live tree and returns a versionId
// (0, 1, 2, ... in call order); any past version stays queryable.
// Sparse: an update touches only O(log maxVal) nodes, so maxVal can be
// ~1e9 with raw values -- you pay log(maxVal) per op, so compress when
// you can enumerate the values up front.
//
// An unset slot reads as INF, so a query over a range with nothing set
// returns INF (a tree over 0..1e9 queried on 1e5..1e6 with nothing set
// there returns INF). queryCurrent/queryVersion also return INF when
// low > high.

#include <bits/stdc++.h>
using namespace std;

class VersionedMinSeg {
public:
    static constexpr long long INF = LLONG_MAX;

    // O(1)
    VersionedMinSeg(int maxVal) : maxVal(maxVal) {
        left.push_back(0);          // node 0 = blank sentinel
        right.push_back(0);
        best.push_back(INF);
        cur = 0;                    // root of the live (unfrozen) tree
        versions.push_back(0);      // versions[versionId] -> frozen root; id 0 = blank
    }

    // O(log maxVal) -- lowers current[value] to min(old, score)
    void chmin(int value, long long score) {
        cur = _chmin(cur, 0, maxVal, value, score);
    }

    // O(1) -- freezes the live tree, returns its versionId
    int snapshot() {
        versions.push_back(cur);
        return (int)versions.size() - 1;
    }

    // O(log maxVal) -- min score over values [low, high] in the live tree.
    // INF if low > high or nothing set in range.
    long long queryCurrentMin(int low, int high) {
        if (low > high) return INF;
        return _query(cur, 0, maxVal, low, high);
    }

    // O(log maxVal) -- min score over values [low, high] in a frozen version.
    // INF if low > high or nothing set in range.
    long long queryVersionMin(int versionId, int low, int high) {
        if (low > high) return INF;
        return _query(versions[versionId], 0, maxVal, low, high);
    }

private:
    int maxVal;
    vector<int> left, right;
    vector<long long> best;
    int cur;
    vector<int> versions;

    // allocate a fresh node, return its index (this is what makes it persistent)
    int _new(int l, int r, long long b) {
        left.push_back(l);
        right.push_back(r);
        best.push_back(b);
        return (int)best.size() - 1;
    }

    // O(log maxVal) -- rebuilds only the root->value path, reuses the rest
    int _chmin(int node, int nodeLow, int nodeHigh, int value, long long score) {
        if (nodeLow == nodeHigh) {
            long long old = best[node];
            return _new(0, 0, old <= score ? old : score);
        }
        int mid = (nodeLow + nodeHigh) >> 1;
        int lc = left[node], rc = right[node];
        if (value <= mid) lc = _chmin(lc, nodeLow, mid, value, score);
        else              rc = _chmin(rc, mid + 1, nodeHigh, value, score);
        return _new(lc, rc, min(best[lc], best[rc]));
    }

    // O(log maxVal)
    long long _query(int node, int nodeLow, int nodeHigh, int low, int high) {
        if (node == 0 || nodeHigh < low || high < nodeLow)
            return INF;
        if (low <= nodeLow && nodeHigh <= high)
            return best[node];
        int mid = (nodeLow + nodeHigh) >> 1;
        return min(_query(left[node], nodeLow, mid, low, high),
                   _query(right[node], mid + 1, nodeHigh, low, high));
    }
};