"""The C++ generic seg trees (templates/segment-trees/generic/*.cpp) in three example levels, picked on the site:

    simple   plain types, no structs: using Node = long long; (a max) and, lazy, using Tag = long long; (an add)
    basic    a struct with int fields (tot, mn, ...): the hand-written Generic*.cpp files themselves
    complex  a struct holding an array (how many of each letter), an empty constructor zeroing it, loops in combine

Only the part above the tree (RawVal, Node, Tag and the functions you fill in) changes; the tree is the hand-written
file's. Writes Generic<Name>.simple.cpp and Generic<Name>.complex.cpp next to each Generic<Name>.cpp, and for the
treaps a version without rangeReverse of each (.norev.cpp / .simple.norev.cpp / .complex.norev.cpp / .norev.py). Edit
the hand-written files or this script, never the generated ones.

    python3 gen_generic_examples.py
"""

import os
import re

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "segment-trees", "generic")

# file stem -> (the tree's first line, what kind of stubs it has)
FILES = {
    "GenericSeg": ("struct Seg {", "seg"),
    "GenericSparseTable": ("// A static array (no updates)", "sparse"),
    "GenericLazySeg": ("struct LazySeg {", "seg"),
    "GenericDynamicSeg": ("struct DynamicSeg {", "dyn"),
    "GenericLazyDynamicSeg": ("struct LazyDynamicSeg {", "dyn"),
    "GenericTreap": ("struct Treap {", "treap"),
    "GenericLazyTreap": ("struct LazyTreap {", "treap"),
    "GenericPersistentTreap": ("// Every op copies", "treap"),
    "GenericPersistentLazyTreap": ("// Every op copies", "treap"),
}

APPLY_DOC = """// return a new node: this node after tag is applied to it
// this function is never called with a tag that never existed, but tags can have things like pending false values or
// pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
// return original node)
"""
TAG_NOTE = ("// We never need to worry about initializing empty tags or anything, these tags come in via "
            "rangeUpdate(l, r, tag) calls\n// or when pushed down from parents\n")
BY_VALUE = "    // This is NOT mutating since {x} is taken by value in the arg, we can also just make a new {kind} if needed\n"


def leaf_sig(kind):
    return {"seg": "Node leaf(const RawVal& v, int i)", "sparse": "Node baseFn(const RawVal& v, int i)", "dyn": "Node leaf(const RawVal& v, long long i)",
            "treap": "Node leaf(const RawVal& v)"}[kind]


def simple(kind, lazy, rev=True):
    if kind == "treap" and rev:
        return simple_ends(lazy)
    out = ["// e.g. long long, char, ...\nusing RawVal = long long;\n\n",
           "// a plain type: here the max of the segment\nusing Node = long long;\n\n"]
    if lazy:
        out.append("// a pending update to every element of a segment: here add this much\n" + TAG_NOTE +
                   "using Tag = long long;\n\n")
    out.append(f"{leaf_sig(kind)} {{\n    // return v;\n}}\n\n")
    if kind == "sparse":
        out.append("// combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count)\n")
    out.append("Node combine(const Node& left, const Node& right) {\n    // return max(left, right);\n}\n\n")
    if kind == "dyn":
        out.append("// the Node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)\n"
                   "Node blank(long long lo, long long hi) {\n    // return 0;  // (the max of elements that are all 0)\n}\n\n")
    if kind == "treap" and rev:
        out.append("// node becomes the Node of its segment read backwards\n"
                   "Node reverse(Node node) {\n    // return node;  // (a max reads the same backwards)\n}\n\n")
    if lazy:
        out.append(APPLY_DOC + "Node apply(Node node, const Tag& tag) {\n"
                   "    // return node + tag;  // (adding to every element raises the max by as much)\n}\n\n")
        out.append("// a tag that is the old tag, then the new tag\n"
                   "Tag compose(Tag old, const Tag& newer) {\n    // return old + newer;\n}\n\n")
    return "".join(out)


