"""Debug versions of the generic seg trees (templates/ultimate-template-tool/generic-seg-trees/): picked on the site with a checkbox, on
top of the language and the example level.

    Generic<Name>.debug.py, Generic<Name>.debug.cpp, Generic<Name>.simple.debug.cpp, Generic<Name>.complex.debug.cpp

The functions you fill in are the normal file's, unchanged, plus (C++ only) how to print a node and a tag. The tree is
written recursively, and prints itself after every operation. Edit this script, never the generated files.

    python3 gen_generic_debug.py
"""

import os
import re

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "generic-seg-trees")

PY_HEAD = """DEBUG = True  # print the tree after every operation
TRACE = False  # also print every node the recursion visits
PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED = 64  # longer arrays only print the operation line, not the tree


"""

CPP_HEAD = """const bool DEBUG = true;  // print the tree after every operation
const bool TRACE = false;  // also print every node the recursion visits
const int PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED = 64;  // longer arrays only print the operation line, not the tree
ostream& debugAndTraceOutput = cout;  // where DEBUG and TRACE print: LeetCode shows cout, use cerr on judges that grade stdout

"""

PY_SEG = '''class Seg:
    def __init__(self, a, leaf, combine):
        self.n = n = len(a)
        self.leaf, self.combine = leaf, combine
        self.tree = [None] * (4 * n)
        if n:
            self._build(1, 0, n - 1, a)
        self._show("build")

    def _build(self, nodeI, tl, tr, a):
        if tl == tr:
            self.tree[nodeI] = self.leaf(a[tl], tl)
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm, a)
        self._build(2 * nodeI + 1, tm + 1, tr, a)
        self._pull(nodeI)

    def _pull(self, nodeI):
        self.tree[nodeI] = self.combine(self.tree[2 * nodeI], self.tree[2 * nodeI + 1])

    def _trace(self, nodeI, tl, tr, what):
        if TRACE:
            print(f"{'    ' * (nodeI.bit_length() - 1)}[{tl},{tr}] {what}")

    def _show(self, op):
        if not DEBUG:
            return
        print(f"---- {op} ----")
        if 0 < self.n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED:
            self._showNode(1, 0, self.n - 1, 0)
        print()

    def _showNode(self, nodeI, tl, tr, depth):
        print(f"{'    ' * depth}[{tl},{tr}] {nodeStr(self.tree[nodeI])}")
        if tl < tr:
            tm = (tl + tr) // 2
            self._showNode(2 * nodeI, tl, tm, depth + 1)
            self._showNode(2 * nodeI + 1, tm + 1, tr, depth + 1)

    def _pointGet(self, nodeI, tl, tr, i):
        self._trace(nodeI, tl, tr, "pointGet: visiting")
        if tl == tr:
            return self.tree[nodeI]
        tm = (tl + tr) // 2
        if i <= tm:
            return self._pointGet(2 * nodeI, tl, tm, i)
        return self._pointGet(2 * nodeI + 1, tm + 1, tr, i)

    def _pointAssign(self, nodeI, tl, tr, i, val):
        self._trace(nodeI, tl, tr, "pointAssign: visiting")
        if tl == tr:
            self.tree[nodeI] = self.leaf(val, i)
            self._trace(nodeI, tl, tr, f"leaf is now {nodeStr(self.tree[nodeI])}")
            return
        tm = (tl + tr) // 2
        if i <= tm:
            self._pointAssign(2 * nodeI, tl, tm, i, val)
        else:
            self._pointAssign(2 * nodeI + 1, tm + 1, tr, i, val)
        self._pull(nodeI)
        self._trace(nodeI, tl, tr, f"pulled: {nodeStr(self.tree[nodeI])}")

    def _rangeQuery(self, nodeI, tl, tr, l, r):
        if l <= tl and tr <= r:
            self._trace(nodeI, tl, tr, f"fully inside: use {nodeStr(self.tree[nodeI])}")
            return self.tree[nodeI]
        tm = (tl + tr) // 2
        if r <= tm:
            self._trace(nodeI, tl, tr, "only the left child overlaps")
            return self._rangeQuery(2 * nodeI, tl, tm, l, r)
        if l > tm:
            self._trace(nodeI, tl, tr, "only the right child overlaps")
            return self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        self._trace(nodeI, tl, tr, "splits into both children")
        leftResult = self._rangeQuery(2 * nodeI, tl, tm, l, r)
        rightResult = self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        res = self.combine(leftResult, rightResult)
        self._trace(nodeI, tl, tr, f"combined {nodeStr(leftResult)} and {nodeStr(rightResult)} into {nodeStr(res)}")
        return res

    # how many elements
    def size(self):
        return self.n

    # the node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        res = self._pointGet(1, 0, self.n - 1, i)
        self._show(f"pointGet({i}) -> {nodeStr(res)}")
        return res

    # a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError("pointAssign: needs 0 <= i < n")
        self._pointAssign(1, 0, self.n - 1, i, val)
        self._show(f"pointAssign({i}, {val})")

    # the node of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
        res = self._rangeQuery(1, 0, self.n - 1, l, r)
        self._show(f"rangeQuery({l}, {r}) -> {nodeStr(res)}")
        return res

    # the node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.tree[1]
'''

