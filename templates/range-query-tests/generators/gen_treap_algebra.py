"""Implicit treaps with composable aggregates: one template per (aggregates, range updates, reverse, cut / paste) a
treap can keep, each carrying only the arrays its ops need.

    python3 gen_treap_algebra.py

Aggregates (each a module: its node arrays, how a node combines its children, what a reverse and each range update do
to it, and its queries):
    sum      rangeSum
    min/max  rangeMin / rangeMax, and the leftmost / rightmost Gt / Gte / Lt / Lte searches they prune
    hash     rangeHash / rangeHashReversed / isPalindrome / rangesEqual (mod 2^61 - 1, random base and offset)
    pre/suf/best  maxPrefixSum (+ leftmostPrefixSumGt(e)X), maxSuffixSum (+ rightmostSuffixSumGt(e)X), maxSubarraySum;
             they combine through the sum, so they bring rangeSum; best needs pre and suf
    xor      rangeXorQuery          and / or   rangeAndQuery / rangeOrQuery
    gcd      rangeGcd: the gcd of the values, or (with range add) of the first value and the adjacent differences,
             which an add leaves alone
    run      longestEqualRun: first / last value, the equal run at each end, the best run
    alt      maxAltSubseqSum: best +a -b +c ... per (start sign, end sign)
Range updates, each only with the aggregates it can keep current: rangeAssign (all), rangeAdd (sum, min, max, hash,
gcd, run), rangeAddArithSeq (sum), rangeChmin / rangeChmax (min, max: one clamp tag x -> min(hi, max(lo, x + c))),
rangeAndApply / rangeOrApply (and, or: x -> (x & A) | O), rangeXorApply (xor). A pending assign is applied before a
pending add (an assign clears it). Combinations: any of sum / min / max / hash with up to two of the other families
(pre / suf / pre+suf / pre+suf+best count as one; xor, and, or, gcd, run, alt), and for three or more one cover per
update set holding every family it allows; each with each update set they allow (dominated ones left out: an update
set whose tags another set with more ops also needs), reverse or not, cut / paste or not (cut / paste treaps share one
node pool so pieces move between them).
"""
import itertools
import os
import shutil

from gen_treap import CPP_HASH_HELPERS, PY_HASH_CONST, no_push, wrap
from gen_treap_more import slots_line
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
MARK = "Implicit treap with composable aggregates"
SEQ = ["append", "appendLeft", "getAll", "insertAt", "insertCopiesAt", "moveRange", "rangeRotateLeft",
       "rangeRotateRight"]
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
PIECES = ["cut", "merge", "paste", "split", "trisect"]
SEARCH = {f"{side}{cmp}X": (side, cmp) for side in ("leftmost", "rightmost") for cmp in ("Gt", "Gte", "Lt", "Lte")}
CMP = {"Gt": ">", "Gte": ">=", "Lt": "<", "Lte": "<="}
HASH_OPS = ["isPalindrome", "rangeHash", "rangeHashReversed", "rangesEqual"]
MAXSUB = {"pre", "suf", "best"}
MS_SETS = [("pre",), ("suf",), ("pre", "suf"), ("pre", "suf", "best")]
OTHER = ["ms", "xor", "and", "or", "gcd", "run", "alt"]  # ms = one of MS_SETS
# which update families each aggregate can absorb
OK = {"sum": {"assign", "add", "ap", "shrink"}, "min": {"assign", "add", "clamp", "shrink"}, "max": {"assign", "add", "clamp", "shrink"},
      "hash": {"assign", "add", "shrink"}, "pre": {"assign", "shrink"}, "suf": {"assign", "shrink"}, "best": {"assign", "shrink"},
      "xor": {"assign", "xor", "shrink"}, "and": {"assign", "bits", "shrink"}, "or": {"assign", "bits", "shrink"},
      "gcd": {"assign", "add"}, "run": {"assign", "add", "shrink"}, "alt": {"assign", "shrink"}}
# (shrink = range mod / floor div / floor sqrt: a walk down every node whose max still changes, pulling on the way
# back, so any aggregate with a cheap pull keeps up; it needs the max to prune, and with assign the min too: a node
# whose values are all equal takes the shrink as one assign)
# update sets (op sets) per family, dominated ones left out
UPDATE_SETS = [
    ("", ()), ("assign", ("assign",)),
    ("add", ("add",)), ("add", ("add", "assign")),
    ("ap", ("add", "ap")), ("ap", ("add", "ap", "assign")),
    ("clamp", ("chmin",)), ("clamp", ("chmax",)), ("clamp", ("assign", "chmax", "chmin")),
    ("clamp", ("add", "chmin")), ("clamp", ("add", "chmax")), ("clamp", ("add", "assign", "chmax", "chmin")),
    ("bits", ("and",)), ("bits", ("or",)), ("bits", ("and", "assign", "or")),
    ("xor", ("xor",)), ("xor", ("assign", "xor")),
    ("shrink", ("div", "mod", "sqrt")), ("shrink", ("assign", "div", "mod", "sqrt")),
]
UOP = {"assign": "rangeAssign", "add": "rangeAdd", "ap": "rangeAddArithSeq", "chmin": "rangeChmin", "chmax": "rangeChmax",
       "and": "rangeAndApply", "or": "rangeOrApply", "xor": "rangeXorApply", "mod": "rangeMod", "div": "rangeFloorDiv",
       "sqrt": "rangeFloorSqrt"}
QOPS = {"sum": ["rangeSum"], "min": ["rangeMin"], "max": ["rangeMax"], "hash": HASH_OPS,
        "pre": ["leftmostPrefixSumGtX", "leftmostPrefixSumGteX", "maxPrefixSum"],
        "suf": ["maxSuffixSum", "rightmostSuffixSumGtX", "rightmostSuffixSumGteX"], "best": ["maxSubarraySum"],
        "xor": ["rangeXorQuery"], "and": ["rangeAndQuery"], "or": ["rangeOrQuery"], "gcd": ["rangeGcd"],
        "run": ["longestEqualRun"], "alt": ["maxAltSubseqSum"]}
DESC = {"sum": "its sum", "min": "its min", "max": "its max", "hash": "its forward / backward hash (and B^size)",
        "pre": "its best prefix sum", "suf": "its best suffix sum", "best": "its best subarray sum", "xor": "its xor",
        "and": "its AND", "or": "its OR", "gcd": "its gcd", "run": "its first / last value and the equal runs at its ends "
        "and inside", "alt": "its best alternating (+ - + ...) subsequence sum for each start / end sign"}


class Spec:
    def __init__(self, mods, fam, ups, rev, find=False):
        self.mods, self.fam, self.ups, self.rev, self.find = mods, fam, set(ups), rev, find
        self.ptr = True  # (every treap cuts / pastes: pieces share their source's node pool)
        m, u = set(mods), self.ups
        self.ms = MAXSUB & m
        self.clamp, self.bits, self.xorf, self.shrink = fam == "clamp", fam == "bits", fam == "xor", fam == "shrink"
        self.asgTag = "assign" in u and not self.clamp and not self.bits
        self.addTag = "add" in u and fam == "add"
        self.ap = fam == "ap"
        self.gdiff = "gcd" in m and "add" in u
        self.ends = "run" in m or self.gdiff
        self.G = "hash" in m and ("add" in u or "assign" in u)
        self.ops = sorted(set(SEQ + POINT + [UOP[x] for x in u] + (["rangeReverse"] if rev else []) + PIECES + (["find"] if find else []) +
                              [q for mod in mods for q in QOPS[mod]] +
                              [op for op, (_, c) in SEARCH.items() if ("max" if c.startswith("G") else "min") in m]))

    def has(self, *names):
        return any(n in self.mods for n in names)

    def fields(self):
        """(name, C++ type, Python node-0 value, C++ node-0 value) for every node array beyond val / sz / L / R / pri"""
        f = []
        if self.has("sum"):
            f.append(("sm", "S", "0", "0"))
        if self.has("min"):
            f.append(("mn", "T", "0", "T(0)"))
        if self.has("max"):
            f.append(("mx", "T", "0", "T(0)"))
        if self.has("hash"):
            f += [("fh", "U64", "0", "0"), ("bh", "U64", "0", "0"), ("pw", "U64", "1", "1")] + ([("gs", "U64", "0", "0")] if self.G else [])
        for x in ("pre", "suf", "best"):
            if x in self.ms:
                f.append((x, "S", "0", "0"))
        if self.has("xor"):
            f.append(("xr", "T", "0", "T(0)"))
        if self.has("and"):
            f.append(("an", "T", "-1", "~T(0)"))
        if self.has("or"):
            f.append(("orr", "T", "0", "T(0)"))
        if self.has("gcd"):
            f.append(("g", "T", "0", "T(0)"))
        if self.ends:
            f += [("fv", "T", "0", "T(0)"), ("lv", "T", "0", "T(0)")]
        if self.has("run"):
            f += [("pr", "int", "0", "0"), ("sr", "int", "0", "0"), ("br", "int", "0", "0")]
        if self.has("alt"):
            f += [(a, "S", "0", "0") for a in ("a00", "a01", "a10", "a11")]
        if self.find:
            f.append(("par", "int", "0", "0"))
        return f

    def tags(self):
        """(name, C++ type, Python identity, C++ identity)"""
        t = [("rev", "char", "0", "0")] if self.rev else []
        if self.asgTag:
            t += [("asg", "T", "0", "T(0)"), ("hasAsg", "char", "0", "0")]
        if self.addTag:
            t.append(("add", "T", "0", "T(0)"))
        if self.ap:
            t += [("as_", "T", "0", "T(0)"), ("ad", "T", "0", "T(0)")]
        if self.clamp:
            if "chmin" in self.ups or "assign" in self.ups:
                t.append(("hi", "T", "INF", "INF"))
            if "chmax" in self.ups or "assign" in self.ups:
                t.append(("lo", "T", "NEG", "NEG"))
            if "add" in self.ups:
                t.append(("c", "T", "0", "T(0)"))
        if self.bits:
            if "and" in self.ups or "assign" in self.ups:
                t.append(("tA", "T", "-1", "~T(0)"))
            if "or" in self.ups or "assign" in self.ups:
                t.append(("tO", "T", "0", "T(0)"))
        if self.xorf:
            t.append(("tx", "T", "0", "T(0)"))
        return t

    def name(self):
        mods = "-".join(self.mods) or "plain"
        ups = "-".join(sorted(self.ups))
        return "treap-" + mods + (f"-updates-{ups}" if ups else "") + ("-rev" if self.rev else "") + ("-find" if self.find else "")