def simple_ends(lazy):  # (a treap with rangeReverse: a node whose two ends trade places when it's read backwards)
    out = ["// e.g. long long, char, ...\nusing RawVal = long long;\n\n",
           "// a plain type: here the (first, last) values of the segment\nusing Node = pair<long long, long long>;\n\n"]
    if lazy:
        out.append("// a pending update to every element of a segment: here add this much\n" + TAG_NOTE +
                   "using Tag = long long;\n\n")
    out.append("Node leaf(const RawVal& v) {\n    // return {v, v};\n}\n\n")
    out.append("Node combine(const Node& left, const Node& right) {\n    // return {left.first, right.second};\n}\n\n")
    out.append("// node becomes the Node of its segment read backwards\n"
               "Node reverse(Node node) {\n    // return {node.second, node.first};  // (read backwards, the two ends trade places)\n}\n\n")
    if lazy:
        out.append(APPLY_DOC + "Node apply(Node node, const Tag& tag) {\n    // return {node.first + tag, node.second + tag};\n}\n\n")
        out.append("// a tag that is the old tag, then the new tag\n"
                   "Tag compose(Tag old, const Tag& newer) {\n    // return old + newer;\n}\n\n")
    return "".join(out)


def complex_sparse():
    return ("// e.g. long long, char, pair, struct, ...\nusing RawVal = char;\n\n"
            "struct Node {\n"
            "    // bool seen[26];  // which letters appear (a count wouldn't work: combine must be idempotent, see below)\n"
            "    // Node() {  // can make an empty constructor which runs every time a Node is made\n"
            "    //     for (int c = 0; c < 26; c++) seen[c] = false;\n"
            "    // }\n};\n\n"
            "Node baseFn(const RawVal& v, int i) {\n    // Node res;\n    // res.seen[v - 'a'] = true;\n    // return res;\n}\n\n"
            "// combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count)\n"
            "Node combine(const Node& left, const Node& right) {\n    // Node res;\n"
            "    // for (int c = 0; c < 26; c++) res.seen[c] = left.seen[c] || right.seen[c];\n    // return res;\n}\n\n")


