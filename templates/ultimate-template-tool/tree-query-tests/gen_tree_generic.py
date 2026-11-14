"""Writes the generic tree templates: generic-trees/Generic[Lazy]Tree{Nodes,Edges,Both}[.simple|.complex][.norev].{py,cpp}.

The fill-in templates of the tree picker, shaped like the generic seg trees (generic-seg-trees/): you write what a
stretch of values is summed up as and how two stretches join, and the Tree answers paths and subtrees with it. Six
families: node values, edge weights, or both (two separate merges in one Tree), each plain or lazy (a tag applied to
every value of a path or a subtree).

What is filled in, for nodes (edges: the same with Edge / edge):
    NodeVal                      a node's raw value
    NodeData                     what a stretch of nodes is summed up as
    nodeLeaf(v, node)            the data of one node
    nodeCombine(left, right)     two stretches joined
    nodeReverse(data)            the same stretch read backwards: only in the versions where the order along a path
                                 matters. The .norev files have no reverse to fill in
    NodeTag, nodeApply(data, tag), nodeCompose(old, newer)     lazy only

There are no identity values: a seg tree slot that covers nothing is marked as such, a path's pieces are joined
starting from the first one, and an edge query with no edges (the path a..a, a leaf's subtree) raises.

Python has one example level; C++ has the three of the generic seg trees (.simple.cpp, .cpp, .complex.cpp). The
examples are comments: test_tree_generic.py switches every one on and checks it against a plain fold. The C++ files
are in fast mode like every tree template, and that covers the functions filled in: each starts with
LEETCODE_NO_SANITIZE, as in the generic seg trees' fast version (unmarked, they could not be inlined into the marked
tree code that calls them).

    python3 gen_tree_generic.py           # write
    python3 gen_tree_generic.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402

DIR = os.path.join(shape.ROOT, "generic-trees")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-trees"
KINDS = ("Nodes", "Edges", "Both")
LEVELS = ("simple", "basic", "complex")  # (the C++ example levels; Python has the basic one only)
NO_TAG_NOTE = ("We never need to worry about initializing empty tags or anything, these tags come in via the update calls "
               "or when pushed down from parents")
APPLY_NOTE = ("return new data: this data after tag is applied to it. This function is never called with a tag that never "
              "existed, but tags can have things like pending false values or pending no-ops (for instance two lazy bools "
              "canceling) and we still need to check for this and no-op (could just return the original data)")
BY_VALUE = "This is NOT mutating since {arg} is taken by value in the arg, we can also just make a new {what} if needed"


# (the line the C++ fill-in section starts after: test_tree_generic.py switches the examples on from here down)
FILL_NOTE = G.wrap("//", "WHAT YOU FILL IN. Fast mode covers these functions too (each one starts with LEETCODE_NO_SANITIZE): "
                   "sanitizers are skipped in them, so a bad access in one goes unreported. The #define in the FAST MODE "
                   "note above turns that off for them as well. Any helper they call needs LEETCODE_NO_SANITIZE too, and "
                   "so does a constructor of your data or tag struct.")


def combine_note(t, rev):
    """What the combine function is handed: about reading order only, never about up or down in the tree."""
    if rev:
        return ("two stretches that sit next to each other, joined into one: left is the one read first, right the one read "
                "straight after it. Left and right are about reading order only, not about up or down in the tree. The "
                "template calls this on any two neighbouring stretches (inside its segment tree, and when it puts the "
                f"pieces of a path together), and where a path walks up a stretch it has already turned that stretch "
                f"around with {t}Reverse")
    return ("two stretches joined into one. In this version the result must not depend on which one is left and which is "
            "right (a sum, a min, a gcd, ...): the template hands the two over in whatever order it meets them. If reading "
            f"a path a -> b can give a different answer than reading it b -> a, use the version with {t}Reverse (\"order "
            "matters on a path\")")


COMPOSE_NOTE = ("one tag that does what old does and then what newer does. Only ever called with two real tags: old is "
                "already waiting at a slot when newer arrives there (the first tag to reach a slot is just stored as it is)")


def must(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


# ---------------------------------------------------------------- the fill-in sections

def py_fill(t, rev, lazy):
    """The Python fill-in section for one target ("node" or "edge"): types, then functions, each with its example."""
    T, things, thing = t.capitalize(), ("nodes" if t == "node" else "edges"), ("node" if t == "node" else "edge")
    raw, raw_word = ("v", "value") if t == "node" else ("w", "weight")
    where = "node: int" if t == "node" else "a: int, b: int"
    if rev:
        leaf = f"({raw}, {raw}, {raw}, 1)  # (tot, the {raw_word} at the first end, at the last end, len)"
        comb = "(left[0] + right[0], left[1], right[2], left[3] + right[3])"
        appl = "(data[0] + tag * data[3], data[1] + tag, data[2] + tag, data[3])"
    elif lazy:
        leaf, comb = f"({raw}, {raw}, 1)", "(left[0] + right[0], min(left[1], right[1]), left[2] + right[2])"
        appl = "(data[0] + tag * data[2], data[1] + tag, data[2])"
    else:
        leaf, comb = f"({raw}, {raw})", "(left[0] + right[0], min(left[1], right[1]))"
    types = [f"# {'a' if t == 'node' else 'an'} {thing}'s raw {raw_word}, e.g. int, str, tuple, ...\n{T}Val = int\n",
             f"# what a stretch of {things} is summed up as. Can replace this tuple with an entire class and it works\n"
             f"{T}Data = tuple\n"]
    if lazy:
        types.append(f"# a pending update to every {thing} of a stretch, e.g. add\n" + G.wrap("#", NO_TAG_NOTE)
                     + f"{T}Tag = int\n")
    ends = "" if t == "node" else " (a and b: its two ends, a the one nearer the root)"
    funcs = [f"# the data of one {thing}{' (node: its label)' if t == 'node' else ends}\n"
             f"def {t}Leaf({raw}: {T}Val, {where}) -> {T}Data:\n    # return {leaf}\n    pass\n",
             G.wrap("#", combine_note(t, rev)) +
             f"def {t}Combine(left: {T}Data, right: {T}Data) -> {T}Data:\n    # return {comb}\n    pass\n"]
    if rev:
        funcs.append(f"# the data of the same stretch read backwards\n"
                     f"def {t}Reverse(data: {T}Data) -> {T}Data:\n"
                     "    # return (data[0], data[2], data[1], data[3])  # (read backwards, the two ends trade places)\n"
                     "    pass\n")
    if lazy:
        funcs.append(G.wrap("#", APPLY_NOTE) + f"def {t}Apply(data: {T}Data, tag: {T}Tag) -> {T}Data:\n"
                     f"    # return {appl}\n    pass\n")
        funcs.append(G.wrap("#", COMPOSE_NOTE) +
                     f"def {t}Compose(old: {T}Tag, newer: {T}Tag) -> {T}Tag:\n    # return old + newer\n    pass\n")
    return "\n".join(types) + "\n\n" + "\n\n".join(funcs)


def cpp_fill(t, rev, lazy, level):
    """The C++ fill-in section for one target at one example level."""
    T, things, thing = t.capitalize(), ("nodes" if t == "node" else "edges"), ("node" if t == "node" else "edge")
    raw, raw_word = ("v", "value") if t == "node" else ("w", "weight")
    where = "int node" if t == "node" else "int a, int b"
    a_thing = f"{'a' if t == 'node' else 'an'} {thing}"
    ends = " (node: its label)" if t == "node" else " (a and b: its two ends, a the one nearer the root)"
    D, G_ = f"{T}Data", f"{T}Tag"
    value_note = BY_VALUE.format(arg="data", what="one")
    tag_value_note = BY_VALUE.format(arg="old", what="tag")
    out = []

    def fn(comment, sig, body):
        lines = "".join(f"    // {line}\n" for line in body)
        out.append("".join(f"// {c}\n" for c in comment) + f"LEETCODE_NO_SANITIZE {sig} {{\n{lines}}}\n")

    leaf_sig = f"{D} {t}Leaf(const {T}Val& {raw}, {where})"
    comb_sig = f"{D} {t}Combine(const {D}& left, const {D}& right)"
    rev_sig, app_sig = f"{D} {t}Reverse({D} data)", f"{D} {t}Apply({D} data, const {G_}& tag)"
    com_sig = f"{G_} {t}Compose({G_} old, const {G_}& newer)"
    apply_comment = G.wrap("//", APPLY_NOTE).rstrip("\n").replace("// ", "", 1).split("\n// ")
    def lines(text):  # a comment's lines, wrapped
        return G.wrap("//", text).rstrip("\n").replace("// ", "", 1).split("\n// ")
    leaf_comment, comb_comment = [f"the data of one {thing}{ends}"], lines(combine_note(t, rev))
    rev_comment, com_comment = ["the data of the same stretch read backwards"], lines(COMPOSE_NOTE)
    tag_comment = [f"a pending update to every {thing} of a stretch", *G.wrap("//", NO_TAG_NOTE).rstrip("\n")
                   .replace("// ", "", 1).split("\n// ")]

    if level == "simple":
        out.append(f"// {a_thing}'s raw {raw_word}, e.g. long long, char, ...\nusing {T}Val = long long;\n")
        if rev:
            out.append(f"// what a stretch of {things} is summed up as. A plain type: here its (first, last) {raw_word}s\n"
                       f"using {D} = pair<long long, long long>;\n")
        else:
            out.append(f"// what a stretch of {things} is summed up as. A plain type: here its max\n"
                       f"using {D} = long long;\n")
        if lazy:
            out.append("".join(f"// {c}\n" for c in [tag_comment[0] + ": here add this much", *tag_comment[1:]])
                       + f"using {G_} = long long;\n")
        if rev:
            fn(leaf_comment, leaf_sig, [f"return {{{raw}, {raw}}};"])
            fn(comb_comment, comb_sig, ["return {left.first, right.second};"])
            fn(rev_comment, rev_sig, ["return {data.second, data.first};  // (read backwards, the two ends trade places)"])
            if lazy:
                fn(apply_comment, app_sig, ["return {data.first + tag, data.second + tag};"])
        else:
            fn(leaf_comment, leaf_sig, [f"return {raw};"])
            fn(comb_comment, comb_sig, ["return max(left, right);"])
            if lazy:
                fn(apply_comment, app_sig, [f"return data + tag;  // (adding to every {thing} raises the max by as much)"])
        if lazy:
            fn(com_comment, com_sig, ["return old + newer;"])
    elif level == "basic":
        out.append(f"// {a_thing}'s raw {raw_word}, e.g. long long, char, pair, struct, ...\nusing {T}Val = long long;\n")
        fields = ["long long tot;", "long long first, last;", "int len;"] if rev else \
            ["long long tot;", "long long mn;"] + (["int len;"] if lazy else [])
        out.append(f"// what a stretch of {things} is summed up as\nstruct {D} {{\n"
                   + "".join(f"    // {f}\n" for f in fields) + "};\n")
        if lazy:
            out.append("".join(f"// {c}\n" for c in tag_comment) + f"struct {G_} {{\n    // long long add;\n}};\n")
        if rev:
            fn(leaf_comment, leaf_sig, [f"{D} res;", f"res.tot = {raw}, res.first = res.last = {raw}, res.len = 1;", "return res;"])
            fn(comb_comment, comb_sig, [f"{D} res;", "res.tot = left.tot + right.tot;",
                                        "res.first = left.first, res.last = right.last;",
                                        "res.len = left.len + right.len;", "return res;"])
            fn(rev_comment, rev_sig, [value_note, "swap(data.first, data.last);  // (read backwards, the two ends trade places)",
                                      "return data;"])
            if lazy:
                fn(apply_comment, app_sig, [value_note, "data.tot += tag.add * data.len, data.first += tag.add, data.last += tag.add;",
                                            "return data;"])
        else:
            fn(leaf_comment, leaf_sig, [f"{D} res;", f"res.tot = {raw}, res.mn = {raw};" + (" res.len = 1;" if lazy else ""),
                                        "return res;"] if not lazy else
               [f"{D} res;", f"res.tot = {raw}, res.mn = {raw}, res.len = 1;", "return res;"])
            fn(comb_comment, comb_sig, [f"{D} res;", "res.tot = left.tot + right.tot, res.mn = min(left.mn, right.mn);",
                                        *(["res.len = left.len + right.len;"] if lazy else []), "return res;"])
            if lazy:
                fn(apply_comment, app_sig, [value_note, "data.tot += tag.add * data.len, data.mn += tag.add;", "return data;"])
        if lazy:
            fn(com_comment, com_sig, [tag_value_note, "old.add += newer.add;", "return old;"])
    else:  # complex: letters
        out.append(f"// {a_thing}'s raw {raw_word}, e.g. long long, char, pair, struct, ...\nusing {T}Val = char;\n")
        fields = ["int cnt[26];  // how many of each letter",
                  *(["char first, last;  // the letters at the two ends"] if rev else []), "int len;",
                  f"LEETCODE_NO_SANITIZE {D}() {{  // can make an empty constructor which runs every time one is made",
                  "    for (int c = 0; c < 26; c++) cnt[c] = 0;  // (the other fields are always set before they're read)",
                  "}"]
        out.append(f"// what a stretch of {things} is summed up as\nstruct {D} {{\n"
                   + "".join(f"    // {f}\n" for f in fields) + "};\n")
        if lazy:
            out.append("".join(f"// {c}\n" for c in tag_comment) + f"struct {G_} {{\n"
                       f"    // bool assign;  // every {thing} becomes letter, if set\n    // char letter;\n"
                       "    // int shift;  // then every letter moves this many places on, z wrapping to a (0..25; 0 = none)\n"
                       "};\n")
        fn(leaf_comment, leaf_sig, [f"{D} res;", f"res.cnt[{raw} - 'a'] = 1;",
                                    *([f"res.first = res.last = {raw};"] if rev else []), "res.len = 1;", "return res;"])
        fn(comb_comment, comb_sig, [f"{D} res;", "for (int c = 0; c < 26; c++) res.cnt[c] = left.cnt[c] + right.cnt[c];",
                                    *(["res.first = left.first, res.last = right.last;"] if rev else []),
                                    "res.len = left.len + right.len;", "return res;"])
        if rev:
            fn(rev_comment, rev_sig, [value_note, "swap(data.first, data.last);  // (read backwards, the two ends trade places)",
                                      "return data;"])
        if lazy:
            fn(apply_comment, app_sig, [
                value_note, "if (tag.assign) {", "    for (int c = 0; c < 26; c++) data.cnt[c] = 0;",
                "    data.cnt[tag.letter - 'a'] = data.len;", *(["    data.first = data.last = tag.letter;"] if rev else []), "}",
                "if (tag.shift) {",
                "    rotate(data.cnt, data.cnt + 26 - tag.shift, data.cnt + 26);  // (letter c's count moves to c + shift)",
                *(["    data.first = 'a' + (data.first - 'a' + tag.shift) % 26;",
                   "    data.last = 'a' + (data.last - 'a' + tag.shift) % 26;"] if rev else []), "}", "return data;"])
            fn(com_comment, com_sig, [tag_value_note, "if (newer.assign) return newer;  // (a later assign wipes out everything before it)",
                                      "old.shift = (old.shift + newer.shift) % 26;  // (shifts add up, still after old's assign if it had one)",
                                      "return old;"])
    return "\n".join(out)


# ---------------------------------------------------------------- the segment trees (no identity value)

PY_SEG = '''\
# A segment tree with no identity value: a slot that covers nothing holds None. data: one item per leaf, in order
class _Seg:
    def __init__(self, data, combine):
        self.n = n = len(data)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.combine = combine
        # (None: a slot over the padding past n only)
        self.t = t = [None] * cap + data + [None] * (cap - n)
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    # the data of item i
    def get(self, i):
        return self.t[self.cap + i]

    # item i becomes data
    def set(self, i, data):
        t, combine = self.t, self.combine
        k = self.cap + i
        t[k] = data
        k >>= 1
        while k:
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])
            k >>= 1

    # items l..r joined in order (needs l <= r)
    def query(self, l, r):
        t, combine = self.t, self.combine
        sl = sr = None
        l += self.cap
        r += self.cap + 1
        while l < r:
            if l & 1:
                sl = t[l] if sl is None else combine(sl, t[l])
                l += 1
            if r & 1:
                r -= 1
                sr = t[r] if sr is None else combine(t[r], sr)
            l >>= 1
            r >>= 1
        if sl is None:
            return sr
        if sr is None:
            return sl
        return combine(sl, sr)
'''
PY_LAZY_SEG = '''\
# A lazy segment tree with no identity value: a slot that covers nothing holds None, and a slot with no tag waiting
# holds _NO_TAG. data: one item per leaf, in order
class _LazySeg:
    _NO_TAG = object()  # (so any tag value works, None too)

    def __init__(self, data, combine, apply, compose):
        self.n = n = len(data)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.lg = cap.bit_length() - 1
        self.combine, self.apply, self.compose = combine, apply, compose
        # (None: a slot over the padding past n only)
        self.t = t = [None] * cap + data + [None] * (cap - n)
        # lz[k]: the tag waiting for slot k's two children
        self.lz = [_LazySeg._NO_TAG] * cap
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    def _applyAt(self, k, tag):
        t = self.t
        if t[k] is None:
            return
        t[k] = self.apply(t[k], tag)
        if k < self.cap:
            lz = self.lz
            lz[k] = tag if lz[k] is _LazySeg._NO_TAG else self.compose(lz[k], tag)

    def _push(self, k):
        tag = self.lz[k]
        if tag is not _LazySeg._NO_TAG:
            self._applyAt(2 * k, tag)
            self._applyAt(2 * k + 1, tag)
            self.lz[k] = _LazySeg._NO_TAG

    def _pull(self, k):
        t = self.t
        t[k] = t[2 * k] if t[2 * k + 1] is None else self.combine(t[2 * k], t[2 * k + 1])

    # hands down the tags above the leaf range [l, r) (l and r already offset by cap)
    def _pushAbove(self, l, r):
        for i in range(self.lg, 0, -1):
            if (l >> i) << i != l:
                self._push(l >> i)
            if (r >> i) << i != r:
                self._push((r - 1) >> i)

    # the data of item i
    def get(self, i):
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        return self.t[k]

    # item i becomes data
    def set(self, i, data):
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        self.t[k] = data
        for j in range(1, self.lg + 1):
            self._pull(k >> j)

    # items l..r joined in order (needs l <= r)
    def query(self, l, r):
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        t, combine = self.t, self.combine
        sl = sr = None
        while l < r:
            if l & 1:
                sl = t[l] if sl is None else combine(sl, t[l])
                l += 1
            if r & 1:
                r -= 1
                sr = t[r] if sr is None else combine(t[r], sr)
            l >>= 1
            r >>= 1
        if sl is None:
            return sr
        if sr is None:
            return sl
        return combine(sl, sr)

    # tag applied to every one of items l..r (needs l <= r)
    def update(self, l, r, tag):
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        a, b = l, r
        while a < b:
            if a & 1:
                self._applyAt(a, tag)
                a += 1
            if b & 1:
                b -= 1
                self._applyAt(b, tag)
            a >>= 1
            b >>= 1
        for i in range(1, self.lg + 1):
            if (l >> i) << i != l:
                self._pull(l >> i)
            if (r >> i) << i != r:
                self._pull((r - 1) >> i)
'''
CPP_SEG = '''\
// A segment tree with no identity value: has[k] says whether slot k covers anything. data: one item per leaf, in order
struct @Seg@ {
    int n = 0, cap = 1;
    HotVector<@Data@> t;
    HotVector<char> has;

    void build(const vector<@Data@>& data) {
        n = (int)data.size();
        while (cap < n) cap *= 2;
        t.assign(2 * cap, @Data@());
        has.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = data[i], has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    // (the padding is a suffix, so a slot with an empty right child is just its left child)
    LEETCODE_NO_SANITIZE void pull(int k) {
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = @combine@(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    // the data of item i
    LEETCODE_NO_SANITIZE @Data@ get(int i) { return t[cap + i]; }

    // item i becomes data
    LEETCODE_NO_SANITIZE void set(int i, const @Data@& data) {
        int k = cap + i;
        t[k] = data;
        for (k >>= 1; k >= 1; k >>= 1) pull(k);
    }

    // items l..r joined in order (needs l <= r)
    LEETCODE_NO_SANITIZE @Data@ query(int l, int r) {
        l += cap, r += cap + 1;
        @Data@ sl = @Data@(), sr = @Data@();  // (set before they are read: hl and hr say when)
        bool hl = false, hr = false;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) sl = hl ? @combine@(sl, t[l]) : t[l], hl = true, l++;
            if (r & 1) --r, sr = hr ? @combine@(t[r], sr) : t[r], hr = true;
        }
        if (!hl) return sr;
        if (!hr) return sl;
        return @combine@(sl, sr);
    }
};
'''
CPP_LAZY_SEG = '''\
// A lazy segment tree with no identity value: has[k] says whether slot k covers anything, tagged[k] whether lz[k] is
// waiting for slot k's two children. data: one item per leaf, in order
struct @Seg@ {
    int n = 0, cap = 1, lg = 0;
    HotVector<@Data@> t;
    HotVector<@Tag@> lz;
    HotVector<char> has, tagged;

    void build(const vector<@Data@>& data) {
        n = (int)data.size();
        while (cap < n) cap *= 2, lg++;
        t.assign(2 * cap, @Data@());
        lz.assign(cap, @Tag@());
        has.assign(2 * cap, 0);
        tagged.assign(cap, 0);
        for (int i = 0; i < n; i++) t[cap + i] = data[i], has[cap + i] = 1;
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    // (the padding is a suffix, so a slot with an empty right child is just its left child)
    LEETCODE_NO_SANITIZE void pull(int k) {
        has[k] = has[2 * k];
        if (has[2 * k + 1]) t[k] = @combine@(t[2 * k], t[2 * k + 1]);
        else if (has[2 * k]) t[k] = t[2 * k];
    }

    LEETCODE_NO_SANITIZE void applyAt(int k, const @Tag@& tag) {
        if (!has[k]) return;
        t[k] = @apply@(t[k], tag);
        if (k < cap) {
            if (tagged[k]) lz[k] = @compose@(lz[k], tag);
            else lz[k] = tag, tagged[k] = 1;
        }
    }

    LEETCODE_NO_SANITIZE void push(int k) {
        if (!tagged[k]) return;
        applyAt(2 * k, lz[k]);
        applyAt(2 * k + 1, lz[k]);
        tagged[k] = 0;
    }

    // hands down the tags above the leaf range [l, r) (l and r already offset by cap)
    LEETCODE_NO_SANITIZE void pushAbove(int l, int r) {
        for (int i = lg; i >= 1; i--) {
            if (((l >> i) << i) != l) push(l >> i);
            if (((r >> i) << i) != r) push((r - 1) >> i);
        }
    }

    // the data of item i
    LEETCODE_NO_SANITIZE @Data@ get(int i) {
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        return t[k];
    }

    // item i becomes data
    LEETCODE_NO_SANITIZE void set(int i, const @Data@& data) {
        int k = cap + i;
        for (int j = lg; j >= 1; j--) push(k >> j);
        t[k] = data;
        for (int j = 1; j <= lg; j++) pull(k >> j);
    }

    // items l..r joined in order (needs l <= r)
    LEETCODE_NO_SANITIZE @Data@ query(int l, int r) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        @Data@ sl = @Data@(), sr = @Data@();  // (set before they are read: hl and hr say when)
        bool hl = false, hr = false;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) sl = hl ? @combine@(sl, t[l]) : t[l], hl = true, l++;
            if (r & 1) --r, sr = hr ? @combine@(t[r], sr) : t[r], hr = true;
        }
        if (!hl) return sr;
        if (!hr) return sl;
        return @combine@(sl, sr);
    }

    // tag applied to every one of items l..r (needs l <= r)
    LEETCODE_NO_SANITIZE void update(int l, int r, const @Tag@& tag) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) applyAt(a++, tag);
            if (b & 1) applyAt(--b, tag);
        }
        for (int i = 1; i <= lg; i++) {
            if (((l >> i) << i) != l) pull(l >> i);
            if (((r >> i) << i) != r) pull((r - 1) >> i);
        }
    }
};
'''


def cpp_seg(t, lazy):
    T = t.capitalize()
    text = CPP_LAZY_SEG if lazy else CPP_SEG
    for k, v in {"@Seg@": f"{T}Seg", "@Data@": f"{T}Data", "@Tag@": f"{T}Tag", "@combine@": f"{t}Combine",
                 "@apply@": f"{t}Apply", "@compose@": f"{t}Compose"}.items():
        text = text.replace(k, v)
    return text


# ---------------------------------------------------------------- the Tree's ops

PY_PIECES = '''\
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        update = self.@t@Seg.update
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            update(pos[head[a]]@S@, pos[a]@S@, tag)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
@LAST@'''
CPP_PIECES = '''\
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) swap(a, b);
            @t@Seg.update(pos[head[a]]@S@, pos[a]@S@, tag);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) swap(l, r);
@LAST@'''


def ops(t, rev, lazy):
    """(py methods, cpp methods) of one target: the text of every value op, in menu order."""
    T, edge = t.capitalize(), t == "edge"
    D, things = f"{T}Data", ("edges" if edge else "nodes")
    seg, S = f"{t}Seg", (" - 1" if edge else "")  # (the edge above position p is item p - 1: the root has no edge)
    py, cpp = [], []
    order_note = (", read a -> b" if rev else "")
    sub_order = (" (read in position order: a node, then its heavy child's subtree, then the others'; only an answer "
                 "that does not depend on the order means anything here)" if rev else "")

    def add(cost, doc, py_sig, py_body, cpp_sig, cpp_body):
        py.append(G.comment("#", cost, doc) + f"    def {py_sig}:\n" + py_body)
        cpp.append(G.comment("//", cost, doc) + f"    LEETCODE_NO_SANITIZE {cpp_sig} {{\n" + cpp_body + "    }\n")

    if edge:
        py.append("    # the lower end of the edge a - b, the node its weight is kept under (a and b in either order)\n"
                  "    def _edge(self, name, a, b):\n"
                  "        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):\n"
                  "            self._bad(name, a, b)\n"
                  "        if self.par[a] == b:\n            return a\n"
                  "        if self.par[b] == a:\n            return b\n"
                  '        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")\n')
        cpp.append("    // the lower end of the edge a - b, the node its weight is kept under (a and b in either order)\n"
                   "    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {\n"
                   "        if (a < lo || a > hi || b < lo || b > hi) bad(name);\n"
                   "        if (par[a] == b) return a;\n        if (par[b] == a) return b;\n"
                   '        throw out_of_range(string(name) + ": needs an edge between a and b");\n    }\n')
        either = "; a and b are the edge's two ends, in either order"

        def one(name):
            return (f'        v = self._edge("edge{name}", a, b)\n', f'        int v = edgeAt("edge{name}", a, b);\n')
        at, sig_py, sig_cpp, raw = "the edge a - b", "a, b", "int a, int b", "w"
        leaf_py, leaf_cpp = "edgeLeaf(w, self.par[v], v)", "edgeLeaf(w, par[v], v)"
    else:
        either = ""

        def one(name):
            return (G.py_check(f"node{name}", ("node",)) + "        v = node\n",
                    G.cpp_check(f"node{name}", ("node",)) + "        int v = node;\n")
        at, sig_py, sig_cpp, raw = "node", "node", "int node", "val"
        leaf_py, leaf_cpp = "nodeLeaf(val, node)", "nodeLeaf(val, node)"
    if not edge:  # (no helper variable for a node: its label is the argument)
        def one(name):  # noqa: F811
            return G.py_check(f"node{name}", ("node",)), G.cpp_check(f"node{name}", ("node",))
    v_py, v_cpp = ("self.pos[v] - 1", "pos[v] - 1") if edge else ("self.pos[node]", "pos[node]")

    # ---- one node / edge
    p, c = one("Get")
    add("log(N)" if lazy else "1", f"the data of {at} alone{either}", f"{t}Get(self, {sig_py})",
        p + f"        return self.{seg}.get({v_py})\n", f"{D} {t}Get({sig_cpp})", c + f"        return {seg}.get({v_cpp});\n")
    p, c = one("Assign")
    what = "weight" if edge else "value"
    add("log(N)", f"the {what} of {at} becomes {raw}{either}", f"{t}Assign(self, {sig_py}, {raw})",
        p + f"        self.{seg}.set({v_py}, {leaf_py})\n",
        f"void {t}Assign({sig_cpp}, const {T}Val& {raw})", c + f"        {seg}.set({v_cpp}, {leaf_cpp});\n")
    if lazy:
        p, c = one("Update")
        add("log(N)", f"tag applied to {at}{either}", f"{t}Update(self, {sig_py}, tag)",
            p + f"        p = {v_py}\n        self.{seg}.update(p, p, tag)\n",
            f"void {t}Update({sig_cpp}, const {T}Tag& tag)", c + f"        int p = {v_cpp};\n        {seg}.update(p, p, tag);\n")

    # ---- a path
    join_py = f"res = piece if res is None else {t}Combine(res, piece)"
    join_cpp = f"res = any ? {t}Combine(res, piece) : piece, any = true;"
    plain_py, plain_cpp = f"piece = query(l{S}, r{S})\n{join_py}", f"{D} piece = {seg}.query(l{S}, r{S});\n{join_cpp}"
    up_py = f"piece = {t}Reverse(query(l{S}, r{S}))\n{join_py}" if rev else plain_py
    up_cpp = f"{D} piece = {t}Reverse({seg}.query(l{S}, r{S}));\n{join_cpp}" if rev else plain_cpp
    none_py = ('        if res is None:\n'
               '            raise IndexError(f"edgePathQuery: needs a != b (a path from a node to itself has no edges), "\n'
               '                             f"got a = b = {a}")\n') if edge else ""
    none_cpp = ('        if (!any)\n'
                '            throw out_of_range("edgePathQuery: needs a != b (a path from a node to itself has no edges)");\n') if edge else ""
    raises = ("; raises IndexError when a == b (no edges)", "; throws out_of_range when a == b (no edges)") if edge else ("", "")
    doc = f"the data of the {things} on the path a..b{order_note}"
    py.append(G.comment("#", "log^2(N)", doc + raises[0]) + f"    def {t}PathQuery(self, a, b):\n"
              + G.py_check(f"{t}PathQuery", ("a", "b"))
              + "        head, par, dep, pos = self.head, self.par, self.dep, self.pos\n"
              f"        query = self.{seg}.query\n        res = None\n"
              + G.walk(G.PY_WALK, up_py, plain_py, edge) + none_py + "        return res\n")
    cpp.append(G.comment("//", "log^2(N)", doc + raises[1]) + f"    LEETCODE_NO_SANITIZE {D} {t}PathQuery(int a, int b) {{\n"
               + G.cpp_check(f"{t}PathQuery", ("a", "b")) + f"        {D} res = {D}();  // (set before it is read: any says when)\n        bool any = false;\n"
               + G.walk(G.CPP_WALK, up_cpp, plain_cpp, edge) + none_cpp + "        return res;\n    }\n")
    if lazy:
        last_py = ("        if l < r:  # (the lca's own position is the edge above it)\n            update(l, r - 1, tag)\n"
                   if edge else "        update(l, r, tag)\n")
        last_cpp = (f"        if (l < r) {seg}.update(l, r - 1, tag);  // (the lca's own position is the edge above it)\n"
                    if edge else f"        {seg}.update(l, r, tag);\n")
        nothing = " (nothing when a == b)" if edge else ""
        add("log^2(N)", f"tag applied to every one of the {things} on the path a..b{nothing}", f"{t}PathUpdate(self, a, b, tag)",
            G.py_check(f"{t}PathUpdate", ("a", "b")) + PY_PIECES.replace("@t@", t).replace("@S@", S).replace("@LAST@", last_py),
            f"void {t}PathUpdate(int a, int b, const {T}Tag& tag)",
            G.cpp_check(f"{t}PathUpdate", ("a", "b")) + CPP_PIECES.replace("@t@", t).replace("@S@", S).replace("@LAST@", last_cpp))

    # ---- a subtree: one stretch of positions (for edges: the ones after node's own, which is the edge above it)
    if edge:
        sub_py = ("        l = self.pos[node]\n        if self.sz[node] == 1:\n"
                  '            raise IndexError(f"edgeSubtreeQuery: node {node} is a leaf, so there are no edges below it")\n'
                  f"        return self.{seg}.query(l, l + self.sz[node] - 2)\n")
        sub_cpp = ('        if (sz[node] == 1) throw out_of_range("edgeSubtreeQuery: node is a leaf, so there are no edges below it");\n'
                   f"        return {seg}.query(pos[node], pos[node] + sz[node] - 2);\n")
        doc = "the data of the edges below node"
        raises = ("; raises IndexError when node is a leaf (no edges)", "; throws out_of_range when node is a leaf (no edges)")
    else:
        sub_py = f"        l = self.pos[node]\n        return self.{seg}.query(l, l + self.sz[node] - 1)\n"
        sub_cpp = f"        return {seg}.query(pos[node], pos[node] + sz[node] - 1);\n"
        doc, raises = "the data of the nodes in node's subtree", ("", "")
    py.append(G.comment("#", "log(N)", doc + sub_order + raises[0]) + f"    def {t}SubtreeQuery(self, node):\n"
              + G.py_check(f"{t}SubtreeQuery", ("node",)) + sub_py)
    cpp.append(G.comment("//", "log(N)", doc + sub_order + raises[1])
               + f"    LEETCODE_NO_SANITIZE {D} {t}SubtreeQuery(int node) {{\n"
               + G.cpp_check(f"{t}SubtreeQuery", ("node",)) + sub_cpp + "    }\n")
    if lazy:
        if edge:
            upd_py = ("        l = self.pos[node]\n        if self.sz[node] > 1:\n"
                      f"            self.{seg}.update(l, l + self.sz[node] - 2, tag)\n")
            upd_cpp = f"        if (sz[node] > 1) {seg}.update(pos[node], pos[node] + sz[node] - 2, tag);\n"
            doc = "tag applied to every edge below node (nothing when node is a leaf)"
        else:
            upd_py = f"        l = self.pos[node]\n        self.{seg}.update(l, l + self.sz[node] - 1, tag)\n"
            upd_cpp = f"        {seg}.update(pos[node], pos[node] + sz[node] - 1, tag);\n"
            doc = "tag applied to every node in node's subtree"
        add("log(N)", doc, f"{t}SubtreeUpdate(self, node, tag)", G.py_check(f"{t}SubtreeUpdate", ("node",)) + upd_py,
            f"void {t}SubtreeUpdate(int node, const {T}Tag& tag)", G.cpp_check(f"{t}SubtreeUpdate", ("node",)) + upd_cpp)
    return py, cpp


# ---------------------------------------------------------------- one file

HOW = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one "
       "stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps, for each "
       "of its slots, the data of the {things} under it joined in position order{edge_at}. A subtree is one stretch, and "
       "a path a..b is O(log n) stretches, one per chain it crosses{rev}. Nothing here needs an identity value: a "
       "slot that covers nothing is marked as such and left out, and a path's pieces are joined starting from the first "
       "one{lazy}.")


EDGE_NOTES = ("An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the "
              "edges between a and b, and a subtree covers the edges below node. A query with no edges to join (the path "
              "from a node to itself, the edges below a leaf) {raises}: there is no identity value to return. An update "
              "there does nothing. Nodes go in and come out with your labels, -1 means \"none\", and a label that is not "
              "in the tree {raises}. Nothing recurses, so a 10^6-node chain is fine.")
BOTH_NOTES = ("The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each "
              "other. For nodes, a path a..b includes both a and b. " + EDGE_NOTES.replace("A path a..b covers", "For edges, a path a..b covers"))


def class_doc(cm, kind, sig, how):
    """The comment above the Tree: how it is built, what the labels and edges mean, how it works."""
    py = cm == "#"
    doc = {"Nodes": (G.PY_DOC, G.CPP_DOC), "Edges": (G.PY_DOC_EDGE, G.CPP_DOC_EDGE), "Both": (G.PY_DOC_BOTH, G.CPP_DOC_BOTH)}[kind][not py]
    notes = {"Nodes": "", "Edges": EDGE_NOTES, "Both": BOTH_NOTES}[kind].format(raises="raises IndexError" if py else "throws out_of_range")
    return (doc.replace("@SIG@", sig).replace("@EXTRA@", "").replace("@EX@", "").replace("@NOTES@", G.wrap(cm, notes))
            .replace("@HOW@", G.wrap(cm, how)))


def make(kind, lazy, rev, level, ext):
    """One file's text. level: a C++ example level ("basic" for Python)."""
    targets = {"Nodes": ("node",), "Edges": ("edge",), "Both": ("node", "edge")}[kind]
    name = f"Generic{'Lazy' if lazy else ''}Tree{kind}"
    file = name + ("" if level == "basic" else f".{level}") + ("" if rev else ".norev") + f".{ext}"
    cm = "#" if ext == "py" else "//"
    sig = "edges, root" if kind == "Edges" else "edges, root, vals"
    things = {"Nodes": "nodes", "Edges": "edges", "Both": "nodes (nodeSeg) or of the edges (edgeSeg)"}[kind]
    edge_at = "" if kind == "Nodes" else (" (an edge sits at its lower end's position, so the root's position holds none "
                                          "and the edges are items 0 .. n - 2)")
    how = HOW.format(
        things=things, edge_at=edge_at,
        rev=(": the ones on a's side are read backwards, which is what the reverse function is for" if rev else ""),
        lazy=("; a tag waits at the O(log n) slots that cover a stretch until something below one of them is needed, and "
              "a slot with no tag waiting is marked as such too" if lazy else ""))
    py_ops, cpp_ops = [], []
    for t in targets:
        p, c = ops(t, rev, lazy)
        py_ops += p
        cpp_ops += c

    if ext == "py":
        doc = class_doc("#", kind, sig, how)
        fills = "\n\n".join(py_fill(t, rev, lazy) for t in targets)
        seg_cls = "_LazySeg" if lazy else "_Seg"
        build = ""
        if "node" in targets:
            build += G.PY_VALS + (f"        self.nodeSeg = {seg_cls}([nodeLeaf(vals[v], v) for v in order], nodeCombine"
                                  + (", nodeApply, nodeCompose" if lazy else "") + ")\n")
        if "edge" in targets:
            build += ("        for e in edges:\n            if len(e) != 3:\n"
                      '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                      "        above = [None] * (hi + 1)  # above[v]: the weight of the edge above v (the root has none)\n"
                      "        for e in edges:\n            above[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n"
                      "        # the edge above the node at position p is item p - 1 (position 0 is the root: no edge)\n"
                      f"        self.edgeSeg = {seg_cls}([edgeLeaf(above[v], par[v], v) for v in order[1:]], edgeCombine"
                      + (", edgeApply, edgeCompose" if lazy else "") + ")\n")
        bad = {"Nodes": "vals has the wrong length", "Edges": "an edge has no weight",
               "Both": "vals has the wrong length or an edge has no weight"}[kind]
        ctor = (note("#", "O(n) -- builds the layout and the segment tree" + ("s" if kind == "Both" else "") + "; raises "
                     f"ValueError when the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4)
                + f"\n    def __init__(self, {sig}):\n" + shape.py_layout_body() + build)
        return file, (f"# Template by https://github.com/ishaanbuildsthings\n# {URL}/{file}\nfrom bisect import bisect_left\n\n"
                      + fills + "\n\n" + (PY_LAZY_SEG if lazy else PY_SEG) + "\n\n" + doc + "class Tree:\n" + ctor + "\n"
                      + "\n".join(py_ops) + "\n" + shape.py_shape_methods())

    doc = class_doc("//", kind, sig, how)
    doc = doc.replace("Tree<long long> tree(", "Tree tree(")
    if kind == "Nodes":
        doc = must(doc, "vector<T> (T = long long, or int), vals[node]", "vector<NodeVal>, vals[node]")
    elif kind == "Edges":
        doc = must(doc, "// T is the type the weights are kept in (long long, or int).\n",
                   "// A weight is read from its edge's third number and kept as an EdgeVal.\n")
    else:
        doc = must(doc, "vector<T> (T = long long, or int; the weights are kept as T too), vals[node]", "vector<NodeVal>, vals[node]")
        doc = must(doc, "// root: the root node (required), e.g. 0 or 1.\n",
                   "//        A weight is read from its edge's third number and kept as an EdgeVal.\n"
                   "// root: the root node (required), e.g. 0 or 1.\n")
    fills = "\n".join(cpp_fill(t, rev, lazy, level) for t in targets)
    members, build = "", ""
    if "node" in targets:
        members += "    NodeSeg nodeSeg;  // each node's data, at its position\n"
        build += ("        if ((int)vals.size() != hi + 1)\n"
                  '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                  "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                  "        vector<NodeData> nodeData(n);\n"
                  "        for (int i = 0; i < n; i++) nodeData[i] = nodeLeaf(vals[order[i]], order[i]);\n"
                  "        nodeSeg.build(nodeData);\n")
    if "edge" in targets:
        members += ("    // each edge's data: the edge above the node at position p is item p - 1 (position 0 is the root: no edge)\n"
                    "    EdgeSeg edgeSeg;\n")
        build += ("        for (const auto& e : edges)\n"
                  '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                  "        vector<EdgeVal> above(hi + 1);  // above[v]: the weight of the edge above v (the root has none)\n"
                  "        for (const auto& e : edges) {\n            int a = (int)e[0], b = (int)e[1];\n"
                  "            above[par[a] == b ? a : b] = (EdgeVal)e[2];\n        }\n"
                  "        vector<EdgeData> edgeData(n - 1);\n"
                  "        for (int i = 1; i < n; i++) edgeData[i - 1] = edgeLeaf(above[order[i]], par[order[i]], order[i]);\n"
                  "        edgeSeg.build(edgeData);\n")
    bad = {"Nodes": "vals has the wrong length", "Edges": "an edge has no weight",
           "Both": "vals has the wrong length or an edge has no weight"}[kind]
    args = "const vector<vector<E>>& edges, int root" + ("" if kind == "Edges" else ", const vector<NodeVal>& vals")
    ctor = (note("//", "O(n) -- builds the layout and the segment tree" + ("s" if kind == "Both" else "") + "; throws "
                 f"invalid_argument when the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4)
            + "\n    template <typename E = int>\n"
            + f"    Tree({args}) : root(root) {{\n" + shape.cpp_layout_body().rstrip("\n") + "\n\n" + build + "    }\n")
    segs = "\n".join(cpp_seg(t, lazy) for t in targets)
    return file, (f"// Template by https://github.com/ishaanbuildsthings\n// {URL}/{file}\n"
                  "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n"
                  + shape.FAST_NOTE + shape.PRELUDE + FILL_NOTE + "\n" + fills + "\n"
                  + segs + "\n" + doc + "struct Tree {\n" + shape.cpp_members() + members
                  + "\n" + ctor + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")


def sources():
    out = {}
    for kind in KINDS:
        for lazy in (False, True):
            for rev in (False, True):
                file, text = make(kind, lazy, rev, "basic", "py")
                out[file] = shape.tidy(text, file)
                for level in LEVELS:
                    file, text = make(kind, lazy, rev, level, "cpp")
                    out[file] = shape.tidy(text, file)
    return out


def main():
    check = "--check" in sys.argv
    made, stale = sources(), []
    for rel, text in made.items():
        path = os.path.join(DIR, rel)
        if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
            continue
        stale.append(rel)
        if not check:
            os.makedirs(DIR, exist_ok=True)
            open(path, "w", encoding="utf-8").write(text)
    extra = sorted(set(os.listdir(DIR)) - set(made) - {"__pycache__"}) if os.path.isdir(DIR) else []
    if check:
        for rel in stale:
            print(f"FAIL  generic-trees/{rel}: differs from what gen_tree_generic.py writes (rerun it)")
        for rel in extra:
            print(f"FAIL  generic-trees/{rel}: not a file gen_tree_generic.py writes")
        print(f"{len(stale) + len(extra)} stale generic tree files" if stale or extra else "generic tree templates are fresh")
        sys.exit(1 if stale or extra else 0)
    print(f"{len(made)} generic tree files, {len(stale)} written" + (f"; not written by this: {extra}" if extra else ""))


if __name__ == "__main__":
    main()