PY_LAZY = '''class LazySeg:
    _NO_TAG = object()  # a pending-tag slot with nothing pending (so any tag value works, None too)

    def __init__(self, a, leaf, combine, apply, compose):
        self.n = n = len(a)
        self.leaf, self.combine, self.apply, self.compose = leaf, combine, apply, compose
        self.tree = [None] * (4 * n)
        self.lazy = [LazySeg._NO_TAG] * (4 * n)  # lazy[nodeI]: the tag pending for nodeI's children
        if n:
            self._build(1, 0, n - 1, a)
        self._show("build")

    def _build(self, nodeI, tl, tr, a):
        if tl == tr:
            self.tree[nodeI] = self.leaf(a[tl], tl)
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm, a)
        self._build(2 * nodeI + 1, tm + 1, tr, a)
        self._pull(nodeI)

    def _pull(self, nodeI):
        self.tree[nodeI] = self.combine(self.tree[2 * nodeI], self.tree[2 * nodeI + 1])

    # the tag reaches this node now, and is remembered for its children
    def _applyTag(self, nodeI, tl, tr, tag):
        self.tree[nodeI] = self.apply(self.tree[nodeI], tag)
        if tl < tr:
            old = self.lazy[nodeI]
            self.lazy[nodeI] = tag if old is LazySeg._NO_TAG else self.compose(old, tag)
        self._trace(nodeI, tl, tr, f"applied tag {tagStr(tag)}: node is now {nodeStr(self.tree[nodeI])}")

    def _pushDown(self, nodeI, tl, tr):
        tag = self.lazy[nodeI]
        if tag is LazySeg._NO_TAG:
            return
        self._trace(nodeI, tl, tr, f"pushing tag {tagStr(tag)} down")
        tm = (tl + tr) // 2
        self._applyTag(2 * nodeI, tl, tm, tag)
        self._applyTag(2 * nodeI + 1, tm + 1, tr, tag)
        self.lazy[nodeI] = LazySeg._NO_TAG

    def _trace(self, nodeI, tl, tr, what):
        if TRACE:
            print(f"{'    ' * (nodeI.bit_length() - 1)}[{tl},{tr}] {what}")

    def _show(self, op):
        if not DEBUG:
            return
        print(f"---- {op} ----")
        if 0 < self.n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED:
            self._showNode(1, 0, self.n - 1, 0)
            actual = [nodeStr(node) for node in self._actual(1, 0, self.n - 1, [])]
            print(f"each element, pending tags included: {actual}")
        print()

    def _showNode(self, nodeI, tl, tr, depth):
        tag = self.lazy[nodeI]
        pending = "" if tag is LazySeg._NO_TAG else f"  pending for children: {tagStr(tag)}"
        print(f"{'    ' * depth}[{tl},{tr}] {nodeStr(self.tree[nodeI])}{pending}")
        if tl < tr:
            tm = (tl + tr) // 2
            self._showNode(2 * nodeI, tl, tm, depth + 1)
            self._showNode(2 * nodeI + 1, tm + 1, tr, depth + 1)

    # what each element really is, without pushing anything: tags is every tag waiting above this node, oldest last
    def _actual(self, nodeI, tl, tr, tags):
        if tl == tr:
            node = self.tree[nodeI]
            for tag in reversed(tags):
                node = self.apply(node, tag)
            return [node]
        pending = self.lazy[nodeI]
        below = tags if pending is LazySeg._NO_TAG else tags + [pending]
        tm = (tl + tr) // 2
        return self._actual(2 * nodeI, tl, tm, below) + self._actual(2 * nodeI + 1, tm + 1, tr, below)

    def _pointGet(self, nodeI, tl, tr, i):
        self._trace(nodeI, tl, tr, "pointGet: visiting")
        if tl == tr:
            return self.tree[nodeI]
        self._pushDown(nodeI, tl, tr)
        tm = (tl + tr) // 2
        if i <= tm:
            return self._pointGet(2 * nodeI, tl, tm, i)
        return self._pointGet(2 * nodeI + 1, tm + 1, tr, i)

    def _pointAssign(self, nodeI, tl, tr, i, val):
        self._trace(nodeI, tl, tr, "pointAssign: visiting")
        if tl == tr:
            self.tree[nodeI] = self.leaf(val, i)
            self._trace(nodeI, tl, tr, f"leaf is now {nodeStr(self.tree[nodeI])}")
            return
        self._pushDown(nodeI, tl, tr)
        tm = (tl + tr) // 2
        if i <= tm:
            self._pointAssign(2 * nodeI, tl, tm, i, val)
        else:
            self._pointAssign(2 * nodeI + 1, tm + 1, tr, i, val)
        self._pull(nodeI)
        self._trace(nodeI, tl, tr, f"pulled: {nodeStr(self.tree[nodeI])}")

    def _rangeQuery(self, nodeI, tl, tr, l, r):
        if l <= tl and tr <= r:
            self._trace(nodeI, tl, tr, f"fully inside: use {nodeStr(self.tree[nodeI])}")
            return self.tree[nodeI]
        self._pushDown(nodeI, tl, tr)
        tm = (tl + tr) // 2
        if r <= tm:
            self._trace(nodeI, tl, tr, "only the left child overlaps")
            return self._rangeQuery(2 * nodeI, tl, tm, l, r)
        if l > tm:
            self._trace(nodeI, tl, tr, "only the right child overlaps")
            return self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        self._trace(nodeI, tl, tr, "splits into both children")
        leftResult = self._rangeQuery(2 * nodeI, tl, tm, l, r)
        rightResult = self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        res = self.combine(leftResult, rightResult)
        self._trace(nodeI, tl, tr, f"combined {nodeStr(leftResult)} and {nodeStr(rightResult)} into {nodeStr(res)}")
        return res

    def _rangeUpdate(self, nodeI, tl, tr, l, r, tag):
        if r < tl or l > tr:
            return
        if l <= tl and tr <= r:
            self._trace(nodeI, tl, tr, "fully inside")
            self._applyTag(nodeI, tl, tr, tag)
            return
        self._pushDown(nodeI, tl, tr)
        tm = (tl + tr) // 2
        self._rangeUpdate(2 * nodeI, tl, tm, l, r, tag)
        self._rangeUpdate(2 * nodeI + 1, tm + 1, tr, l, r, tag)
        self._pull(nodeI)
        self._trace(nodeI, tl, tr, f"pulled: {nodeStr(self.tree[nodeI])}")

    # how many elements
    def size(self):
        return self.n

    # the node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        res = self._pointGet(1, 0, self.n - 1, i)
        self._show(f"pointGet({i}) -> {nodeStr(res)}")
        return res

    # a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError("pointAssign: needs 0 <= i < n")
        self._pointAssign(1, 0, self.n - 1, i, val)
        self._show(f"pointAssign({i}, {val})")

    # the node of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
        res = self._rangeQuery(1, 0, self.n - 1, l, r)
        self._show(f"rangeQuery({l}, {r}) -> {nodeStr(res)}")
        return res

    # the node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.tree[1]

    # tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeUpdate(self, l, r, tag):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeUpdate: needs 0 <= l <= r < n")
        self._rangeUpdate(1, 0, self.n - 1, l, r, tag)
        self._show(f"rangeUpdate({l}, {r}, {tagStr(tag)})")
'''