def complex_(kind, lazy, rev=True):
    if kind == "sparse":
        return complex_sparse()
    big = kind == "dyn"  # (a dynamic tree's ranges can be ~1e18 long: counts and lengths in long long)
    num = "long long" if big else "int"
    ends = kind == "treap" and rev  # (read backwards, the end letters trade places)
    out = ["// e.g. long long, char, pair, struct, ...\nusing RawVal = char;\n\n", "struct Node {\n",
           f"    // {num} cnt[26];  // how many of each letter\n"]
    if ends:
        out.append("    // char first, last;  // the letters at the two ends\n")
    if lazy:
        out.append(f"    // {num} len;\n")
    out.append("    // Node() {  // can make an empty constructor which runs every time a Node is made\n"
               "    //     for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)\n"
               "    // }\n};\n\n")
    if lazy:
        out.append(TAG_NOTE + "struct Tag {\n"
                   "    // bool assign;  // every element becomes letter, if set\n"
                   "    // char letter;\n"
                   "    // int shift;  "
                   "// then every letter moves this many places on, z wrapping to a (0..25; 0 = none)\n"
                   "};\n\n")
    out.append(f"{leaf_sig(kind)} {{\n    // Node res;\n    // res.cnt[v - 'a'] = 1;\n" + ("    // res.first = res.last = v;\n" if ends else "") +
               ("    // res.len = 1;\n" if lazy else "") + "    // return res;\n}\n\n")
    out.append("Node combine(const Node& left, const Node& right) {\n    // Node res;\n"
               "    // for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];\n" +
               ("    // res.first = left.first, res.last = right.last;\n" if ends else "") +
               ("    // res.len = left.len + right.len;\n" if lazy else "") + "    // return res;\n}\n\n")
    if kind == "dyn":
        out.append("// the Node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)\n"
                   "Node blank(long long lo, long long hi) {\n    // Node res;  // (no letters: every count 0)\n" +
                   ("    // res.len = hi - lo + 1;\n" if lazy else "") + "    // return res;\n}\n\n")
    if ends:
        out.append("// node becomes the Node of its segment read backwards\n"
                   "Node reverse(Node node) {\n" + BY_VALUE.format(x="node", kind="node") +
                   "    // swap(node.first, node.last);  // (read backwards, the two ends trade places)\n    // return node;\n}\n\n")
    if lazy:
        out.append(APPLY_DOC + "Node apply(Node node, const Tag& tag) {\n" + BY_VALUE.format(x="node", kind="node") +
                   "    // if (tag.assign) {\n"
                   "    //     for (int c = 0; c < 26; c++) node.cnt[c] = 0;\n"
                   "    //     node.cnt[tag.letter - 'a'] = node.len;\n" +
                   ("    //     node.first = node.last = tag.letter;\n" if ends else "") +
                   "    // }\n"
                   "    // if (tag.shift) {\n"
                   "    //     rotate(node.cnt, node.cnt + 26 - tag.shift, node.cnt + 26);  "
                   "// (letter c's count moves to c + shift)\n" +
                   ("    //     node.first = 'a' + (node.first - 'a' + tag.shift) % 26;\n"
                    "    //     node.last = 'a' + (node.last - 'a' + tag.shift) % 26;\n" if ends else "") +
                   "    // }\n"
                   "    // return node;\n}\n\n")
        out.append("// a tag that is the old tag, then the new tag\n"
                   "Tag compose(Tag old, const Tag& newer) {\n" + BY_VALUE.format(x="old", kind="tag") +
                   "    // if (newer.assign) return newer;  // (a later assign wipes out everything before it)\n"
                   "    // old.shift = (old.shift + newer.shift) % 26;  "
                   "// (shifts add up, still after old's assign if it had one)\n"
                   "    // return old;\n}\n\n")
    return "".join(out)


def stubs_region(text, tree_start):
    a = text.index("// e.g. long long")
    b = text.index(tree_start)
    return a, b


# ------------------------------------------------------------------------------------------------ without rangeReverse
# Every treap also comes without rangeReverse (the site's default): no reverse stub, no reverse flag, no flip, and a
# push that only hands down tags. Generic<Name>.norev.cpp / .norev.py, and each C++ level's .norev too.

TREAPS = ["GenericTreap", "GenericLazyTreap", "GenericPersistentTreap", "GenericPersistentLazyTreap"]


def _rep(text, old, new, count=1):
    assert text.count(old) == count, (old[:90], text.count(old))
    return text.replace(old, new)


def drop_method(text, start, lang):
    """text without the method whose first line holds start (and the comment lines right above it)"""
    a = text.index(start)
    a = text.rindex("\n", 0, a) + 1
    mark = "//" if lang == "cpp" else "#"
    while True:
        prev = text.rindex("\n", 0, a - 1) + 1
        if text[prev:a - 1].strip().startswith(mark):
            a = prev
        else:
            break
    b = text.index("\n    }\n", a) + len("\n    }\n") if lang == "cpp" else text.index("\n\n", a) + 1
    if text[b:b + 1] == "\n":
        b += 1
    return text[:a] + text[b:]


PLAIN_CPP = """// e.g. long long, char, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mn;
LEN};
TAG
Node leaf(const RawVal& v) {
    // Node res;
    // res.tot = v, res.mn = v;LEAFLEN
    // return res;
}

Node combine(const Node& left, const Node& right) {
    // Node res;
    // res.tot = left.tot + right.tot;
    // res.mn = min(left.mn, right.mn);
COMBLEN    // return res;
}

"""
PLAIN_LAZY_REST = APPLY_DOC + """Node apply(Node node, const Tag& tag) {
""" + BY_VALUE.format(x="node", kind="node") + """    // node.tot += tag.add * node.len, node.mn += tag.add;
    // return node;
}

// a tag that is the old tag, then the new tag
Tag compose(Tag old, const Tag& newer) {
""" + BY_VALUE.format(x="old", kind="tag") + """    // old.add += newer.add;
    // return old;
}

"""


