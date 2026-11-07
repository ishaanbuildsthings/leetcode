"""Sparse (dynamic) versions of the 32-variant lazy-tree family: sparse.py + sparse.cpp per folder.

    python3 sparse_lazy.py

Same variants as gen_lazy_family.py (node fields from {sum, min, max}, tags from {add, assign, chmin, chmax}),
over any index range [lo, hi] where every position starts at 0. A recursive dynamic tree:
  - node 0 is the shared all-zeros block (sum, min and max of any block of zeros are 0), so a missing child
    needs no special case in a pull;
  - updates push a node's tag into its children (creating them) before recursing past it; queries never push:
    they carry the tags of the ancestors down and apply them to whatever they return, so they create nothing;
  - add-only variants never push at all (adds commute): a node's own add stays folded into its aggregate.
C++: nodes in one pool shared by every tree of the type (resetPool() between test cases).
Python: parallel lists (node 0 = zeros, node 1 = root); a tag is a tuple, None for no tag.
"""
import os

from note_lang import write_template
import sys

sys.dont_write_bytecode = True
from lazy_common import DIR, FIELD_ARR, FIELD_OP, class_name, describe, ops_of, tag_arrays, variants  # noqa: E402

FN = {"min": "min", "max": "max"}


def header(cm, kind, fields, tags):
    ops = ops_of(kind, fields, tags)
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: lazy-seg-tree", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: log(U)" for o in ops] + [f"{cm}   build: 1"]
    node = " ".join(f"{FIELD_ARR[f]}[4*log(U)]" for f in fields)
    tagm = " ".join(f"{t}[4*log(U)]" for t in tag_arrays(kind, tags) if t != "hasAsg") + (
        " hasAsg[4*log(U)]" if "assign" in tags and kind == "sum" else "")
    comm = commutes(kind, tags)
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: {tagm}",
              f"{cm}   other: children[8*log(U)]",
              f"{cm}   note: per update, the nodes it visits (at most 4 per level{'' if comm else ', counting the children a push creates'}); "
              f"queries create nothing. C++: one shared node pool (node 0 = all zeros), call resetPool() between test "
              f"cases; Python: parallel lists"]
    return "\n".join(lines) + "\n"


def commutes(kind, tags):
    return (kind == "clamp" and tags == "C") or (kind == "sum" and tags == "add")


# ================================================================================================ C++