def cpp_tree(lazy):
    """The recursive tree, in C++: the Python one above, method for method."""
    name = "LazySeg" if lazy else "Seg"
    fields = """    int n;
    vector<Node> tree;
""" + ("""    vector<Tag> lazy;
    vector<char> tagged;  // tagged[nodeI]: lazy[nodeI] is pending for nodeI's children
""" if lazy else "")
    ctor = f"""    {name}(const vector<RawVal>& a) : n(a.size()) {{
        tree.assign(4 * max(n, 1), Node());
""" + ("""        lazy.assign(4 * max(n, 1), Tag());
        tagged.assign(4 * max(n, 1), 0);
""" if lazy else "") + """        if (n) _build(1, 0, n - 1, a);
        _show("build");
    }
"""
    tags = """    // the tag reaches this node now, and is remembered for its children
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

""" if lazy else ""
    show = """    void _show(const string& op) {
        if (!DEBUG) return;
        debugAndTraceOutput << "---- " << op << " ----\\n";
        if (n > 0 && n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED) {
            _showNode(1, 0, n - 1, 0);
""" + ("""            vector<Tag> above;
            debugAndTraceOutput << "each element, pending tags included:";
            _actual(1, 0, n - 1, above);
            debugAndTraceOutput << "\\n";
""" if lazy else "") + """        }
        debugAndTraceOutput << "\\n";
    }

    void _showNode(int nodeI, int tl, int tr, int depth) {
        debugAndTraceOutput << string(4 * depth, ' ') << "[" << tl << "," << tr << "] " << nodeStr(tree[nodeI]);
""" + ("""        if (tl < tr && tagged[nodeI]) debugAndTraceOutput << "  pending for children: " << tagStr(lazy[nodeI]);
""" if lazy else "") + """        debugAndTraceOutput << "\\n";
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        _showNode(2 * nodeI, tl, tm, depth + 1);
        _showNode(2 * nodeI + 1, tm + 1, tr, depth + 1);
    }

""" + ("""    // what each element really is, without pushing anything: above is every tag waiting over this node, oldest last
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

""" if lazy else "")
    push = "        _pushDown(nodeI, tl, tr);\n" if lazy else ""
    body = """    void _build(int nodeI, int tl, int tr, const vector<RawVal>& a) {
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

""" + tags + """    void _trace(int nodeI, int tl, int tr, const string& what) {
        if (TRACE) debugAndTraceOutput << string(4 * __lg(nodeI), ' ') << "[" << tl << "," << tr << "] " << what << "\\n";
    }

""" + show + """    Node _pointGet(int nodeI, int tl, int tr, int i) {
        _trace(nodeI, tl, tr, "pointGet: visiting");
        if (tl == tr) return tree[nodeI];
""" + push + """        int tm = (tl + tr) / 2;
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
""" + push + """        int tm = (tl + tr) / 2;
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
""" + push + """        int tm = (tl + tr) / 2;
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

""" + ("""    void _rangeUpdate(int nodeI, int tl, int tr, int l, int r, const Tag& tag) {
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

""" if lazy else "")
    public = """    // how many elements
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
""" + ("""
    // tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else out_of_range
    void rangeUpdate(int l, int r, const Tag& tag) {
        if (l < 0 || r >= n || l > r) throw out_of_range("rangeUpdate: needs 0 <= l <= r < n");
        _rangeUpdate(1, 0, n - 1, l, r, tag);
        _show("rangeUpdate(" + to_string(l) + ", " + to_string(r) + ", " + tagStr(tag) + ")");
    }
""" if lazy else "")
    return f"struct {name} {{\n{fields}\n{ctor}\n{body}{public}}};\n"