def plain_stubs(lazy):  # (a treap without rangeReverse: the tot / mn examples)
    text = PLAIN_CPP.replace("LEAFLEN", "").replace("COMBLEN", "    // res.len = left.len + right.len;\n" if lazy else "")
    text = text.replace("LEN", "    // int len;\n" if lazy else "").replace(
        "TAG", "\n// a pending update to every element of a segment\n" + TAG_NOTE +
        "struct Tag {\n    // long long add;\n};\n" if lazy else "")
    if lazy:
        text = text.replace("    // res.tot = v, res.mn = v;\n", "    // res.tot = v, res.mn = v, res.len = 1;\n")
    return text + (PLAIN_LAZY_REST if lazy else "")


def norev_cpp(text, stem):
    lazy, persistent = "Lazy" in stem, "Persistent" in stem
    a = text.index("// e.g. long long")
    b = text.index("// node becomes the Node of its segment read backwards\n")
    end = text.index("\n}\n\n", b) + len("\n}\n\n")
    tree = text.index("struct " + stem[len("Generic"):] + " {") if not persistent else text.index("// Every op copies")
    text = text[:a] + plain_stubs(lazy) + text[tree:]
    text = drop_method(text, "    static void flip(int t) {", "cpp")
    text = drop_method(text, "    void rangeReverse(", "cpp")
    if not persistent:
        if lazy:
            text = _rep(text, "        bool rev = false, tagged = false;\n", "        bool tagged = false;\n")
            text = _rep(text, "        if (nd[t].rev) flip(nd[t].L), flip(nd[t].R), nd[t].rev = false;\n", "")
        else:  # (push only handed down the flip: gone, with its calls)
            text = _rep(text, "        bool rev = false;\n", "")
            text = drop_method(text, "    static void push(int t) {", "cpp")
            text = re.sub(r"^\s*push\(\w+\);\n", "", text, flags=re.M)
        return text
    text = _rep(text, "        bool rev = false; // the children still need reversing (L / R and agg already are)\n", "")
    if lazy:
        a = text.index("    // hands t's pending flip and tag to copies of its children")
        b = text.index("\n    }\n", a) + len("\n    }\n")
        text = text[:a] + """    // hands t's pending tag to copies of its children (t is a copy no other tree sees)
    static void push(int t) {
        if (!nd[t].tagged) return;
        int l = nd[t].L, r = nd[t].R;
        Tag g = nd[t].lz;
        if (l) l = clone(l), applyTag(l, g);
        if (r) r = clone(r), applyTag(r, g);
        nd[t].L = l, nd[t].R = r, nd[t].tagged = false;
    }
""" + text[b:]
        a = text.index("    // the Node of items l..r of t, read with a flip")
        b = text.index("\n    }\n", a) + len("\n    }\n")
        text = text[:a] + """    // the Node of items l..r of t, read with a tag (g, or none) pending from above (makes no copies)
    static Node rq(int t, long long l, long long r, const Tag* g) {
        const Item& x = nd[t];
        if (l <= 0 && r >= x.sz - 1) return g ? apply(x.agg, *g) : x.agg;
        // the children's pending: x's own tag, then the one from above
        Tag both;
        const Tag* cg = g;
        if (x.tagged) cg = g ? &(both = compose(x.lz, *g)) : &x.lz;
        long long ls = nd[x.L].sz;
        Node res;
        bool has = false;
        if (l < ls) res = rq(x.L, l, min(r, ls - 1), cg), has = true;
        if (l <= ls && ls <= r) {
            Node self = g ? apply(x.self, *g) : x.self;
            res = has ? combine(res, self) : self, has = true;
        }
        if (r > ls) {
            Node s = rq(x.R, max(l - ls - 1, 0LL), r - ls - 1, cg);
            res = has ? combine(res, s) : s;
        }
        return res;
    }
""" + text[b:]
        text = text.replace("false, nullptr)", "nullptr)")
    else:
        text = drop_method(text, "    static void push(int t) {", "cpp")
        text = re.sub(r"^\s*push\(\w+\);\n", "", text, flags=re.M)
        a = text.index("    // the Node of items l..r of t, read with flipped pending")
        b = text.index("\n    }\n", a) + len("\n    }\n")
        text = text[:a] + """    // the Node of items l..r of t (makes no copies)
    static Node rq(int t, long long l, long long r) {
        const Item& x = nd[t];
        if (l <= 0 && r >= x.sz - 1) return x.agg;
        long long ls = nd[x.L].sz;
        Node res;
        bool has = false;
        if (l < ls) res = rq(x.L, l, min(r, ls - 1)), has = true;
        if (l <= ls && ls <= r) res = has ? combine(res, x.self) : x.self, has = true;
        if (r > ls) {
            Node s = rq(x.R, max(l - ls - 1, 0LL), r - ls - 1);
            res = has ? combine(res, s) : s;
        }
        return res;
    }
""" + text[b:]
        text = text.replace(", false)", ")")
    return text