def cpp(kind, fields, tags):
    name = "Sparse" + class_name(kind, fields, tags)
    comm = commutes(kind, tags)
    has_sum = "sum" in fields
    agg_fields = (["S sm;"] if has_sum else []) + [f"T {FIELD_ARR[f]};" for f in fields if f != "sum"]
    first = FIELD_ARR[fields[0]]
    merge = ", ".join(("a.sm + b.sm" if f == "sum" else f"std::{FN[f]}(a.{FIELD_ARR[f]}, b.{FIELD_ARR[f]})") for f in fields)
    leaf = ", ".join("S(v)" if f == "sum" else "v" for f in fields)
    minmax = [FIELD_ARR[f] for f in fields if f != "sum"]

    if kind == "clamp":
        A, B, C = "A" in tags, "B" in tags, "C" in tags
        tf = [n for n, on in (("hi", A), ("lo", B), ("c", C)) if on]
        tag_struct = "struct Tag { " + " ".join(f"T {n};" for n in tf) + " };  // x -> " + {
            "C": "x + c", "A": "min(hi, x)", "B": "max(lo, x)", "AB": "min(hi, max(lo, x))", "AC": "min(hi, x + c)",
            "BC": "max(lo, x + c)", "ABC": "min(hi, max(lo, x + c))"}[tags]
        ident = "Tag{" + ", ".join({"hi": "INF", "lo": "NEG", "c": "0"}[n] for n in tf) + "}"
        is_id = " && ".join({"hi": "t.hi == INF", "lo": "t.lo == NEG", "c": "t.c == 0"}[n] for n in tf)
        val = []
        if C: val.append("v += t.c;")
        if B: val.append("v = std::max(v, t.lo);")
        if A: val.append("v = std::min(v, t.hi);")
        val_fn = f"    static T val(T v, const Tag& t) {{ {' '.join(val)} return v; }}\n"
        apply_body = "".join(f"        v.{a} = val(v.{a}, t);\n" for a in minmax)
        comp = []
        if A:
            comp.append(f"T h = {'o.hi == INF ? INF : o.hi + t.c' if C else 'o.hi'};")
            comp.append(f"h = std::min(t.hi, {'std::max(t.lo, h)' if B else 'h'});")
        if B:
            comp.append(f"T l = std::max(t.lo, {'o.lo == NEG ? NEG : o.lo + t.c' if C else 'o.lo'});")
            if A: comp.append("l = std::min(l, h);")
        comp_ret = "Tag{" + ", ".join({"hi": "h", "lo": "l", "c": "o.c + t.c"}[n] for n in tf) + "}"
        compose = f"""    // tag o, then tag t; these maps compose into the same form
    static Tag compose(const Tag& o, const Tag& t) {{
{"".join(f"        {c}{chr(10)}" for c in comp)}        return {comp_ret};
    }}
"""
        mk = lambda h, l, c: "Tag{" + ", ".join({"hi": h, "lo": l, "c": c}[n] for n in tf) + "}"  # noqa: E731
        upd = []
        if C: upd.append(("rangeAdd", "a[i] += v", mk("INF", "NEG", "v")))
        if A: upd.append(("rangeChmin", "a[i] = min(a[i], v)", mk("v", "NEG", "0")))
        if B: upd.append(("rangeChmax", "a[i] = max(a[i], v)", mk("INF", "v", "0")))
        if A and B: upd.append(("rangeAssign", "a[i] = v", mk("v", "v", "0")))
        acc_field = "c"
        intro = ("The tag is the map x -> " + tag_struct.split("// x -> ")[1] + "; these maps compose into the same form, "
                 "and each\n// is monotone, so it sends a node's min / max straight to the new min / max.")
        consts = "    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n"
    else:
        ADD, ASG = "add" in tags, "assign" in tags
        tf = (["asg"] if ASG else []) + (["add"] if ADD else []) + (["has"] if ASG else [])
        tag_struct = "struct Tag { " + " ".join(("bool has;" if n == "has" else f"T {n};") for n in tf) + " };" + (
            "  // has: assign asg (later adds fold into it); else add" if ADD and ASG else "")
        ident = "Tag{" + ", ".join({"asg": "0", "add": "0", "has": "false"}[n] for n in tf) + "}"
        is_id = " && ".join({"asg": "true", "add": "t.add == 0", "has": "!t.has"}[n] for n in tf if n != "asg")
        val_fn = ""
        if ASG and ADD:
            apply_body = ("        if (t.has) {\n            v.sm = S(t.asg) * k;\n" + "".join(f"            v.{a} = t.asg;\n" for a in minmax)
                          + "        } else {\n            v.sm += S(t.add) * k;\n" + "".join(f"            v.{a} += t.add;\n" for a in minmax) + "        }\n")
            compose = """    // tag o, then tag t
    static Tag compose(const Tag& o, const Tag& t) {
        if (t.has) return t;
        if (o.has) return Tag{o.asg + t.add, 0, true};
        return Tag{0, o.add + t.add, false};
    }
"""
        elif ASG:
            apply_body = ("        if (t.has) {\n            v.sm = S(t.asg) * k;\n" + "".join(f"            v.{a} = t.asg;\n" for a in minmax) + "        }\n")
            compose = "    // tag o, then tag t\n    static Tag compose(const Tag& o, const Tag& t) { return t.has ? t : o; }\n"
        else:
            apply_body = "        v.sm += S(t.add) * k;\n" + "".join(f"        v.{a} += t.add;\n" for a in minmax)
            compose = "    // tag o, then tag t\n    static Tag compose(const Tag& o, const Tag& t) { return Tag{o.add + t.add}; }\n"
        mk_add = "Tag{" + ", ".join({"asg": "0", "add": "v", "has": "false"}[n] for n in tf) + "}"
        mk_asg = "Tag{" + ", ".join({"asg": "v", "add": "0", "has": "true"}[n] for n in tf) + "}"
        upd = ([("rangeAdd", "a[i] += v", mk_add)] if ADD else []) + ([("rangeAssign", "a[i] = v", mk_asg)] if ASG else [])
        acc_field = "add"
        intro = {"add": "The tag is a pending add.", "assign": "The tag is a pending assign.",
                 "add+assign": "The tag is a pending assign or add (an add on an assigned node shifts the assigned value)."}[tags]
        consts = ""
    uses_k = kind == "sum"
    k_param = "long long k, " if uses_k else "long long, "
    if comm:
        how = ("Adds commute, so nothing is ever pushed: a node's own add stays folded into its aggregate, and\n"
               "// queries and point writes add up the adds of the ancestors on the way down.")
        push_fn = ""
        pull_extra = "\n        v = applyTag(v, k, pool[x].t);  // the node's own add, never pushed"
    else:
        how = ("Updates push a node's tag into its children (creating them) before recursing past it; queries never push:\n"
               "// they carry the ancestors' tags down and apply them to what they return, so they create no nodes.")
        push_fn = """
    // move x's tag (x covers [a, b]) into its children, creating them
    void push(int x, long long a, long long b) {
        if (isId(pool[x].t)) return;
        Tag t = pool[x].t;
        long long m = a + (b - a) / 2;
        applyNode(kid(x, false), m - a + 1, t);
        applyNode(kid(x, true), b - m, t);
        pool[x].t = ID;
    }
"""
    upd_text = "".join(f"\n    // O(logU) -- {d} for i in [l, r]\n    void {m}(long long l, long long r, T v) {{\n"
                       f"        if (l <= r) update(root, lo, hi, l, r, {t});\n    }}\n" for m, d, t in upd)
    queries = ""
    for f in fields:
        a = FIELD_ARR[f]
        rt = "S" if f == "sum" else "T"
        desc = "a[l] + ... + a[r]" if f == "sum" else f"{f} of a[l..r]"
        queries += f"\n    // O(logU) -- {desc}\n    {rt} {FIELD_OP[f]}(long long l, long long r) const {{ return query(root, lo, hi, l, r, ID).{a}; }}\n"
    d = describe(kind, fields, tags)
    walk_push = "            push(y, a, b);\n" if not comm else f"            acc += pool[y].t.{acc_field};\n"
    return f'''
// {d[0].upper() + d[1:]}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// {intro}
// {how}
// Sparse: nodes exist only where updates reached, in one pool shared by every {name}<T>; node 0 is the shared
// all-zeros block (its sum, min and max are 0 at any length). T: int, long long, ...{"; sums are kept in S" if has_sum else ""}
template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
{consts}    struct Agg {{ {" ".join(agg_fields)} }};
    {tag_struct}
    static constexpr Tag ID = {ident};
    struct Node {{ Agg v; Tag t; int l, r; }};
    static inline vector<Node> pool{{Node{{Agg{{}}, ID, 0, 0}}}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    {name}(long long lo, long long hi) : lo(lo), hi(hi) {{ root = make(); }}

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{Agg{{}}, ID, 0, 0}});
        return (int)pool.size() - 1;
    }}

    // child of x, creating it (as a block of zeros) if missing
    static int kid(int x, bool right) {{
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {{
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }}
        return y;
    }}

    static bool isId(const Tag& t) {{ return {is_id}; }}
{val_fn}{compose}
    // the aggregate of k slots after tag t
    static Agg applyTag(Agg v, {k_param}const Tag& t) {{
{apply_body}        return v;
    }}

    static Agg merge(const Agg& a, const Agg& b) {{ return Agg{{{merge}}}; }}

    // node x (k slots) takes tag t: its aggregate now, its children later
    void applyNode(int x, long long k, const Tag& t) {{
        pool[x].v = applyTag(pool[x].v, k, t);
        pool[x].t = compose(pool[x].t, t);
    }}
{push_fn}
    void pull(int x, long long k) {{
        Agg v = merge(pool[pool[x].l].v, pool[pool[x].r].v);{pull_extra if comm else ""}
        pool[x].v = v;{"" if comm else chr(10) + "        (void)k;"}
    }}

    void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {{
        if (l <= a && b <= r) {{ applyNode(x, b - a + 1, t); return; }}
{"" if comm else "        push(x, a, b);" + chr(10)}        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
        pull(x, b - a + 1);
    }}

    // aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with t, the ancestors' pending tags, on top
    Agg query(int x, long long a, long long b, long long l, long long r, const Tag& t) const {{
        if (!x) return applyTag(Agg{{}}, std::min(r, b) - std::max(l, a) + 1, t);
        if (l <= a && b <= r) return applyTag(pool[x].v, b - a + 1, t);
        Tag down = compose(pool[x].t, t);
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r, down);
        if (l > m) return query(pool[x].r, m + 1, b, l, r, down);
        return merge(query(pool[x].l, a, m, l, r, down), query(pool[x].r, m + 1, b, l, r, down));
    }}
{upd_text}{queries}
    // O(logU) -- a[i]
    T pointGet(long long i) const {{ return T(query(root, lo, hi, i, i, ID).{first}); }}

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        int path[130], d = 0, y = root;
        long long len[130], a = lo, b = hi;{chr(10) + "        T acc = 0;  // the adds above i" if comm else ""}
        while (a < b) {{
{walk_push}            path[d] = y, len[d++] = b - a + 1;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }}
        {"v -= acc;" + chr(10) + "        " if comm else ""}pool[y].v = Agg{{{leaf}}};
        while (d--) pull(path[d], len[d]);
    }}

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) {{ pointAssign(i, pointGet(i) + delta); }}

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {{ if (v > pointGet(i)) pointAssign(i, v); }}

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {{ if (v < pointGet(i)) pointAssign(i, v); }}
}};
'''