def allowed(mods):
    """the update sets a treap keeping mods can take"""
    out = []
    for fam, ups in UPDATE_SETS:
        if fam and any(fam not in OK[m] for m in mods):
            continue
        if "assign" in ups and any("assign" not in OK[m] for m in mods):
            continue
        if fam == "shrink" and ("max" not in mods or ("assign" in ups and "min" not in mods)):
            continue  # (the walk prunes by the max; with assign, a node whose min == max takes it as one assign)
        out.append((fam, ups))
    return out


def mod_sets():
    """every aggregate set a template is written for: sum / min / max / hash with up to two other families (a maxsub
    piece set counts as one), then for each update set the largest set it allows (it covers any three or more)"""
    seen = []
    for k in range(4):
        for core in itertools.combinations(("sum", "min", "max"), k):
            for H in (False, True):
                base = core + (("hash",) if H else ())
                for j in range(3):
                    for ex in itertools.combinations(OTHER, j):
                        groups = [g for g in ex if g != "ms"]
                        for ms in (MS_SETS if "ms" in ex else [()]):
                            if ms and "sum" not in core:
                                continue  # (the prefix / suffix pieces combine through the sum: those come with sum)
                            seen.append((base + ms + tuple(groups), False))
                for fam, ups in UPDATE_SETS:  # (the cover: every other family this update set allows)
                    ex = [g for g in OTHER if g != "ms" and fam in OK[g] | {""} and ("assign" not in ups or "assign" in OK[g])]
                    ms = ("pre", "suf", "best") if "sum" in core and (not fam or fam in OK["pre"]) else ()
                    if len(ex) + bool(ms) > 2:
                        seen.append((base + ms + tuple(ex), (fam, ups)))
    return seen


def variants():
    out, have = [], set()
    for mods, only in mod_sets():
        for fam, ups in allowed(mods):
            if only and only != (fam, ups):
                continue
            for rev in (False, True):
                if rev and MAXSUB & set(mods) and not {"pre", "suf"} <= set(mods):
                    continue  # a reverse swaps prefix and suffix: it needs both
                key = (mods, tuple(sorted(ups)), rev)
                if key not in have:
                    have.add(key)
                    out.append(Spec(mods, fam, ups, rev))
    # find(x): a parent per node and a map value -> node. Only without range updates (each would rewrite the map entry
    # of every value it changes), and with sum / min / max / hash only
    for k in range(5):
        for mods in itertools.combinations(("sum", "min", "max", "hash"), k):
            for rev in (False, True):
                out.append(Spec(mods, "", (), rev, find=True))
    return out


# ================================================================================================ shared text

def header(cm, s):
    fields, tags = s.fields(), s.tags()
    lines = [f"@operations: {' '.join(s.ops)}", "@data-structure-type: treap", "@complexities:"]
    g = s.has("gcd")  # (a pull pays a gcd: every op that splits / merges, i.e. all but pointGet and getAll)
    lines += [f"  {op}: {SHRINK_COST[op] if op in SHRINK_COST else 'N' if op == 'getAll' else 'log(N)*log(U) expected ?' if g and op != 'pointGet' else 'log(N) expected'}"
              for op in s.ops] + [f"  build: {'N*log(U) ?' if g else 'N'}", "@memory:", "  layout: none"]
    lines += ["  node: " + " ".join(f"{f}[1*N]" for f in ["val", "sz", "L", "R", "pri"] + [f[0] for f in fields]),
              "  tags: " + (" ".join(f"{t[0]}[1*N]" for t in tags) or "none"), "  other: " + ("where[1*N]" if s.find else "none"),
              "  note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)" +
              "; every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)" +
              ("; find: a parent per node and a map value -> node" if s.find else "")]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(s):
    keeps = ", ".join(DESC[m] for m in s.mods)
    ups = ", ".join(UOP[u] for u in sorted(s.ups))
    return (f"{MARK}: an array you can insert into anywhere, " + ("reverse, " if s.rev else "") + "rotate, move" +
            ", cut pieces out of (that is how to erase) and paste them back in O(logN) expected each" + (", and find any value's index (values distinct)" if s.find else "") +
            (f", with {ups}" if ups else "") + (f"; each node keeps {keeps} over its subtree" if keeps else "") + ". All indices "
            "0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when "
            "nothing qualifies." + (" Lazy tags mean \"already applied to this node, not yet to its children\"" +
                                    ("; a pending assign comes before a pending add." if s.asgTag and (s.addTag or s.ap or s.xorf) else ".")
                                    if s.tags() else ""))



POOL_NOTE = ("one node pool shared by every {cls}: cut / paste move nodes between them, so a piece from one can go "
             "into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the "
             "whole run), so there is nothing to reset between test cases")


def py_skeleton(F, TG, extra=(), cls="ImplicitTreap", ctor=None, empty=None):
    """the class line, the node lists (class-level: every instance shares them) and the constructor. extra: (name,
    Python value) more class-level state (the find map); ctor / empty: the constructor and _empty text when they are not
    the plain (arr) ones"""
    names = [("val", "0"), ("pri", "0"), ("L", "0"), ("R", "0"), ("sz", "0")] + [(f[0], f[2]) for f in F] + [(t[0], t[2]) for t in TG]
    return (f"class {cls}:\n" + wrap(POOL_NOTE.format(cls=cls), "    #") +
            "".join(f"    {n} = [{v}]\n" for n, v in names) + "".join(f"    {n} = {v}\n" for n, v in extra) +
            (ctor or f'''    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))
''') + (empty or f'''
    def _empty(self):  # a new, empty {cls} (on the same pool, like every one)
        return {cls}()
''') + "\n")


def cpp_skeleton(F, TG, extra=(), cls="ImplicitTreap"):
    """the node arrays (static: every instance shares them) and the plain constructor. extra: (C++ type, name) more
    shared state"""
    arrays = [("T", "val", "T(0)"), ("unsigned long long", "pri", "0"), ("int", "L", "0"), ("int", "R", "0"), ("int", "sz", "0")]
    arrays += [(f[1], f[0], f[3]) for f in F] + [(t[1], t[0], t[3]) for t in TG]
    return (wrap(POOL_NOTE.format(cls=cls + "<T>"), "    //") + "".join(f"    static inline vector<{t}> {n}{{{v}}};\n" for t, n, v in arrays) +
            "".join(f"    static inline {t} {n};\n" for t, n in extra) + f"""    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit {cls}(const vector<T>& arr = {{}}) {{ root = build(arr); }}

    {cls} makeEmpty() const {{ return {cls}(); }}  // (a new, empty one)
""")


SAFE_HASH = '''    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
'''


# ================================================================================================ Python