# how to print a node / a tag, per example level (the commented lines show what to fill in, like the other stubs)
STR_STUBS = {
    "simple": ('    return to_string(node);\n', '    return to_string(tag);\n'),
    "": ('    // return "tot=" + to_string(node.tot) + " mn=" + to_string(node.mn);\n    return "?";\n',
         '    // return "add=" + to_string(tag.add);\n    return "?";\n'),
    "complex": ('    // string res = "len=" + to_string(node.len) + " letters:";\n'
                '    // for (int c = 0; c < 26; c++) if (node.cnt[c]) res += " " + string(1, char(\'a\' + c)) + "=" + to_string(node.cnt[c]);\n'
                '    // return res;\n    return "?";\n',
                '    // return "assign=" + to_string(tag.assign) + " letter=" + string(1, tag.letter) + " shift=" + to_string(tag.shift);\n    return "?";\n'),
}


def str_stubs(level, lazy):
    node, tag = STR_STUBS[level]
    if level == "complex" and not lazy:  # (the plain tree's example has no len field)
        node = node.replace('"len=" + to_string(node.len) + " letters:"', '"letters:"')
    out = "// how a node prints in the debug output\nstring nodeStr(const Node& node) {\n" + node + "}\n\n"
    if lazy:
        out += "// how a tag prints in the debug output\nstring tagStr(const Tag& tag) {\n" + tag + "}\n\n"
    return out