PLAIN_PY = [("    # return (v, v, v)  # (tot, the best prefix sum, the best suffix sum)\n", "    # return (v, v)  # (tot, mn)\n"),
            ("    # return (left[0] + right[0], max(left[1], left[0] + right[1]), max(right[2], right[0] + left[2]))\n",
             "    # return (left[0] + right[0], min(left[1], right[1]))\n"),
            ("    # return (v, v, v, 1)  # (tot, the value at the left end, at the right end, len)\n", "    # return (v, v, 1)  # (tot, mn, len)\n"),
            ("    # return (left[0] + right[0], left[1], right[2], left[3] + right[3])\n",
             "    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])\n"),
            ("    # return (node[0] + tag * node[3], node[1] + tag, node[2] + tag, node[3])\n",
             "    # return (node[0] + tag * node[2], node[1] + tag, node[2])\n")]


def norev_py(text, stem):
    lazy, persistent = "Lazy" in stem, "Persistent" in stem
    cls = stem[len("Generic"):]
    for old, new in PLAIN_PY:
        text = text.replace(old, new)
    a = text.index("# the node of the same segment read backwards\n")
    text = text[:a] + text[text.index("\n\n\n", a) + len("\n\n\n"):]
    text = drop_method(text, "    def _flip(self, t):", "py")
    text = drop_method(text, "    def rangeReverse(", "py")
    text = _rep(text, "    # reverse is only needed for rangeReverse\n", "")
    text = text.replace(", reverse=lambda node: node):", "):")
    text = text.replace(", self.reverse = ", " = ").replace(", reverse\n", "\n")
    text = text.replace(", self.reverse)", ")")
    text = re.sub(r"(_self, _agg, _L, _R, _sz(?:, _pr)?), _rev((?:, _lz)?) = (\[None\], \[None\], \[0\], \[0\], \[0\](?:, \[0\])?), \[False\]",
                  r"\1\2 = \3", text)
    text = re.sub(r"^\s*(?:P|%s)\._rev\.append\([^\n]*\)\n" % cls, "", text, flags=re.M)
    if persistent:
        text = _rep(text, "    # rev[t]: t's children still need reversing (L / R and agg already are)\n" if not lazy else
                    "    # rev[t]: t's children still need reversing (L / R and agg already are); lz[t]: the tag pending for t's children\n",
                    "" if not lazy else "    # lz[t]: the tag pending for t's children\n")
    if not lazy:  # (push only handed down the flip: gone, with its calls)
        text = drop_method(text, "    def _push(self, t):", "py")
        text = re.sub(r"^\s*self\._push\(\w+\)\n", "", text, flags=re.M)
    elif not persistent:
        text = _rep(text, f"""        if {cls}._rev[t]:
            self._flip({cls}._L[t])
            self._flip({cls}._R[t])
            {cls}._rev[t] = False
""", "")
    else:
        a = text.index("    # hands t's pending flip and tag to copies of its children")
        b = text.index("\n\n", a) + 1
        text = text[:a] + f"""    # hands t's pending tag to copies of its children (t is a copy no other tree sees)
    def _push(self, t):
        P = {cls}
        tag = P._lz[t]
        if tag is P._NO_TAG:
            return
        for side in (P._L, P._R):
            if side[t]:
                c = self._clone(side[t])
                self._applyTag(c, tag)
                side[t] = c
        P._lz[t] = P._NO_TAG
""" + text[b:]
    if persistent:
        a = text.index("    # the node of items l..r of t, read with")
        b = text.index("\n\n", text.index("    def _rq(", a)) + 1
        if lazy:
            new = f"""    # the node of items l..r of t, read with a tag (g, or _NO_TAG) pending from above (makes no copies)
    def _rq(self, t, l, r, g):
        P = {cls}
        none = P._NO_TAG
        if l <= 0 and r >= P._sz[t] - 1:
            return P._agg[t] if g is none else self.apply(P._agg[t], g)
        # the children's pending: t's own tag, then the one from above
        own = P._lz[t]
        cg = g if own is none else own if g is none else self.compose(own, g)
        ls = P._sz[P._L[t]]
        res = None
        if l < ls:
            res = self._rq(P._L[t], l, min(r, ls - 1), cg)
        if l <= ls <= r:
            me = P._self[t] if g is none else self.apply(P._self[t], g)
            res = me if res is None else self.combine(res, me)
        if r > ls:
            s = self._rq(P._R[t], max(l - ls - 1, 0), r - ls - 1, cg)
            res = s if res is None else self.combine(res, s)
        return res
"""
        else:
            new = f"""    # the node of items l..r of t (makes no copies)
    def _rq(self, t, l, r):
        P = {cls}
        if l <= 0 and r >= P._sz[t] - 1:
            return P._agg[t]
        ls = P._sz[P._L[t]]
        res = None
        if l < ls:
            res = self._rq(P._L[t], l, min(r, ls - 1))
        if l <= ls <= r:
            res = P._self[t] if res is None else self.combine(res, P._self[t])
        if r > ls:
            s = self._rq(P._R[t], max(l - ls - 1, 0), r - ls - 1)
            res = s if res is None else self.combine(res, s)
        return res
"""
        text = text[:a] + new + text[b:]
        text = text.replace(", False, PersistentLazyTreap._NO_TAG)", ", PersistentLazyTreap._NO_TAG)").replace(", False)", ")")
    return text