def py(s):
    F, TG = s.fields(), s.tags()
    names = ["val", "pri", "L", "R", "sz"] + [f[0] for f in F] + [t[0] for t in TG]
    NEED_INF = s.clamp or s.has("alt")
    out = [header("#", s), "\n", wrap(describe(s), "#"), "import random\n" + ("from math import gcd\n" if s.has("gcd") else "") + ("from math import isqrt\n" if s.shrink else "") + "\n\n"]
    if s.has("hash"):
        out.append(PY_HASH_CONST)
    if NEED_INF:
        out.append('INF, NEG = float("inf"), float("-inf")\n\n\n')
    if s.has("alt"):
        out.append('''def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


''')
    out.append(py_skeleton(F, TG, [("where", "{}")] if s.find else []))
    out.append("    # O(1) -- the current length of the array\n    def size(self):\n        return self.sz[self.root]\n\n")
    pub = py_public(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append(py_internals(s))
    text = gcd_costs(s, "".join(out))
    return text if TG else no_push(text, "py")


def gcd_costs(s, text):  # with gcd every pull pays a gcd: the method comments say so (pointGet only finds)
    if not s.has("gcd"):
        return text
    text = text.replace("O(logN) expected -- ", "O(logN * logU) expected -- ").replace("O(k + logN) expected", "O(k + logN * logU) expected")
    text = text.replace("(a walk pruned by ", "(pruned by ")  # (room for the longer cost)
    return text.replace("O(logN * logU) expected -- a[i]\n", "O(logN) expected -- a[i]\n")


def py_public(s):
    pub = {}
    J = "self._join(a, b, c)"
    for mod, op, expr in (("sum", "rangeSum", "self.sm[b]"), ("min", "rangeMin", "self.mn[b]"), ("max", "rangeMax", "self.mx[b]"),
                          ("pre", "maxPrefixSum", "self.pre[b]"), ("suf", "maxSuffixSum", "self.suf[b]"),
                          ("best", "maxSubarraySum", "self.best[b]"), ("xor", "rangeXorQuery", "self.xr[b]"),
                          ("and", "rangeAndQuery", "self.an[b]"), ("or", "rangeOrQuery", "self.orr[b]"),
                          ("gcd", "rangeGcd", "gcd(self.fv[b], self.g[b])" if s.gdiff else "self.g[b]"),
                          ("run", "longestEqualRun", "self.br[b]"), ("alt", "maxAltSubseqSum", "max(self.a00[b], self.a01[b])"),
                          ("hash", "rangeHash", "self.fh[b]"), ("hash", "rangeHashReversed", "self.bh[b]"),
                          ("hash", "isPalindrome", "self.fh[b] == self.bh[b]")):
        if mod in s.mods and op in s.ops:
            pub[op] = f'''    # O(logN) expected -- {QDOC[op]}
    def {op}(self, l, r):
        a, b, c = self._cut(l, r)
        res = {expr}
        {J}
        return res
'''
    if "hash" in s.mods:
        pub["rangesEqual"] = f'''    # O(logN) expected -- {QDOC["rangesEqual"]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)
'''
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        if side == "leftmost":
            walk = f'''                if L[t] and F[L[t]] {o} x:
                    t = L[t]
                elif val[t] {o} x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]'''
        else:
            walk = f'''                if R[t] and F[R[t]] {o} x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] {o} x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]'''
        pub[op] = f'''    # O(logN) expected -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the subtree {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.{f}
        t, i, res = b, 0, -1
        if t and F[t] {o} x:  # some value in a[l..r] passes
            while True:
                self._push(t)
{walk}
        {J}
        return res
'''
    for op, field, strict in (("leftmostPrefixSumGteX", "pre", False), ("leftmostPrefixSumGtX", "pre", True),
                              ("rightmostSuffixSumGteX", "suf", False), ("rightmostSuffixSumGtX", "suf", True)):
        if op not in s.ops:
            continue
        o = ">" if strict else ">="
        if field == "pre":
            doc = f"first i in [l, r] with a[l] + ... + a[i] {o} x, or -1 (a walk pruned by best prefix sums)"
            walk = f'''                lt = L[t]
                if lt and acc + P[lt] {o} x:
                    t = lt
                    continue
                acc += sm[lt]
                if acc + val[t] {o} x:
                    res = l + i + sz[lt]
                    break
                acc += val[t]
                i += sz[lt] + 1
                t = R[t]'''
        else:
            doc = f"last i in [l, r] with a[i] + ... + a[r] {o} x, or -1 (a walk pruned by best suffix sums)"
            walk = f'''                rt = R[t]
                if rt and acc + P[rt] {o} x:
                    i += sz[L[t]] + 1
                    t = rt
                    continue
                acc += sm[rt]
                if acc + val[t] {o} x:
                    res = l + i + sz[L[t]]
                    break
                acc += val[t]
                t = L[t]'''
        pub[op] = f'''    # O(logN) expected -- {doc}
    def {op}(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.{field}
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] {o} x:
            while True:
                self._push(t)
{walk}
        {J}
        return res
'''
    upd = {"assign": ("v", "self._applyAssign(b, v)" if s.asgTag else "self._applyClamp(b, " + clamp_args(s, "v", "v", "0") + ")" if s.clamp
                      else "self._applyBits(b, " + bits_args(s, "0", "v") + ")"),
           "add": ("v", "self._applyAP(b, v, 0)" if s.ap else "self._applyAdd(b, v)" if s.addTag else "self._applyClamp(b, " + clamp_args(s, "INF", "NEG", "v") + ")"),
           "ap": ("start, step", "self._applyAP(b, start, step)"),
           "chmin": ("v", "self._applyClamp(b, " + clamp_args(s, "v", "NEG", "0") + ")"),
           "chmax": ("v", "self._applyClamp(b, " + clamp_args(s, "INF", "v", "0") + ")"),
           "and": ("v", "self._applyBits(b, " + bits_args(s, "v", "0") + ")"),
           "or": ("v", "self._applyBits(b, " + bits_args(s, "-1", "v") + ")"),
           "xor": ("v", "self._applyXor(b, v)")}
    shr = {"mod": ("x", "if x >= 1:\n            self._shrink(b, x, lambda v: v % x)", "logN * logU"),
           "div": ("x", "if x >= 2:\n            self._shrink(b, 1, lambda v: v // x)", "logN * logU"),
           "sqrt": ("", "self._shrink(b, 2, isqrt)", "logN * loglogU")}
    for u in s.ups:
        if u in shr:
            args, call, c = shr[u]
            pub[UOP[u]] = f'''    # amortized O({c}) expected -- {UDOC[u]}
    def {UOP[u]}(self, l, r{", " + args if args else ""}):
        a, b, c = self._cut(l, r)
        {call}
        {J}
'''
            continue
        args, call = upd[u]
        pub[UOP[u]] = f'''    # O(logN) expected -- {UDOC[u]}
    def {UOP[u]}(self, l, r, {args}):
        a, b, c = self._cut(l, r)
        {call}
        {J}
'''
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self.val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(self.val[t], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(self.val[t], v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        t, path = self._find(i)
''' + ("        old = self.val[t]\n" if s.find else "") + f"        self.val[t] = {expr}\n" + ("        self._rekey(t, old)\n" if s.find else "") + (
        "        self._pull(t)\n        for x in reversed(path):\n            self._pull(x)\n" if s.mods else "")
    pub.update(PY_SEQ)
    pub.update(PY_PIECES)
    if s.find:
        pub["find"] = '''    # O(logN) expected -- the index of x, or -1 if x isn't in this treap (values distinct across all treaps)
    def find(self, x):
        t = self.where.get(x, 0)
        if not t or self.val[t] != x:
            return -1
        L, R, par, sz, path = self.L, self.R, self.par, self.sz, [t]
        while True:  # up to the root (a parent counts only while it still has the node as a child)
            c = path[-1]
            p = par[c]
            if not p or L[p] != c and R[p] != c:
                break
            path.append(p)
        if path[-1] != self.root:
            return -1  # (erased, or in another treap)
''' + ('''        for y in reversed(path):  # (pending reverses above it, applied top-down so the path reads left to right)
            self._push(y)
''' if s.tags() else "") + '''        i = sz[L[t]]
        for k in range(1, len(path)):
            if R[path[k]] == path[k - 1]:
                i += sz[L[path[k]]] + 1
        return i
'''
    return pub


def clamp_args(s, hi, lo, c):
    names = [t[0] for t in s.tags()]
    return ", ".join(v for n, v in (("hi", hi), ("lo", lo), ("c", c)) if n in names)


def bits_args(s, A, O):
    names = [t[0] for t in s.tags()]
    return ", ".join(v for n, v in (("tA", A), ("tO", O)) if n in names)


SHRINK_COST = {"rangeMod": "log(N)*log(U) amortized", "rangeFloorDiv": "log(N)*log(U) amortized",
               "rangeFloorSqrt": "log(N)*log(log(U)) amortized"}
QDOC = {"rangeSum": "a[l] + ... + a[r]", "rangeMin": "min of a[l..r]", "rangeMax": "max of a[l..r]",
        "maxPrefixSum": "max of a[l] + ... + a[i] over i in [l, r]", "maxSuffixSum": "max of a[i] + ... + a[r] over i in [l, r]",
        "maxSubarraySum": "max sum of a non-empty contiguous subarray of a[l..r]", "rangeXorQuery": "a[l] ^ ... ^ a[r]",
        "rangeAndQuery": "a[l] & ... & a[r]", "rangeOrQuery": "a[l] | ... | a[r]", "rangeGcd": "gcd of |a[l]|, ..., |a[r]|",
        "longestEqualRun": "the longest run of equal adjacent values in a[l..r]",
        "maxAltSubseqSum": "max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]",
        "rangeHash": "hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal",
        "rangeHashReversed": "hash of a[l..r] read right to left (= rangeHash of the reversed range)",
        "isPalindrome": "is a[l..r] a palindrome (its two hashes agree)",
        "rangesEqual": "are a[l1..r1] and a[l2..r2] equal (same length and hash)"}
UDOC = {"assign": "a[i] = v for i in [l, r]", "add": "a[i] += v for i in [l, r]",
        "ap": "a[l + k] += start + k * step for k in [0, r - l]", "chmin": "a[i] = min(a[i], v) for i in [l, r]",
        "chmax": "a[i] = max(a[i], v) for i in [l, r]", "and": "a[i] &= v for i in [l, r]", "or": "a[i] |= v for i in [l, r]",
        "xor": "a[i] ^= v for i in [l, r]", "mod": "a[i] %= x for i in [l, r] (values >= 0, x >= 1)",
        "div": "a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing)",
        "sqrt": "a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0)"}


def py_pull(s):
    L = ["        l, r = self.L[x], self.R[x]", "        self.sz[x] = self.sz[l] + self.sz[r] + 1"]
    if s.find:  # (a child's parent is only trusted while the parent still has it as a child: splits leave stale ones)
        L += ["        self.par[l] = self.par[r] = x"]
    if not s.mods:
        return L
    L.append("        v = self.val[x]")
    if s.ms:
        nm = ["s"] + [{"pre": "p", "suf": "q", "best": "b"}[f] for f in ("pre", "suf", "best") if f in s.ms]
        fld = {"s": "sm", "p": "pre", "q": "suf", "b": "best"}
        e = lambda A, B: {"s": f"{A}s + {B}s", "p": f"max({A}p, {A}s + {B}p)", "q": f"max({B}q, {B}s + {A}q)",  # noqa: E731
                          "b": f"max({A}b, {B}b, {A}q + {B}p)"}
        L += [f"        {', '.join(nm)} = {', '.join('v' for _ in nm)}  # the node alone, then with its left / right parts",
              "        if l:", f"            {', '.join('l' + n for n in nm)} = {', '.join(f'self.{fld[n]}[l]' for n in nm)}",
              f"            {', '.join(nm)} = {', '.join(e('l', '')[n] for n in nm)}",
              "        if r:", f"            {', '.join('r' + n for n in nm)} = {', '.join(f'self.{fld[n]}[r]' for n in nm)}",
              f"            {', '.join(nm)} = {', '.join(e('', 'r')[n] for n in nm)}",
              f"        {', '.join(f'self.{fld[n]}[x]' for n in nm)} = {', '.join(nm)}"]
    elif s.has("sum"):
        L.append("        self.sm[x] = self.sm[l] + v + self.sm[r]")
    for mod, f, c in (("min", "mn", "<"), ("max", "mx", ">")):
        if s.has(mod):
            L += ["        m = v", f"        if l and self.{f}[l] {c} m:", f"            m = self.{f}[l]",
                  f"        if r and self.{f}[r] {c} m:", f"            m = self.{f}[r]", f"        self.{f}[x] = m"]
    if s.has("hash"):  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        L += ["        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh", "        hv = (v + _HO) % P",
              "        pw[x] = pw[l] * B % P * pw[r] % P"] + (["        gs = self.gs", "        gs[x] = ((gs[l] * B + 1) * pw[r] + gs[r]) % P"] if s.G else []) + [
              "        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P", "        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P"]
    if s.has("xor"):
        L.append("        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]")
    if s.has("and"):
        L.append("        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)")
    if s.has("or"):
        L.append("        self.orr[x] = self.orr[l] | v | self.orr[r]")
    if s.has("gcd"):
        if s.gdiff:  # the gcd of the adjacent differences inside the subtree (a range add leaves them alone)
            L += ["        g = gcd(self.g[l], self.g[r])", "        if l:", "            g = gcd(g, v - self.lv[l])", "        if r:",
                  "            g = gcd(g, self.fv[r] - v)", "        self.g[x] = g"]
        else:
            L.append("        self.g[x] = gcd(gcd(self.g[l], v), self.g[r])")
    if s.has("run"):  # (prefix run, suffix run, best run): the left part joins the node, then the right part joins them
        L += ["        pr = sr = br = 1", "        if l:", "            j = self.lv[l] == v", "            pr = self.pr[l] + (1 if j and self.pr[l] == self.sz[l] else 0)",
              "            sr = self.sr[l] + 1 if j else 1", "            br = max(self.br[l], sr)", "        if r:", "            j = v == self.fv[r]",
              "            rp, rs = self.pr[r], self.sr[r]", "            br = max(br, self.br[r], sr + rp if j else 0)",
              "            if j and pr == self.sz[l] + 1:", "                pr += rp", "            sr = rs + sr if j and rs == self.sz[r] else rs",
              "        self.pr[x], self.sr[x], self.br[x] = pr, sr, br"]
    if s.ends:
        L += ["        self.fv[x] = self.fv[l] if l else v", "        self.lv[x] = self.lv[r] if r else v"]
    if s.has("alt"):
        L += ["        c = (v, NEG, NEG, -v)", "        if l:", "            c = _altJoin((self.a00[l], self.a01[l], self.a10[l], self.a11[l]), c)",
              "        if r:", "            c = _altJoin(c, (self.a00[r], self.a01[r], self.a10[r], self.a11[r]))",
              "        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = c"]
    return L


def py_new(s):
    """_newNode's lines for the module arrays (a lone node: v)"""
    L = []
    if s.has("sum"):
        L.append("        self.sm.append(v)")
    for mod, f in (("min", "mn"), ("max", "mx")):
        if s.has(mod):
            L.append(f"        self.{f}.append(v)")
    if s.has("hash"):
        L += ["        self.fh.append((v + _HO) % _HP)", "        self.bh.append((v + _HO) % _HP)", "        self.pw.append(_HB)"] + (
            ["        self.gs.append(1)"] if s.G else [])
    for f in ("pre", "suf", "best"):
        if f in s.ms:
            L.append(f"        self.{f}.append(v)")
    for mod, f in (("xor", "xr"), ("and", "an"), ("or", "orr")):
        if s.has(mod):
            L.append(f"        self.{f}.append(v)")
    if s.has("gcd"):
        L.append("        self.g.append(0)" if s.gdiff else "        self.g.append(abs(v))")
    if s.ends:
        L += ["        self.fv.append(v)", "        self.lv.append(v)"]
    if s.has("run"):
        L += ["        self.pr.append(1)", "        self.sr.append(1)", "        self.br.append(1)"]
    if s.has("alt"):
        L += ["        self.a00.append(v)", "        self.a01.append(NEG)", "        self.a10.append(NEG)", "        self.a11.append(-v)"]
    L += [f"        self.{t[0]}.append({t[2]})" for t in s.tags()]
    if s.find:
        L += ["        self.par.append(0)", "        self.where[v] = x"]
    return L


def py_internals(s):
    TG = s.tags()
    out = ['''
    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
''' + "".join(x + "\n" for x in py_new(s)) + '''        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):  # recompute x from its children
''' + "".join(x + "\n" for x in py_pull(s))]
    push = []
    if s.rev:
        rv = ["            self.L[x], self.R[x] = self.R[x], self.L[x]", "            self.rev[x] ^= 1"]
        for a, b in (("fh", "bh"), ("pre", "suf"), ("fv", "lv"), ("pr", "sr"), ("a01", "a10")):
            if a in [f[0] for f in s.fields()]:
                rv.append(f"            self.{a}[x], self.{b}[x] = self.{b}[x], self.{a}[x]")
        if s.ap:  # a pending arithmetic add read backwards: start + step * (size - 1), then -step
            rv += ["            if self.ad[x] or self.as_[x]:", "                self.as_[x] += self.ad[x] * (self.sz[x] - 1)",
                   "                self.ad[x] = -self.ad[x]"]
        out.append("\n    def _applyRev(self, x):  # reverse x's subtree\n        if x:\n" + "".join(x + "\n" for x in rv))
        push.append("        if self.rev[x]:\n            self._applyRev(self.L[x])\n            self._applyRev(self.R[x])\n            self.rev[x] = 0\n")
    fl = [f[0] for f in s.fields()]
    if s.asgTag:
        a = (["            n = self.sz[x]"] if {"sm", "pre", "suf", "best", "xr", "pr", "a00"} & set(fl) else []) + ["            self.val[x] = v"]
        if "sm" in fl:
            a.append("            self.sm[x] = v * n")
        for f in ("mn", "mx", "an", "orr"):
            if f in fl:
                a.append(f"            self.{f}[x] = v")
        if "fh" in fl:
            a.append("            self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[x] % _HP")
        ms = [f for f in ("pre", "suf", "best") if f in fl]
        if ms:
            a.append("            " + " = ".join(f"self.{f}[x]" for f in ms) + " = v * n if v > 0 else v")
        if "xr" in fl:
            a.append("            self.xr[x] = v if n & 1 else 0")
        if "g" in fl:
            a.append("            self.g[x] = 0" if s.gdiff else "            self.g[x] = abs(v)")
        if s.ends:
            a.append("            self.fv[x] = self.lv[x] = v")
        if "pr" in fl:
            a.append("            self.pr[x] = self.sr[x] = self.br[x] = n")
        if "a00" in fl:
            a += ["            self.a00[x], self.a11[x] = v, -v", "            self.a01[x] = self.a10[x] = 0 if n > 1 else NEG"]
        a += ["            self.asg[x], self.hasAsg[x] = v, 1"]
        if s.addTag:
            a.append("            self.add[x] = 0  # (an add pending below the assign is gone)")
        if s.ap:
            a.append("            self.as_[x] = self.ad[x] = 0")
        if s.xorf:
            a.append("            self.tx[x] = 0")
        out.append("\n    def _applyAssign(self, x, v):  # every value of x's subtree becomes v\n        if x:\n" + "".join(y + "\n" for y in a))
        push.append("        if self.hasAsg[x]:\n            self._applyAssign(self.L[x], self.asg[x])\n            self._applyAssign(self.R[x], self.asg[x])\n"
                    "            self.hasAsg[x] = 0\n")
    if s.addTag:
        a = ["            self.val[x] += v"]
        if "sm" in fl:
            a.append("            self.sm[x] += v * self.sz[x]")
        for f in ("mn", "mx"):
            if f in fl:
                a.append(f"            self.{f}[x] += v")
        if "fh" in fl:
            a += ["            h = v % _HP * self.gs[x] % _HP", "            self.fh[x] = (self.fh[x] + h) % _HP", "            self.bh[x] = (self.bh[x] + h) % _HP"]
        if s.ends:
            a += ["            self.fv[x] += v", "            self.lv[x] += v"]
        a.append("            self.add[x] += v")
        out.append("\n    def _applyAdd(self, x, v):  # every value of x's subtree gains v\n        if x:\n" + "".join(y + "\n" for y in a))
        push.append("        if self.add[x]:\n            self._applyAdd(self.L[x], self.add[x])\n            self._applyAdd(self.R[x], self.add[x])\n"
                    "            self.add[x] = 0\n")
    if s.ap:
        out.append('''
    def _applyAP(self, x, s, d):  # the k-th value of x's subtree (k from 0) gains s + k * d
        if x:
            self.val[x] += s + d * self.sz[self.L[x]]
''' + ("            n = self.sz[x]\n            self.sm[x] += s * n + d * (n * (n - 1) // 2)\n" if "sm" in fl else "") + '''            self.as_[x] += s
            self.ad[x] += d
''')
        push.append('''        if self.as_[x] or self.ad[x]:
            s, d = self.as_[x], self.ad[x]
            self._applyAP(self.L[x], s, d)
            self._applyAP(self.R[x], s + d * (self.sz[self.L[x]] + 1), d)
            self.as_[x] = self.ad[x] = 0
''')
    if s.clamp:
        tn = [t[0] for t in TG]
        params = [{"hi": "H", "lo": "Lo", "c": "C"}[p] for p in ("hi", "lo", "c") if p in tn]
        f = lambda e: ("min(H, " if "hi" in tn else "") + ("max(Lo, " if "lo" in tn else "") + e + (" + C" if "c" in tn else "") + (")" if "lo" in tn else "") + (")" if "hi" in tn else "")  # noqa: E731
        a = [f"            self.val[x] = {f('self.val[x]')}"] + [f"            self.{g}[x] = {f(f'self.{g}[x]')}" for g in ("mn", "mx") if g in fl]
        # compose (the old map, then this one): hi' = H(old hi), lo' = min(lo pushed through, hi'), c' = old c + C
        if "hi" in tn:
            a.append("            h = min(H, " + ("max(Lo, " if "lo" in tn else "") + "self.hi[x]" + (" + C" if "c" in tn else "") + (")" if "lo" in tn else "") + ")")
        if "lo" in tn:
            a.append("            self.lo[x] = " + ("min(" if "hi" in tn else "") + "max(Lo, self.lo[x]" + (" + C" if "c" in tn else "") + ")" +
                     (", h)" if "hi" in tn else ""))
        if "hi" in tn:
            a.append("            self.hi[x] = h")
        if "c" in tn:
            a.append("            self.c[x] += C")
        out.append(f"\n    def _applyClamp(self, x, {', '.join(params)}):  # every value v of x's subtree becomes "
                   f"{f('v')}\n        if x:\n" + "".join(y + "\n" for y in a))
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        cond = " or ".join({"hi": "self.hi[x] != INF", "lo": "self.lo[x] != NEG", "c": "self.c[x]"}[p] for p in tp)
        args = ", ".join(f"self.{p}[x]" for p in tp)
        reset = ", ".join(f"self.{p}[x]" for p in tp) + " = " + ", ".join({"hi": "INF", "lo": "NEG", "c": "0"}[p] for p in tp)
        push.append(f"        if {cond}:\n            self._applyClamp(self.L[x], {args})\n            self._applyClamp(self.R[x], {args})\n            {reset}\n")
    if s.bits:
        tn = [t[0] for t in TG]
        TA, TO = "tA" in tn, "tO" in tn
        params = ", ".join((["A"] if TA else []) + (["O"] if TO else []))
        f = lambda e: ("(" if TO else "") + e + (" & A" if TA else "") + (") | O" if TO else "")  # noqa: E731
        a = [f"            self.{g}[x] = {f(f'self.{g}[x]')}" for g in ("val", "an", "orr") if g == "val" or g in fl]
        if TA:
            a.append("            self.tA[x] &= A")
        if TO:
            a.append("            self.tO[x] = " + f("self.tO[x]"))
        out.append(f"\n    def _applyBits(self, x, {params}):  # every value v of x's subtree becomes {f('v')}\n        if x:\n" + "".join(y + "\n" for y in a))
        cond = " or ".join((["self.tA[x] != -1"] if TA else []) + (["self.tO[x]"] if TO else []))
        args = ", ".join((["self.tA[x]"] if TA else []) + (["self.tO[x]"] if TO else []))
        reset = ", ".join((["self.tA[x]"] if TA else []) + (["self.tO[x]"] if TO else [])) + " = " + ", ".join((["-1"] if TA else []) + (["0"] if TO else []))
        push.append(f"        if {cond}:\n            self._applyBits(self.L[x], {args})\n            self._applyBits(self.R[x], {args})\n            {reset}\n")
    if s.xorf:
        a = ["            self.val[x] ^= v"] + (["            if self.sz[x] & 1:", "                self.xr[x] ^= v"] if "xr" in fl else []) + ["            self.tx[x] ^= v"]
        out.append("\n    def _applyXor(self, x, v):  # every value of x's subtree is xored with v\n        if x:\n" + "".join(y + "\n" for y in a))
        push.append("        if self.tx[x]:\n            self._applyXor(self.L[x], self.tx[x])\n            self._applyXor(self.R[x], self.tx[x])\n            self.tx[x] = 0\n")
    if push:
        out.append("\n    def _push(self, x):  # hand x's pending tags to its children\n" + "".join(push))
    if s.shrink:
        out.append('''
    def _shrink(self, t, lim, f):  # every value v >= lim under t becomes f(v) (the rest are fixed)
        if not t or self.mx[t] < lim:
            return
''' + ('''        if self.mn[t] == self.mx[t]:  # all equal: one assign
            self._applyAssign(t, f(self.mx[t]))
            return
''' if s.asgTag else "") + '''        self._push(t)
        v = self.val[t]
        if v >= lim:
            self.val[t] = f(v)
        self._shrink(self.L[t], lim, f)
        self._shrink(self.R[t], lim, f)
        self._pull(t)
''')
    if s.find:
        out.append('''
    def _rekey(self, t, old):  # t's value changed from old: the map follows (find needs distinct values)
        if self.where.get(old) == t:
            del self.where[old]
        self.where[self.val[t]] = t
''')
    out.append(PY_TAIL)
    return "".join(out)


PY_SEQ = {
    "pointGet": '''    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]
''',
    "insertAt": '''    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)
