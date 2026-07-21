// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   VersionedMaxSeg seg(1'000'000'000);              // values (slots) in [0, 1e9]
//   seg.chmax(value, score);                         // raise current[value] to max(old, score)
//   int versionId = seg.snapshot();                  // freeze -> version id
//   long long m = seg.queryVersionMax(versionId, low, high);  // max over [low, high] of that version
//   long long c = seg.queryCurrentMax(low, high);    // same, on the live tree
//
// Persistent max segment tree over values [0, maxVal]. chmax raises a
// slot; snapshot() freezes the live tree and returns a versionId
// (0, 1, 2, ... in call order); any past version stays queryable.
// Sparse: an update touches only O(log maxVal) nodes, so maxVal can be
// ~1e9 with raw values -- you pay log(maxVal) per op, so compress when
// you can enumerate the values up front.
//
// An unset slot reads as NEG, so a query over a range with nothing set
// returns NEG (e.g. a tree over 0..1e9 queried on 1e5..1e6 with nothing
// set there returns NEG). queryCurrent/queryVersion also return NEG when
// low > high.

#include <bits/stdc++.h>
using namespace std;

class VersionedMaxSeg {
public:
    static constexpr long long NEG = LLONG_MIN;

    // O(1)
    VersionedMaxSeg(int maxVal) : maxVal(maxVal) {
        left.push_back(0);          // node 0 = blank sentinel
        right.push_back(0);
        best.push_back(NEG);
        cur = 0;                    // root of the live (unfrozen) tree
        versions.push_back(0);      // versions[versionId] -> frozen root; id 0 = blank
    }

    // O(log maxVal) -- raises current[value] to max(old, score)
    void chmax(int value, long long score) {
        cur = _chmax(cur, 0, maxVal, value, score);
    }

    // O(1) -- freezes the live tree, returns its versionId
    int snapshot() {
        versions.push_back(cur);
        return (int)versions.size() - 1;
    }

    // O(log maxVal) -- max score over values [low, high] in the live tree.
    // NEG if low > high or nothing set in range.
    long long queryCurrentMax(int low, int high) {
        if (low > high) return NEG;
        return _query(cur, 0, maxVal, low, high);
    }

    // O(log maxVal) -- max score over values [low, high] in frozen version.
    // NEG if low > high or nothing set in range.
    long long queryVersionMax(int versionId, int low, int high) {
        if (low > high) return NEG;
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
    int _chmax(int node, int nodeLow, int nodeHigh, int value, long long score) {
        if (nodeLow == nodeHigh) {
            long long cur2 = best[node];
            return _new(0, 0, cur2 >= score ? cur2 : score);
        }
        int mid = (nodeLow + nodeHigh) >> 1;
        int lc = left[node], rc = right[node];
        if (value <= mid) lc = _chmax(lc, nodeLow, mid, value, score);
        else              rc = _chmax(rc, mid + 1, nodeHigh, value, score);
        return _new(lc, rc, max(best[lc], best[rc]));
    }

    // O(log maxVal)
    long long _query(int node, int nodeLow, int nodeHigh, int low, int high) {
        if (node == 0 || nodeHigh < low || high < nodeLow)
            return NEG;
        if (low <= nodeLow && nodeHigh <= high)
            return best[node];
        int mid = (nodeLow + nodeHigh) >> 1;
        return max(_query(left[node], nodeLow, mid, low, high),
                   _query(right[node], mid + 1, nodeHigh, low, high));
    }
};