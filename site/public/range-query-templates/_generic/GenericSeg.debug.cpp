// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSeg.debug.cpp
#include <bits/stdc++.h>
using namespace std;

const bool DEBUG = true;  // print the tree after every operation
const bool TRACE = false;  // also print every node the recursion visits
const int PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED = 64;  // longer arrays only print the operation line, not the tree
ostream& debugAndTraceOutput = cout;  // where DEBUG and TRACE print: LeetCode shows cout, use cerr on judges that grade stdout

// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mn;
};

// how a node prints in the debug output
string nodeStr(const Node& node) {
    // return "tot=" + to_string(node.tot) + " mn=" + to_string(node.mn);
    return "?";
}

Node leaf(const RawVal& v, int i) {
    // Node res;
    // res.tot = v, res.mn = v;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot;
    // res.mn = min(left.mn, right.mn);
    // return res;
}

struct Seg {
    int n;
    vector<Node> tree;

    Seg(const vector<RawVal>& a) : n(a.size()) {
        tree.assign(4 * max(n, 1), Node());
        if (n) _build(1, 0, n - 1, a);
        _show("build");
    }

    void _build(int nodeI, int tl, int tr, const vector<RawVal>& a) {
        if (tl == tr) {
            tree[nodeI] = leaf(a[tl], tl);
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, a);
        _build(2 * nodeI + 1, tm + 1, tr, a);
        _pull(nodeI);
    }

    void _pull(int nodeI) {
        tree[nodeI] = combine(tree[2 * nodeI], tree[2 * nodeI + 1]);
    }

    void _trace(int nodeI, int tl, int tr, const string& what) {
        if (TRACE) debugAndTraceOutput << string(4 * __lg(nodeI), ' ') << "[" << tl << "," << tr << "] " << what << "\n";
    }

    void _show(const string& op) {
        if (!DEBUG) return;
        debugAndTraceOutput << "---- " << op << " ----\n";
        if (n > 0 && n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED) {
            _showNode(1, 0, n - 1, 0);
        }
        debugAndTraceOutput << "\n";
    }

    void _showNode(int nodeI, int tl, int tr, int depth) {
        debugAndTraceOutput << string(4 * depth, ' ') << "[" << tl << "," << tr << "] " << nodeStr(tree[nodeI]);
        debugAndTraceOutput << "\n";
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        _showNode(2 * nodeI, tl, tm, depth + 1);
        _showNode(2 * nodeI + 1, tm + 1, tr, depth + 1);
    }

    Node _pointGet(int nodeI, int tl, int tr, int i) {
        _trace(nodeI, tl, tr, "pointGet: visiting");
        if (tl == tr) return tree[nodeI];
        int tm = (tl + tr) / 2;
        if (i <= tm) return _pointGet(2 * nodeI, tl, tm, i);
        return _pointGet(2 * nodeI + 1, tm + 1, tr, i);
    }

    void _pointAssign(int nodeI, int tl, int tr, int i, const RawVal& val) {
        _trace(nodeI, tl, tr, "pointAssign: visiting");
        if (tl == tr) {
            tree[nodeI] = leaf(val, i);
            _trace(nodeI, tl, tr, "leaf is now " + nodeStr(tree[nodeI]));
            return;
        }
        int tm = (tl + tr) / 2;
        if (i <= tm) _pointAssign(2 * nodeI, tl, tm, i, val);
        else _pointAssign(2 * nodeI + 1, tm + 1, tr, i, val);
        _pull(nodeI);
        _trace(nodeI, tl, tr, "pulled: " + nodeStr(tree[nodeI]));
    }

    Node _rangeQuery(int nodeI, int tl, int tr, int l, int r) {
        if (l <= tl && tr <= r) {
            _trace(nodeI, tl, tr, "fully inside: use " + nodeStr(tree[nodeI]));
            return tree[nodeI];
        }
        int tm = (tl + tr) / 2;
        if (r <= tm) {
            _trace(nodeI, tl, tr, "only the left child overlaps");
            return _rangeQuery(2 * nodeI, tl, tm, l, r);
        }
        if (l > tm) {
            _trace(nodeI, tl, tr, "only the right child overlaps");
            return _rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r);
        }
        _trace(nodeI, tl, tr, "splits into both children");
        Node leftResult = _rangeQuery(2 * nodeI, tl, tm, l, r);
        Node rightResult = _rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r);
        Node res = combine(leftResult, rightResult);
        _trace(nodeI, tl, tr, "combined " + nodeStr(leftResult) + " and " + nodeStr(rightResult) + " into " + nodeStr(res));
        return res;
    }

    // how many elements
    int size() { return n; }

    // the Node of a[i]; needs 0 <= i < n, else out_of_range
    Node pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        Node res = _pointGet(1, 0, n - 1, i);
        _show("pointGet(" + to_string(i) + ") -> " + nodeStr(res));
        return res;
    }

    // a[i] = val; needs 0 <= i < n, else out_of_range
    void pointAssign(int i, const RawVal& val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        _pointAssign(1, 0, n - 1, i, val);
        _show("pointAssign(" + to_string(i) + ") -> " + nodeStr(leaf(val, i)));
    }

    // the Node of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    Node rangeQuery(int l, int r) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeQuery: needs 0 <= l <= r < n");
        Node res = _rangeQuery(1, 0, n - 1, l, r);
        _show("rangeQuery(" + to_string(l) + ", " + to_string(r) + ") -> " + nodeStr(res));
        return res;
    }

    // the Node of the whole array; needs n >= 1, else out_of_range
    Node rangeQueryAll() {
        if (n == 0) throw out_of_range("rangeQueryAll: needs n >= 1");
        return tree[1];
    }
};
