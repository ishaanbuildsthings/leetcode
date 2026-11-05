// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazySeg.complex.debug.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const bool DEBUG = true;  // print the tree after every operation
const bool TRACE = false;  // also print every node the recursion visits
const int PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED = 64;  // longer arrays only print the operation line, not the tree
ostream& debugAndTraceOutput = cout;  // where DEBUG and TRACE print: LeetCode shows cout, use cerr on judges that grade stdout

// e.g. long long, char, pair, struct, ...
using RawVal = char;

struct Node {
    // int cnt[26];  // how many of each letter
    // int len;
    // Node() {  // can make an empty constructor which runs every time a Node is made
    //     for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)
    // }
};

// We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
// or when pushed down from parents
struct Tag {
    // bool assign;  // every element becomes letter, if set
    // char letter;
    // int shift;  // then every letter moves this many places on, z wrapping to a (0..25; 0 = none)
};

// how a node prints in the debug output
string nodeStr(const Node& node) {
    // string res = "len=" + to_string(node.len) + " letters:";
    // for (int c = 0; c < 26; c++) if (node.cnt[c]) res += " " + string(1, char('a' + c)) + "=" + to_string(node.cnt[c]);
    // return res;
    return "?";
}

// how a tag prints in the debug output
string tagStr(const Tag& tag) {
    // return "assign=" + to_string(tag.assign) + " letter=" + string(1, tag.letter) + " shift=" + to_string(tag.shift);
    return "?";
}

Node leaf(const RawVal& v, int i) {
    // Node res;
    // res.cnt[v - 'a'] = 1;
    // res.len = 1;
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];
    // res.len = left.len + right.len;
    // return res;
}

// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
Node apply(Node node, const Tag& tag) {
    // This is NOT mutating since node is taken by value in the arg, we can also just make a new node if needed
    // if (tag.assign) {
    //     for (int c = 0; c < 26; c++) node.cnt[c] = 0;
    //     node.cnt[tag.letter - 'a'] = node.len;
    // }
    // if (tag.shift) {
    //     rotate(node.cnt, node.cnt + 26 - tag.shift, node.cnt + 26);  // (letter c's count moves to c + shift)
    // }
    // return node;
}

// a tag that is the old tag, then the new tag
Tag compose(Tag old, const Tag& newer) {
    // This is NOT mutating since old is taken by value in the arg, we can also just make a new tag if needed
    // if (newer.assign) return newer;  // (a later assign wipes out everything before it)
    // old.shift = (old.shift + newer.shift) % 26;  // (shifts add up, still after old's assign if it had one)
    // return old;
}

struct LazySeg {
    int n;
    vector<Node> tree;
    vector<Tag> lazy;
    vector<char> tagged;  // tagged[nodeI]: lazy[nodeI] is pending for nodeI's children

    LazySeg(const vector<RawVal>& a) : n(a.size()) {
        tree.assign(4 * max(n, 1), Node());
        lazy.assign(4 * max(n, 1), Tag());
        tagged.assign(4 * max(n, 1), 0);
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

    // the tag reaches this node now, and is remembered for its children
    void _applyTag(int nodeI, int tl, int tr, const Tag& tag) {
        tree[nodeI] = apply(tree[nodeI], tag);
        if (tl < tr) {
            if (tagged[nodeI]) lazy[nodeI] = compose(lazy[nodeI], tag);
            else lazy[nodeI] = tag, tagged[nodeI] = 1;
        }
        _trace(nodeI, tl, tr, "applied tag " + tagStr(tag) + ": node is now " + nodeStr(tree[nodeI]));
    }

    void _pushDown(int nodeI, int tl, int tr) {
        if (!tagged[nodeI]) return;
        _trace(nodeI, tl, tr, "pushing tag " + tagStr(lazy[nodeI]) + " down");
        int tm = (tl + tr) / 2;
        Tag tag = lazy[nodeI];
        _applyTag(2 * nodeI, tl, tm, tag);
        _applyTag(2 * nodeI + 1, tm + 1, tr, tag);
        tagged[nodeI] = 0;
    }

    void _trace(int nodeI, int tl, int tr, const string& what) {
        if (TRACE) debugAndTraceOutput << string(4 * __lg(nodeI), ' ') << "[" << tl << "," << tr << "] " << what << "\n";
    }

    void _show(const string& op) {
        if (!DEBUG) return;
        debugAndTraceOutput << "---- " << op << " ----\n";
        if (n > 0 && n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED) {
            _showNode(1, 0, n - 1, 0);
            vector<Tag> above;
            debugAndTraceOutput << "each element, pending tags included:";
            _actual(1, 0, n - 1, above);
            debugAndTraceOutput << "\n";
        }
        debugAndTraceOutput << "\n";
    }

    void _showNode(int nodeI, int tl, int tr, int depth) {
        debugAndTraceOutput << string(4 * depth, ' ') << "[" << tl << "," << tr << "] " << nodeStr(tree[nodeI]);
        if (tl < tr && tagged[nodeI]) debugAndTraceOutput << "  pending for children: " << tagStr(lazy[nodeI]);
        debugAndTraceOutput << "\n";
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        _showNode(2 * nodeI, tl, tm, depth + 1);
        _showNode(2 * nodeI + 1, tm + 1, tr, depth + 1);
    }

    // what each element really is, without pushing anything: above is every tag waiting over this node, oldest last
    void _actual(int nodeI, int tl, int tr, vector<Tag>& above) {
        if (tl == tr) {
            Node node = tree[nodeI];
            for (int j = (int)above.size() - 1; j >= 0; j--) {
                const Tag& tag = above[j];
                node = apply(node, tag);
            }
            debugAndTraceOutput << "  " << nodeStr(node);
            return;
        }
        if (tagged[nodeI]) above.push_back(lazy[nodeI]);
        int tm = (tl + tr) / 2;
        _actual(2 * nodeI, tl, tm, above);
        _actual(2 * nodeI + 1, tm + 1, tr, above);
        if (tagged[nodeI]) above.pop_back();
    }

    Node _pointGet(int nodeI, int tl, int tr, int i) {
        _trace(nodeI, tl, tr, "pointGet: visiting");
        if (tl == tr) return tree[nodeI];
        _pushDown(nodeI, tl, tr);
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
        _pushDown(nodeI, tl, tr);
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
        _pushDown(nodeI, tl, tr);
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

    void _rangeUpdate(int nodeI, int tl, int tr, int l, int r, const Tag& tag) {
        if (r < tl || l > tr) return;
        if (l <= tl && tr <= r) {
            _trace(nodeI, tl, tr, "fully inside");
            _applyTag(nodeI, tl, tr, tag);
            return;
        }
        _pushDown(nodeI, tl, tr);
        int tm = (tl + tr) / 2;
        _rangeUpdate(2 * nodeI, tl, tm, l, r, tag);
        _rangeUpdate(2 * nodeI + 1, tm + 1, tr, l, r, tag);
        _pull(nodeI);
        _trace(nodeI, tl, tr, "pulled: " + nodeStr(tree[nodeI]));
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

    // tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    void rangeUpdate(int l, int r, const Tag& tag) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < n");
        _rangeUpdate(1, 0, n - 1, l, r, tag);
        _show("rangeUpdate(" + to_string(l) + ", " + to_string(r) + ", " + tagStr(tag) + ")");
    }
};