''',
    "insertCopiesAt": '''    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)
''',
    "append": '''    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))
''',
    "appendLeft": '''    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)
''',
    "rangeReverse": '''    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)
''',
    "rangeRotateLeft": '''    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)
''',
    "rangeRotateRight": '''    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)
''',
    "moveRange": '''    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)
''',
    "getAll": '''    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out
''',
}

PY_PIECES = {
    "cut": '''    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece
''',
    "paste": '''    # O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0
''',
    "merge": '''    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0
''',
    "split": '''    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right
''',
    "trisect": '''    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right
''',
}

PY_TAIL = '''
    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's
        if not a or not b:
            return a or b
        if self.pri[a] > self.pri[b]:
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]
'''


# ================================================================================================ C++

def cpp(s):
    F, TG = s.fields(), s.tags()
    fl = [f[0] for f in F]
    tn = [t[0] for t in TG]
    S_ = s.has("sum") or bool(s.ms) or s.has("alt")
    out = [header("//", s), "\n", wrap(describe(s), "//"),
           "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if S_ else ""), "\ntemplate <typename T>\nstruct ImplicitTreap {\n"]
    if S_:
        out.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    if s.has("hash"):
        out.append("    using U64 = unsigned long long;\n")
    if s.clamp:
        out.append("    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n")
    if s.has("alt"):
        out.append("    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)\n")
    if s.find:
        out.append(SAFE_HASH)
    out.append(cpp_skeleton(F, TG, [("unordered_map<T, int, SafeHash>", "where")] if s.find else []))
    out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
''' + (CPP_HASH_HELPERS.replace(
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }",
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) {\n        return a + b >= HP ? a + b - HP : a + b;\n    }")
        if s.has("hash") else "") + '''
    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

''')
    pub = cpp_public(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append(cpp_internals(s))
    text = gcd_costs(s, "".join(out))
    return text if TG else no_push(text, "cpp")


def cpp_public(s):
    pub = {}
    cut = "int a, b, c;\n        cut(l, r, a, b, c);"
    J = "root = merge(merge(a, b), c);"
    for mod, op, typ, expr in (("sum", "rangeSum", "S", "sm[b]"), ("min", "rangeMin", "T", "mn[b]"), ("max", "rangeMax", "T", "mx[b]"),
                               ("pre", "maxPrefixSum", "S", "pre[b]"), ("suf", "maxSuffixSum", "S", "suf[b]"),
                               ("best", "maxSubarraySum", "S", "best[b]"), ("xor", "rangeXorQuery", "T", "xr[b]"),
                               ("and", "rangeAndQuery", "T", "an[b]"), ("or", "rangeOrQuery", "T", "orr[b]"),
                               ("gcd", "rangeGcd", "T", "gcd(fv[b], g[b])" if s.gdiff else "g[b]"),
                               ("run", "longestEqualRun", "int", "br[b]"), ("alt", "maxAltSubseqSum", "S", "max(a00[b], a01[b])"),
                               ("hash", "rangeHash", "U64", "fh[b]"), ("hash", "rangeHashReversed", "U64", "bh[b]"),
                               ("hash", "isPalindrome", "bool", "fh[b] == bh[b]")):
        if mod in s.mods and op in s.ops:
            pub[op] = f'''    // O(logN) expected -- {QDOC[op]}
    {typ} {op}(int l, int r) {{
        {cut}
        {typ} res = {expr};
        {J}
        return res;
    }}
'''
    if "hash" in s.mods:
        pub["rangesEqual"] = f'''    // O(logN) expected -- {QDOC["rangesEqual"]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }}
'''
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        if side == "leftmost":
            walk = f'''                if (L[t] && {f}[L[t]] {o} x) t = L[t];
                else if (val[t] {o} x) {{ res = l + i + sz[L[t]]; break; }}
                else i += sz[L[t]] + 1, t = R[t];'''
        else:
            walk = f'''                if (R[t] && {f}[R[t]] {o} x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] {o} x) {{ res = l + i + sz[L[t]]; break; }}
                else t = L[t];'''
        pub[op] = f'''    // O(logN) expected -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the subtree {"max" if f == "mx" else "min"})
    int {op}(int l, int r, T x) {{
        {cut}
        int t = b, i = 0, res = -1;
        if (t && {f}[t] {o} x) {{  // some value in a[l..r] passes
            while (true) {{
                push(t);
{walk}
            }}
        }}
        {J}
        return res;
    }}
'''
    for op, field, strict in (("leftmostPrefixSumGteX", "pre", False), ("leftmostPrefixSumGtX", "pre", True),
                              ("rightmostSuffixSumGteX", "suf", False), ("rightmostSuffixSumGtX", "suf", True)):
        if op not in s.ops:
            continue
        o = ">" if strict else ">="
        if field == "pre":
            doc = f"first i in [l, r] with a[l] + ... + a[i] {o} x, or -1 (a walk pruned by best prefix sums)"
            walk = f'''                int lt = L[t];
                if (lt && acc + pre[lt] {o} S(x)) {{ t = lt; continue; }}
                acc += sm[lt];
                if (acc + S(val[t]) {o} S(x)) {{ res = l + i + sz[lt]; break; }}
                acc += S(val[t]), i += sz[lt] + 1, t = R[t];'''
        else:
            doc = f"last i in [l, r] with a[i] + ... + a[r] {o} x, or -1 (a walk pruned by best suffix sums)"
            walk = f'''                int rt = R[t];
                if (rt && acc + suf[rt] {o} S(x)) {{ i += sz[L[t]] + 1, t = rt; continue; }}
                acc += sm[rt];
                if (acc + S(val[t]) {o} S(x)) {{ res = l + i + sz[L[t]]; break; }}
                acc += S(val[t]), t = L[t];'''
        pub[op] = f'''    // O(logN) expected -- {doc}
    int {op}(int l, int r, T x) {{
        {cut}
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && {field}[t] {o} S(x)) {{
            while (true) {{
                push(t);
{walk}
            }}
        }}
        {J}
        return res;
    }}
'''
    upd = {"assign": ("T v", "applyAssign(b, v)" if s.asgTag else "applyClamp(b, " + clamp_args(s, "v", "v", "T(0)") + ")" if s.clamp
                      else "applyBits(b, " + bits_args(s, "T(0)", "v") + ")"),
           "add": ("T v", "applyAP(b, v, T(0))" if s.ap else "applyAdd(b, v)" if s.addTag else "applyClamp(b, " + clamp_args(s, "INF", "NEG", "v") + ")"),
           "ap": ("T start, T step", "applyAP(b, start, step)"),
           "chmin": ("T v", "applyClamp(b, " + clamp_args(s, "v", "NEG", "T(0)") + ")"),
           "chmax": ("T v", "applyClamp(b, " + clamp_args(s, "INF", "v", "T(0)") + ")"),
           "and": ("T v", "applyBits(b, " + bits_args(s, "v", "T(0)") + ")"),
           "or": ("T v", "applyBits(b, " + bits_args(s, "~T(0)", "v") + ")"),
           "xor": ("T v", "applyXor(b, v)")}
    shr = {"mod": ("T x", "if (x >= 1) shrink(b, x, [x](T v) { return T(v % x); });", "logN * logU"),
           "div": ("T x", "if (x >= 2) shrink(b, T(1), [x](T v) { return T(v / x); });", "logN * logU"),
           "sqrt": ("", "shrink(b, T(2), isqrtT);", "logN * loglogU")}
    for u in s.ups:
        if u in shr:
            params, call, c = shr[u]
            pub[UOP[u]] = f'''    // amortized O({c}) expected -- {UDOC[u]}
    void {UOP[u]}(int l, int r{", " + params if params else ""}) {{
        {cut}
        {call}
        {J}
    }}
'''
            continue
        params, call = upd[u]
        pub[UOP[u]] = f'''    // O(logN) expected -- {UDOC[u]}
    void {UOP[u]}(int l, int r, {params}) {{
        {cut}
        {call};
        {J}
    }}
'''
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(val[t], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(val[t], v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    // O(logN) expected -- {doc}
    void {op}(int i, T v) {{
        vector<int> path;
        int t = locate(i, &path);
''' + ("        T old = val[t];\n" if s.find else "") + f"        val[t] = {expr};\n" + ("        rekey(t, old);\n" if s.find else "") + (
        "        pull(t);\n        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);\n" if s.mods else "") + "    }\n"
    pub.update(CPP_SEQ)
    pub.update(CPP_PIECES)
    if s.find:
        pub["find"] = '''    // O(logN) expected -- the index of x, or -1 if x isn't in this treap (values distinct across all treaps)
    int find(T x) {
        auto it = where.find(x);
        if (it == where.end() || val[it->second] != x) return -1;
        int t = it->second;
        vector<int> path{t};
        while (true) {  // up to the root (a parent counts only while it still has the node as a child)
            int c = path.back(), p = par[c];
            if (!p || (L[p] != c && R[p] != c)) break;
            path.push_back(p);
        }
        if (path.back() != root) return -1;  // (erased, or in another treap)
''' + ('''        for (int k = (int)path.size() - 1; k >= 0; k--) push(path[k]);  // (pending reverses above it, top-down)
''' if s.tags() else "") + '''        int i = sz[L[t]];
        for (size_t k = 1; k < path.size(); k++)
            if (R[path[k]] == path[k - 1]) i += sz[L[path[k]]] + 1;
        return i;
    }
'''
    return pub


def cpp_pull(s):
    fl = [f[0] for f in s.fields()]
    L = ["        int l = L[x], r = R[x];", "        sz[x] = sz[l] + sz[r] + 1;"]
    if s.find:  # (a child's parent is only trusted while the parent still has it as a child: splits leave stale ones)
        L += ["        par[l] = par[r] = x;"]
    if not s.mods:
        return L
    L.append("        T v = val[x];")
    if s.ms:
        nm = ["s"] + [{"pre": "p", "suf": "q", "best": "b"}[f] for f in ("pre", "suf", "best") if f in s.ms]
        fld = {"s": "sm", "p": "pre", "q": "suf", "b": "best"}
        e = lambda A, B: {"s": f"{A}s + {B}s", "p": f"max({A}p, {A}s + {B}p)", "q": f"max({B}q, {B}s + {A}q)",  # noqa: E731
                          "b": f"max({{{A}b, {B}b, {A}q + {B}p}})"}
        back = ", ".join(f"{n} = n{n}" for n in nm)
        L += [f"        S {', '.join(f'{n} = S(v)' for n in nm)};  // the node alone, then with its left / right parts",
              "        if (l) {", f"            S {', '.join(f'l{n} = {fld[n]}[l]' for n in nm)};",
              f"            S {', '.join(f'n{n} = ' + e('l', '')[n] for n in nm)};", f"            {back};", "        }",
              "        if (r) {", f"            S {', '.join(f'r{n} = {fld[n]}[r]' for n in nm)};",
              f"            S {', '.join(f'n{n} = ' + e('', 'r')[n] for n in nm)};", f"            {back};", "        }",
              f"        {', '.join(f'{fld[n]}[x] = {n}' for n in nm)};"]
    elif "sm" in fl:
        L.append("        sm[x] = sm[l] + S(v) + sm[r];")
    for f, c in (("mn", "<"), ("mx", ">")):
        if f in fl:
            L.append(f"        {f}[x] = v;")
            L.append(f"        if (l && {f}[l] {c} {f}[x]) {f}[x] = {f}[l];")
            L.append(f"        if (r && {f}[r] {c} {f}[x]) {f}[x] = {f}[r];")
    if s.has("hash"):
        L += ["        U64 B = HB(), hv = hval(v);", "        pw[x] = hmul(hmul(pw[l], B), pw[r]);"] + (
            ["        gs[x] = hadd(hmul(hadd(hmul(gs[l], B), 1), pw[r]), gs[r]);"] if s.G else []) + [
            "        fh[x] = hadd(hmul(hadd(hmul(fh[l], B), hv), pw[r]), fh[r]);",
            "        bh[x] = hadd(hmul(hadd(hmul(bh[r], B), hv), pw[l]), bh[l]);"]
    if "xr" in fl:
        L.append("        xr[x] = xr[l] ^ v ^ xr[r];")
    if "an" in fl:
        L.append("        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)")
    if "orr" in fl:
        L.append("        orr[x] = orr[l] | v | orr[r];")
    if "g" in fl:
        if s.gdiff:  # the gcd of the adjacent differences inside the subtree (a range add leaves them alone)
            L += ["        T gg = gcd(g[l], g[r]);", "        if (l) gg = gcd(gg, T(v - lv[l]));", "        if (r) gg = gcd(gg, T(fv[r] - v));", "        g[x] = gg;"]
        else:
            L.append("        g[x] = gcd(gcd(g[l], v), g[r]);")
    if "pr" in fl:  # (prefix run, suffix run, best run): the left part joins the node, then the right part joins them
        L += ["        int rp = 1, rq = 1, bb = 1;", "        if (l) {", "            bool j = lv[l] == v;",
              "            rp = pr[l] + (j && pr[l] == sz[l]);", "            rq = j ? sr[l] + 1 : 1;", "            bb = max(br[l], rq);", "        }",
              "        if (r) {", "            bool j = v == fv[r];", "            bb = max({bb, br[r], j ? rq + pr[r] : 0});",
              "            if (j && rp == sz[l] + 1) rp += pr[r];", "            rq = j && sr[r] == sz[r] ? sr[r] + rq : sr[r];", "        }",
              "        pr[x] = rp, sr[x] = rq, br[x] = bb;"]
    if s.ends:
        L += ["        fv[x] = l ? fv[l] : v;", "        lv[x] = r ? lv[r] : v;"]
    if "a00" in fl:
        L += ["        array<S, 4> c{S(v), NEG, NEG, -S(v)};", "        if (l) c = altJoin({a00[l], a01[l], a10[l], a11[l]}, c);",
              "        if (r) c = altJoin(c, {a00[r], a01[r], a10[r], a11[r]});", "        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];"]
    return L


def cpp_new(s):
    fl = [f[0] for f in s.fields()]
    parts = []
    if "sm" in fl:
        parts.append("sm.push_back(S(v))")
    for f in ("mn", "mx"):
        if f in fl:
            parts.append(f"{f}.push_back(v)")
    if "fh" in fl:
        parts += ["fh.push_back(hval(v))", "bh.push_back(hval(v))", "pw.push_back(HB())"] + (["gs.push_back(1)"] if s.G else [])
    for f in ("pre", "suf", "best"):
        if f in fl:
            parts.append(f"{f}.push_back(S(v))")
    for f in ("xr", "an", "orr"):
        if f in fl:
            parts.append(f"{f}.push_back(v)")
    if "g" in fl:
        parts.append("g.push_back(T(0))" if s.gdiff else "g.push_back(v < T(0) ? T(-v) : v)")
    if s.ends:
        parts += ["fv.push_back(v)", "lv.push_back(v)"]
    if "pr" in fl:
        parts += ["pr.push_back(1)", "sr.push_back(1)", "br.push_back(1)"]
    if "a00" in fl:
        parts += ["a00.push_back(S(v))", "a01.push_back(NEG)", "a10.push_back(NEG)", "a11.push_back(-S(v))"]
    parts += [f"{t[0]}.push_back({t[3]})" for t in s.tags()] + (["par.push_back(0)", "where[v] = (int)val.size() - 1"] if s.find else [])
    lines, cur = [], "       "
    for p in parts:
        if len(cur) + len(p) + 2 > 118:
            lines.append(cur.rstrip(",") + ";")
            cur = "       "
        cur += " " + p + ","
    if parts:
        lines.append(cur.rstrip(",") + ";")
    return lines


def rev_line(parts):  # parts joined by ", " and wrapped at 120 columns
    lines, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) + 10 > 118:
            lines.append(cur + ",")
            cur = ""
        cur += (", " if cur and not cur.endswith(",") else "") + p
    lines.append(cur + ";")
    return "\n        ".join(lines)


def cpp_internals(s):
    fl = [f[0] for f in s.fields()]
    tn = [t[0] for t in s.tags()]
    out = ['''
    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
''' + "".join(x + "\n" for x in cpp_new(s)) + '''        return (int)val.size() - 1;
    }
''' + ('''
    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }
''' if "a00" in fl else "") + CPP_BUILD + '''
    void pull(int x) {  // recompute x from its children
''' + "".join(x + "\n" for x in cpp_pull(s)) + "    }\n"]
    push = []
    if s.rev:
        sw = [f"swap({a}[x], {b}[x])" for a, b in (("fh", "bh"), ("pre", "suf"), ("fv", "lv"), ("pr", "sr"), ("a01", "a10")) if a in fl]
        ap = "\n        if (ad[x] || as_[x]) as_[x] += ad[x] * T(sz[x] - 1), ad[x] = -ad[x];  // a pending arithmetic add read backwards" if s.ap else ""
        out.append('''
    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        ''' + rev_line(["swap(L[x], R[x])", "rev[x] ^= 1"] + sw) + ap + '''
    }
''')
        push.append("        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;\n")
    if s.asgTag:
        a = (["int n = sz[x];"] if {"sm", "pre", "suf", "best", "xr", "pr", "a00"} & set(fl) else []) + ["val[x] = v;"]
        if "sm" in fl:
            a.append("sm[x] = S(v) * n;")
        for f in ("mn", "mx", "an", "orr"):
            if f in fl:
                a.append(f"{f}[x] = v;")
        if "fh" in fl:
            a.append("fh[x] = bh[x] = hmul(hval(v), gs[x]);")
        ms = [f for f in ("pre", "suf", "best") if f in fl]
        if ms:
            a.append(" = ".join(f"{f}[x]" for f in ms) + " = v > T(0) ? S(v) * n : S(v);")
        if "xr" in fl:
            a.append("xr[x] = n & 1 ? v : T(0);")
        if "g" in fl:
            a.append("g[x] = T(0);" if s.gdiff else "g[x] = v < T(0) ? T(-v) : v;")
        if s.ends:
            a.append("fv[x] = lv[x] = v;")
        if "pr" in fl:
            a.append("pr[x] = sr[x] = br[x] = n;")
        if "a00" in fl:
            a.append("a00[x] = S(v), a11[x] = -S(v), a01[x] = a10[x] = n > 1 ? S(0) : NEG;")
        a.append("asg[x] = v, hasAsg[x] = 1;")
        if s.addTag:
            a.append("add[x] = T(0);  // (an add pending below the assign is gone)")
        if s.ap:
            a.append("as_[x] = ad[x] = T(0);")
        if s.xorf:
            a.append("tx[x] = T(0);")
        out.append("\n    void applyAssign(int x, T v) {  // every value of x's subtree becomes v\n        if (!x) return;\n" +
                   "".join(f"        {y}\n" for y in a) + "    }\n")
        push.append("        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;\n")
    if s.addTag:
        a = ["val[x] += v;"]
        if "sm" in fl:
            a.append("sm[x] += S(v) * sz[x];")
        for f in ("mn", "mx"):
            if f in fl:
                a.append(f"{f}[x] += v;")
        if "fh" in fl:
            a += ["U64 h = hmul(hraw(v), gs[x]);", "fh[x] = hadd(fh[x], h), bh[x] = hadd(bh[x], h);"]
        if s.ends:
            a.append("fv[x] += v, lv[x] += v;")
        a.append("add[x] += v;")
        out.append("\n    void applyAdd(int x, T v) {  // every value of x's subtree gains v\n        if (!x) return;\n" +
                   "".join(f"        {y}\n" for y in a) + "    }\n")
        push.append("        if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = T(0);\n")
    if s.ap:
        out.append('''
    void applyAP(int x, T s, T d) {  // the k-th value of x's subtree (k from 0) gains s + k * d
        if (!x) return;
        val[x] += s + d * T(sz[L[x]]);
''' + ("        S n = sz[x];\n        sm[x] += S(s) * n + S(d) * (n * (n - 1) / 2);\n" if "sm" in fl else "") + '''        as_[x] += s, ad[x] += d;
    }
''')
        push.append('''        if (as_[x] != T(0) || ad[x] != T(0)) {
            applyAP(L[x], as_[x], ad[x]), applyAP(R[x], as_[x] + ad[x] * T(sz[L[x]] + 1), ad[x]);
            as_[x] = ad[x] = T(0);
        }
''')
    if s.clamp:
        params = [{"hi": "H", "lo": "Lo", "c": "C"}[p] for p in ("hi", "lo", "c") if p in tn]
        f = lambda e: ("min(H, " if "hi" in tn else "") + ("max(Lo, " if "lo" in tn else "") + e + (" + C" if "c" in tn else "") + (")" if "lo" in tn else "") + (")" if "hi" in tn else "")  # noqa: E731
        a = [f"val[x] = {f('val[x]')};"] + [f"{g}[x] = {f(f'{g}[x]')};" for g in ("mn", "mx") if g in fl]
        # compose (the old map, then this one): hi' = H(old hi), lo' = min(lo pushed through, hi'), c' = old c + C
        if "hi" in tn:
            oh = "(hi[x] == INF ? INF : T(hi[x] + C))" if "c" in tn else "hi[x]"
            a.append("T h = min(H, " + (f"max(Lo, {oh})" if "lo" in tn else oh) + ");")
        if "lo" in tn:
            lo_e = "max(Lo, lo[x] == NEG ? NEG : T(lo[x] + C))" if "c" in tn else "max(Lo, lo[x])"
            a.append(f"lo[x] = {'min(' + lo_e + ', h)' if 'hi' in tn else lo_e};")
        if "hi" in tn:
            a.append("hi[x] = h;")
        if "c" in tn:
            a.append("c[x] += C;")
        sig = ", ".join(f"T {p}" for p in params)
        out.append(f"\n    void applyClamp(int x, {sig}) {{  // every value v of x's subtree becomes {f('v')}\n        if (!x) return;\n" +
                   "".join(f"        {y}\n" for y in a) + "    }\n")
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        cond = " || ".join({"hi": "hi[x] != INF", "lo": "lo[x] != NEG", "c": "c[x] != T(0)"}[p] for p in tp)
        args = ", ".join(f"{p}[x]" for p in tp)
        reset = ", ".join(f"{p}[x] = " + {"hi": "INF", "lo": "NEG", "c": "T(0)"}[p] for p in tp)
        push.append(f"        if ({cond}) {{\n            applyClamp(L[x], {args}), applyClamp(R[x], {args});\n            {reset};\n        }}\n")
    if s.bits:
        TA, TO = "tA" in tn, "tO" in tn
        sig = ", ".join((["T A"] if TA else []) + (["T O"] if TO else []))
        f = lambda e: ("(" if TO else "") + e + (" & A" if TA else "") + (") | O" if TO else "")  # noqa: E731
        a = [f"{g}[x] = {f(f'{g}[x]')};" for g in ("val", "an", "orr") if g == "val" or g in fl]
        if TA:
            a.append("tA[x] &= A;")
        if TO:
            a.append(f"tO[x] = {f('tO[x]')};")
        out.append(f"\n    void applyBits(int x, {sig}) {{  // every value v of x's subtree becomes {f('v')}\n        if (!x) return;\n" +
                   "".join(f"        {y}\n" for y in a) + "    }\n")
        cond = " || ".join((["tA[x] != ~T(0)"] if TA else []) + (["tO[x] != T(0)"] if TO else []))
        args = ", ".join((["tA[x]"] if TA else []) + (["tO[x]"] if TO else []))
        reset = ", ".join((["tA[x] = ~T(0)"] if TA else []) + (["tO[x] = T(0)"] if TO else []))
        push.append(f"        if ({cond}) {{\n            applyBits(L[x], {args}), applyBits(R[x], {args});\n            {reset};\n        }}\n")
    if s.xorf:
        out.append("\n    void applyXor(int x, T v) {  // every value of x's subtree is xored with v\n        if (!x) return;\n"
                   "        val[x] ^= v;\n" + ("        if (sz[x] & 1) xr[x] ^= v;\n" if "xr" in fl else "") + "        tx[x] ^= v;\n    }\n")
        push.append("        if (tx[x] != T(0)) applyXor(L[x], tx[x]), applyXor(R[x], tx[x]), tx[x] = T(0);\n")
    if push:
        out.append("\n    void push(int x) {  // hand x's pending tags to its children\n" + "".join(push) + "    }\n")
    if s.shrink:
        out.append('''
    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrink(int t, T lim, const F& f) {  // every value v >= lim under t becomes f(v) (the rest are fixed)
        if (!t || mx[t] < lim) return;
''' + ("        if (mn[t] == mx[t]) { applyAssign(t, f(mx[t])); return; }  // all equal: one assign\n" if s.asgTag else "") + '''        push(t);
        if (val[t] >= lim) val[t] = f(val[t]);
        shrink(L[t], lim, f), shrink(R[t], lim, f);
        pull(t);
    }
''')
    if s.find:
        out.append('''
    void rekey(int t, T old) {  // t's value changed from old: the map follows (find needs distinct values)
        auto it = where.find(old);
        if (it != where.end() && it->second == t) where.erase(it);
        where[val[t]] = t;
    }
''')
    out.append(CPP_TAIL)
    return "".join(out)


CPP_SEQ = {
    "pointGet": "    // O(logN) expected -- a[i]\n    T pointGet(int i) { return val[locate(i)]; }\n",
    "insertAt": '''    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }
''',
    "insertCopiesAt": '''    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }
''',
    "append": "    // O(logN) expected -- append v to the end\n    void append(T v) { root = merge(root, newNode(v)); }\n",
    "appendLeft": "    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)\n    void appendLeft(T v) { insertAt(0, v); }\n",
    "rangeReverse": '''    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }
''',
    "rangeRotateLeft": '''    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        int a, b, c, len = r - l + 1;
        cut(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            int b1, b2;
            split(b, (int)k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
    }
''',
    "rangeRotateRight": "    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the\n"
                        "    // length (negative shifts left)\n"
                        "    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }\n",
    "moveRange": '''    // O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    void moveRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }
''',
    "getAll": '''    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> out;
        out.reserve(size());
        vector<int> st;
        int t = root;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }
''',
}

CPP_PIECES = {
    "cut": '''    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    ImplicitTreap cut(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }
''',
    "paste": '''    // O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, ImplicitTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }
''',
    "merge": '''    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }
''',
    "split": '''    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }
''',
    "trisect": '''    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }
''',
}

CPP_BUILD = '''
    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    int build(const vector<T>& vals) {
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }
'''

CPP_TAIL = '''
    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }

    void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
        int t = root;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};
'''


def old_folder(text):
    """this generator's folders, and the ones it replaces (gen_treap's and gen_treap_more's max-subarray / bitwise)"""
    flat = " ".join(text.replace("#", " ").split())
    return "@data-structure-type: treap" in text and (MARK in flat or "plus point ops" in flat or (
        "rotate and move ranges, each in O(logN) expected" in flat and ("maxPrefixSum" in text or "maxSuffixSum" in text or
                                                                         "rangeAndQuery" in text or "rangeOrQuery" in text)))


def main(only=None):
    if only is None:
        for d in os.listdir(DIR):
            t = os.path.join(DIR, d, "template.py")
            if os.path.exists(t) and old_folder(open(t).read()):
                shutil.rmtree(os.path.join(DIR, d))
    vs = variants()
    seen = {}
    for s in vs:
        if only is not None and not only(s):
            continue
        name = folder_name(s.ops)
        folder = name if len(name) <= 180 else s.name()
        assert folder not in seen, (folder, seen.get(folder))
        seen[folder] = s.name()
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(s))
        write_template(os.path.join(DIR, folder, "template.cpp"), cpp(s))
    print("wrote", len(seen), "treaps")


if __name__ == "__main__":
    main()