def main():
    n = 0
    for stem, (tree_start, kind) in FILES.items():
        base = open(os.path.join(DIR, stem + ".cpp")).read()
        lazy = "Lazy" in stem
        bases = [("", base, True)]
        if stem in TREAPS:
            nr = norev_cpp(base, stem).replace(f"generic/{stem}.cpp", f"generic/{stem}.norev.cpp")
            bases.append((".norev", nr, False))
            open(os.path.join(DIR, stem + ".norev.cpp"), "w").write(nr)
            py = open(os.path.join(DIR, stem + ".py")).read()
            open(os.path.join(DIR, stem + ".norev.py"), "w").write(
                norev_py(py, stem).replace(f"generic/{stem}.py", f"generic/{stem}.norev.py"))
            n += 2
        for tail, text0, rev in bases:
            a, b = stubs_region(text0, tree_start)
            for level, make in (("simple", simple), ("complex", complex_)):
                text = text0[:a] + make(kind, lazy, rev) + text0[b:]
                text = re.sub(r"generic/" + stem + r"(\.norev)?\.cpp", f"generic/{stem}.{level}{tail}.cpp", text)
                open(os.path.join(DIR, f"{stem}.{level}{tail}.cpp"), "w").write(text)
                n += 1
    print("wrote", n, "files")

if __name__ == "__main__":
    main()