def main():
    n = 0
    for stem, marker in (("GenericSeg", "Seg"), ("GenericLazySeg", "LazySeg")):
        lazy = "Lazy" in stem
        text = open(os.path.join(DIR, stem + ".py")).read()
        a = text.index(f"class {marker}:")
        head = text[:a].replace(f"generic/{stem}.py", f"generic/{stem}.debug.py")
        top = head.index("# e.g.")
        first = head.index("def leaf(")
        strs = ('# how a node prints in the debug output\ndef nodeStr(node: Node) -> str:\n    # return f"tot={node[0]} mn={node[1]}"\n    return str(node)\n\n\n' +
                ('# how a tag prints in the debug output\ndef tagStr(tag: Tag) -> str:\n    # return f"add={tag}"\n    return str(tag)\n\n\n' if lazy else ""))
        head = head[:first] + strs + head[first:]
        open(os.path.join(DIR, stem + ".debug.py"), "w").write(head[:top] + PY_HEAD.rstrip("\n") + "\n\n" + head[top:] + (PY_LAZY if lazy else PY_SEG))
        n += 1
        for level, dot in (("", ""), ("simple", ".simple"), ("complex", ".complex")):
            text = open(os.path.join(DIR, f"{stem}{dot}.cpp")).read()
            a = text.index(f"struct {marker} {{")
            head = text[:a].replace(f"generic/{stem}{dot}.cpp", f"generic/{stem}{dot}.debug.cpp")
            last = "using ll = long long;\n"
            top = head.index(last) + len(last)
            first = head.index("Node leaf(")
            full = head[:top] + "\n" + CPP_HEAD.rstrip("\n") + "\n" + head[top:first] + str_stubs(level, lazy) + head[first:] + cpp_tree(lazy)
            open(os.path.join(DIR, f"{stem}{dot}.debug.cpp"), "w").write(full)
            n += 1
    print("wrote", n, "files")


if __name__ == "__main__":
    main()