# ================================================================================================ Python

PY_CLAMP = '''
INF = float("inf")
NEG = float("-inf")


def _val(v, t):  # v after the tag t = (hi, lo, add): min(hi, max(lo, v + add))
    if t is None:
        return v
    v += t[2]
    if v < t[1]:
        v = t[1]
    return t[0] if v > t[0] else v


def _compose(o, t):  # tag o, then tag t; the maps compose into the same form
    if o is None:
        return t
    if t is None:
        return o
    h = min(t[0], max(t[1], o[0] + t[2]))
    return h, min(max(t[1], o[1] + t[2]), h), o[2] + t[2]
'''

PY_SUM = '''

def _val(v, t):  # one slot after the tag t = (assigned value or None, add)
    if t is None:
        return v
    return t[0] if t[0] is not None else v + t[1]


def _sum(s, k, t):  # the sum s of k slots after the tag t
    if t is None:
        return s
    return t[0] * k if t[0] is not None else s + t[1] * k


def _compose(o, t):  # tag o, then tag t (an add on an assign shifts the assigned value)
    if o is None:
        return t
    if t is None or t[0] is not None:
        return o if t is None else t
    if o[0] is not None:
        return o[0] + t[1], 0
    return None, o[1] + t[1]
'''


def py(kind, fields, tags):
    name = "Sparse" + class_name(kind, fields, tags)
    comm = commutes(kind, tags)
    arrs = [FIELD_ARR[f] for f in fields]
    lists = ["L", "R"] + arrs + ["tg"]
    if kind == "clamp":
        A, B, C = "A" in tags, "B" in tags, "C" in tags
        upd = []
        if C: upd.append(("rangeAdd", "a[i] += v", "(INF, NEG, v)"))
        if A: upd.append(("rangeChmin", "a[i] = min(a[i], v)", "(v, NEG, 0)"))
        if B: upd.append(("rangeChmax", "a[i] = max(a[i], v)", "(INF, v, 0)"))
        if A and B: upd.append(("rangeAssign", "a[i] = v", "(v, v, 0)"))
        pre, acc_idx = PY_CLAMP, 2
        intro = "A tag is the map x -> min(hi, max(lo, x + add)), kept as (hi, lo, add); these maps compose into the same form,\n# and each is monotone, so it sends a node's min / max straight to the new min / max."
    else:
        upd = ([("rangeAdd", "a[i] += v", "(None, v)")] if "add" in tags else []) + (
            [("rangeAssign", "a[i] = v", "(v, 0)")] if "assign" in tags else [])
        pre, acc_idx = PY_SUM, 1
        intro = "A tag is (assigned value or None, add): an assign, or an add (an add on an assigned node shifts the value)."

    def apply_field(f, x, k, t):
        a = FIELD_ARR[f]
        return f"{a}[{x}] = _sum({a}[{x}], {k}, {t})" if f == "sum" else f"{a}[{x}] = _val({a}[{x}], {t})"

    # assemble pull
    pull = []
    for f in fields:
        a = FIELD_ARR[f]
        if f == "sum":
            pull.append(f"        v = sm[l] + sm[r]")
            pull.append(f"        sm[x] = _sum(v, k, t)" if comm else f"        sm[x] = v")
        else:
            cmp = "<" if f == "min" else ">"
            pull.append(f"        u, w = {a}[l], {a}[r]")
            pull.append(f"        {a}[x] = _val(u if u {cmp} w else w, t)" if comm else f"        {a}[x] = u if u {cmp} w else w")
    upd_text = "".join(f'''
    # O(logU) -- {d} for i in [l, r]
    def {m}(self, l, r, v):
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, {t})
''' for m, d, t in upd)
    queries = ""
    for f in fields:
        a = FIELD_ARR[f]
        op = FIELD_OP[f]
        if f == "sum":
            zero = "_sum(0, (r if r < b else b) - (l if l > a else a) + 1, t)"
            cover = "_sum(sm[x], b - a + 1, t)"
            comb = "self._q{F}(L[x], a, m, l, r, d) + self._q{F}(R[x], m + 1, b, l, r, d)"
        else:
            zero = "_val(0, t)"
            cover = f"_val({a}[x], t)"
            comb = (f"{f}(self._q{{F}}(L[x], a, m, l, r, d), self._q{{F}}(R[x], m + 1, b, l, r, d))")
        F = op[5:]
        desc = "a[l] + ... + a[r]" if f == "sum" else f"{f} of a[l..r]"
        queries += f'''
    # {desc.split(" of")[0] if f != "sum" else "sum"} of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _q{F}(self, x, a, b, l, r, t):
        if not x:
            return {zero}
        {a} = self.{a}
        if l <= a and b <= r:
            return {cover}
        L, R = self.L, self.R
        d = _compose(self.tg[x], t)
        m = (a + b) // 2
        if r <= m:
            return self._q{F}(L[x], a, m, l, r, d)
        if l > m:
            return self._q{F}(R[x], m + 1, b, l, r, d)
        return {comb.format(F=F)}

    # O(logU) -- {desc}
    def {op}(self, l, r):
        return self._q{F}(1, self.lo, self.hi, l, r, None)
'''
    first_q = "_q" + FIELD_OP[fields[0]][5:]
    if comm:
        how = "Adds commute, so nothing is ever pushed: a node's own add stays folded into its aggregate, and queries and\n# point writes add up the adds of the ancestors on the way down."
        push = ""
        walk = f"            t = tg[x]\n            if t is not None:\n                acc += t[{acc_idx}]\n"
    else:
        how = "Updates push a node's tag into its children (creating them) before recursing past it; queries never push: they\n# carry the ancestors' tags down and apply them to what they return, so they create no nodes."
        push = '''
    # move x's tag (x covers [a, b]) into its children, creating them
    def _push(self, x, a, b):
        t = self.tg[x]
        if t is not None:
            m = (a + b) // 2
            self._apply(self._kid(x, 0), m - a + 1, t)
            self._apply(self._kid(x, 1), b - m, t)
            self.tg[x] = None
'''
        walk = "            self._push(x, a, b)\n"
    d = describe(kind, fields, tags)
    return pre + f'''

# {d[0].upper() + d[1:]}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# {intro}
# {how}
# Sparse: parallel lists of nodes; node 0 is the shared all-zeros block (its sum, min and max are 0 at any
# length), node 1 is the root.


class {name}:
    __slots__ = ("lo", "hi", {", ".join(f'"{n}"' for n in lists)})

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
{"".join(f"        self.{n} = [0, 0]{chr(10)}" for n in lists[:-1])}        self.tg = [None, None]  # pending tag of each node (None: none)

    def _kid(self, x, right):  # child of x, created as a block of zeros if missing
        kids = self.R if right else self.L
        y = kids[x]
        if not y:
            y = len(self.L)
{"".join(f"            self.{n}.append(0){chr(10)}" for n in lists[:-1])}            self.tg.append(None)
            kids[x] = y
        return y

    # node x (k slots) takes tag t: its aggregate now, its children later
    def _apply(self, x, k, t):
        {", ".join(arrs)} = {", ".join(f"self.{a}" for a in arrs)}
{"".join(f"        {apply_field(f, 'x', 'k', 't')}{chr(10)}" for f in fields)}        self.tg[x] = _compose(self.tg[x], t)
{push}
    def _pull(self, x, k):
        {", ".join(arrs)} = {", ".join(f"self.{a}" for a in arrs)}
        l, r = self.L[x], self.R[x]{chr(10) + "        t = self.tg[x]  # the node's own add, never pushed" if comm else ""}
{chr(10).join(pull)}

    def _update(self, x, a, b, l, r, t):
        if l <= a and b <= r:
            self._apply(x, b - a + 1, t)
            return
{"" if comm else "        self._push(x, a, b)" + chr(10)}        m = (a + b) // 2
        if l <= m:
            self._update(self._kid(x, 0), a, m, l, r, t)
        if r > m:
            self._update(self._kid(x, 1), m + 1, b, l, r, t)
        self._pull(x, b - a + 1)
{upd_text}{queries}
    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.{first_q}(1, self.lo, self.hi, i, i, None)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        path = []
        x, a, b = 1, self.lo, self.hi{chr(10) + "        tg = self.tg" + chr(10) + "        acc = 0  # the adds above i" if comm else ""}
        while a < b:
{walk}            path.append((x, b - a + 1))
            m = (a + b) // 2
            if i <= m:
                x, b = self._kid(x, 0), m
            else:
                x, a = self._kid(x, 1), m + 1
{"        val -= acc" + chr(10) if comm else ""}{"".join(f"        self.{a}[x] = val{chr(10)}" for a in arrs)}        for y, k in reversed(path):
            self._pull(y, k)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''


if __name__ == "__main__":
    for kind, fields, tags in variants():
        folder = "-".join(ops_of(kind, fields, tags))
        path = os.path.join(DIR, folder)
        assert os.path.isdir(path), folder
        write_template(os.path.join(path, "sparse.py"), header("#", kind, fields, tags) + py(kind, fields, tags))
        write_template(os.path.join(path, "sparse.cpp"), header("//", kind, fields, tags) + cpp(kind, fields, tags))
    print(len(variants()), "sparse lazy templates written")
