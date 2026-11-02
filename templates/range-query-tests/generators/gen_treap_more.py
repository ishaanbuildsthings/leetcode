"""More implicit treaps: the sequence edits (insert / erase anywhere, rotate, move ranges) together with aggregates the
plain treaps don't keep. One skeleton (gen_treap.py's, array nodes), three kinds of node data, and every variant keeps
only what its ops need (so nothing pays for an op it doesn't have):

    maxsub   rangeSum plus any of maxPrefixSum / maxSuffixSum / maxSubarraySum (sum always; best needs pre and suf),
             with or without rangeAssign (its tag). An add can't be kept: the best subarray moves with it.
    bitwise  any of rangeAndQuery / rangeOrQuery, and any of rangeAndApply / rangeOrApply / rangeAssign: every update is
             x -> (x & A) | O and those compose; and= keeps only the A tag, or= only the O tag, assign needs both.
    affine   rangeSumMod with rangeAddMod (tag c only), rangeMultMod (tag m only), or all of add / mult / affine / assign
             (x -> x * m + c % MOD, tags m and c).
    brackets isRBS on a sequence of characters (open = +1, anything else = -1): each node keeps its +-1 sum and min
             prefix sum, with or without rangeAssign (assign tag) and rangeFlip (open <-> close, flip tag; a flip negates,
             so it needs the max prefix too); a reverse needs the min suffix (and with flips the max suffix).

and each with or without rangeReverse (its tag; a reverse swaps a node's prefix and suffix, so a maxsub variant with only
one of them can't reverse).

    python3 gen_treap_more.py
"""
import itertools
import os
import re
import shutil

from gen_treap import no_push, wrap
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SEQ = ["append", "appendLeft", "concat", "cut", "getAll", "insertAt", "insertCopiesAt", "moveRange", "paste", "split", "trisect",
       "rangeRotateLeft", "rangeRotateRight"]
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
MAXSUB_Q = {"pre": ("maxPrefixSum", "max of a[l] + ... + a[i] over i in [l, r]"),
            "suf": ("maxSuffixSum", "max of a[i] + ... + a[r] over i in [l, r]"),
            "best": ("maxSubarraySum", "max sum of a non-empty contiguous subarray of a[l..r]")}
BIT_Q = {"an": ("rangeAndQuery", "a[l] & ... & a[r]"), "orr": ("rangeOrQuery", "a[l] | ... | a[r]")}
BIT_U = {"and": ("rangeAndApply", "a[i] &= v for i in [l, r]"), "or": ("rangeOrApply", "a[i] |= v for i in [l, r]"),
         "assign": ("rangeAssign", "a[i] = v for i in [l, r]")}
AFF_U = {"add": ["rangeAddMod"], "mult": ["rangeMultMod"], "full": ["rangeAddMod", "rangeAffineMod", "rangeAssignMod", "rangeMultMod"]}
UDOC = {"rangeFlip": "every open in a[l..r] becomes closeChar and every other character openChar","rangeAddMod": "a[i] = (a[i] + v) % MOD for i in [l, r]", "rangeMultMod": "a[i] = a[i] * v % MOD for i in [l, r]",
        "rangeAffineMod": "a[i] = (a[i] * mult + add) % MOD for i in [l, r]", "rangeAssignMod": "a[i] = v % MOD for i in [l, r]",
        "rangeAssign": BIT_U["assign"][1], "rangeAndApply": BIT_U["and"][1], "rangeOrApply": BIT_U["or"][1]}
IDENT = {"mn": "0", "mx": "0", "mnS": "0", "mxS": "0", "flp": "0", "sm": "0", "pre": "0", "suf": "0", "best": "0", "an": "-1", "orr": "0", "rev": "0", "asg": "0", "hasAsg": "0",
         "tA": "-1", "tO": "0", "tm": "1", "tc": "0"}


def variants():
    """(kind, spec) for every variant: maxsub fields / assign, bitwise queries / updates, affine tags; each with rev or not"""
    out = []
    for rev in (False, True):  # (max-subarray and bitwise treaps: gen_treap_algebra.py, mixable with every other aggregate)
        for aff in ("add", "mult", "full"):
            out.append(("affine", dict(rev=rev, aff=aff)))
        for k in range(3):
            for U in itertools.combinations(("assign", "flip"), k):
                out.append(("brackets", dict(rev=rev, U=U)))
    return out


def ops_of(kind, sp):
    ops = SEQ + (["rangeReverse"] if sp["rev"] else [])
    if kind == "maxsub":
        ops += POINT + ["rangeSum"] + [MAXSUB_Q[f][0] for f in sp["F"]] + (["rangeAssign"] if sp["asg"] else [])
    elif kind == "bitwise":
        ops += POINT + [BIT_Q[q][0] for q in sp["Q"]] + [BIT_U[u][0] for u in sp["U"]]
    elif kind == "affine":
        ops += ["pointAdd", "pointAssign", "pointGet", "rangeSumMod"] + AFF_U[sp["aff"]]
    else:
        ops += ["isRBS", "pointAssign", "pointGet"] + (["rangeAssign"] if "assign" in sp["U"] else []) + (
            ["rangeFlip"] if "flip" in sp["U"] else [])
    return sorted(ops)


def fields_tags(kind, sp):
    """(node arrays beyond val / sz / L / R / pri, tag arrays)"""
    tags = ["rev"] if sp["rev"] else []
    if kind == "maxsub":
        return ["sm"] + list(sp["F"]), tags + (["asg", "hasAsg"] if sp["asg"] else [])
    if kind == "bitwise":
        U = sp["U"]
        return list(sp["Q"]), tags + (["tA"] if "and" in U or "assign" in U else []) + (["tO"] if "or" in U or "assign" in U else [])
    if kind == "brackets":
        FL = "flip" in sp["U"]
        return (["sm", "mn"] + (["mx"] if FL else []) + (["mnS"] if sp["rev"] else []) + (["mxS"] if sp["rev"] and FL else []),
                tags + (["asg", "hasAsg"] if "assign" in sp["U"] else []) + (["flp"] if FL else []))
    return ["sm"], tags + {"add": ["tc"], "mult": ["tm"], "full": ["tm", "tc"]}[sp["aff"]]


def queries(kind, sp):
    """(op, doc, node array it reads)"""
    if kind == "maxsub":
        return [("rangeSum", "a[l] + ... + a[r]", "sm")] + [(MAXSUB_Q[f][0], MAXSUB_Q[f][1], f) for f in sp["F"]]
    if kind == "bitwise":
        return [(BIT_Q[q][0], BIT_Q[q][1], q) for q in sp["Q"]]
    if kind == "brackets":
        return []  # (isRBS reads two arrays)
    return [("rangeSumMod", "(a[l] + ... + a[r]) % MOD", "sm")]


def header(cm, ops, kind, sp):
    F, tags = fields_tags(kind, sp)
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: treap", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N) expected'}" for op in ops] + ["  build: N", "@memory:", "  layout: none"]
    lines += ["  node: " + " ".join(f"{f}[1*N]" for f in ["val", "sz", "L", "R", "pri"] + F),
              "  tags: " + (" ".join(f"{f}[1*N]" for f in tags) or "none"), "  other: none",
              "  note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(kind, sp):
    if kind == "maxsub":
        what = ("each node keeps its subtree's sum" +
                "".join(", best " + {"pre": "prefix", "suf": "suffix", "best": "subarray"}[f] for f in sp["F"]) +
                ("; a reverse swaps prefix and suffix" if sp["rev"] else ""))
    elif kind == "bitwise":
        what = ("each node keeps its subtree's " + " and ".join({"an": "AND", "orr": "OR"}[q] for q in sp["Q"]) +
                ("; every update is x -> (x & A) | O, and those compose" if sp["U"] else ""))
    elif kind == "affine":
        what = "values live % MOD; each node keeps its subtree's sum, and every update is x -> x * m + c (% MOD)"
    else:
        FL = "flip" in sp["U"]
        what = ("the values are characters, openChar = +1 and " + ("closeChar" if FL else "any other character") + " = -1, and "
                "a range is a regular bracket sequence iff its sum is 0 and no prefix sum is negative; each node keeps its "
                "subtree's sum and min prefix sum (over prefixes including the empty one)" +
                (", and its max prefix sum (a flip negates every value: min and max swap and change sign)" if FL else "") +
                (", and its min" + (" / max" if FL else "") + " suffix sum (a reverse swaps prefixes and suffixes)" if sp["rev"] else ""))
    return ("Implicit treap: an array you can insert into / erase from anywhere, " + ("reverse, " if sp["rev"] else "") +
            f"rotate and move ranges, each in O(logN) expected; {what}. All indices 0-based, ranges inclusive [l, r], an "
            "index always the position in the CURRENT array." +
            (" Lazy tags mean \"already applied to this node, not yet to its children\"." if fields_tags(kind, sp)[1] else ""))


def name_of(kind, sp):
    if kind == "maxsub":
        tok = "-".join(sp["F"]) + ("-assign" if sp["asg"] else "")
    elif kind == "bitwise":
        tok = "-".join(sp["Q"]) + "".join("-" + u for u in sp["U"])
    elif kind == "affine":
        tok = sp["aff"]
    else:
        tok = "-".join(sp["U"]) or "plain"
    return f"treap-{kind}-{tok}" + ("-rev" if sp["rev"] else "")


def combine(names, A, B):
    """the combine of part A then part B (variable prefixes) for each of names: s sum, p prefix, q suffix, b best"""
    e = {"s": f"{A}s + {B}s", "p": f"max({A}p, {A}s + {B}p)", "q": f"max({B}q, {B}s + {A}q)", "b": f"max({A}b, {B}b, {A}q + {B}p)"}
    return [e[nm] for nm in names]


MS_NAME = {"pre": "p", "suf": "q", "best": "b"}
MS_FIELD = {"s": "sm", "p": "pre", "q": "suf", "b": "best"}


# ------------------------------------------------------------------------------------------------ Python

def py_pull(kind, sp, F):
    head = "        l, r = self.L[x], self.R[x]\n        self.sz[x] = self.sz[l] + self.sz[r] + 1\n"
    if kind == "maxsub":
        nm = ["s"] + [MS_NAME[f] for f in sp["F"]]
        names = ", ".join(nm)
        return head + f'''        v = self.val[x]
        {names} = {", ".join("v" for _ in nm)}  # the node alone, then with its left / right parts
        if l:
            {", ".join("l" + n for n in nm)} = {", ".join(f"self.{MS_FIELD[n]}[l]" for n in nm)}
            {names} = {", ".join(combine(nm, "l", ""))}
        if r:
            {", ".join("r" + n for n in nm)} = {", ".join(f"self.{MS_FIELD[n]}[r]" for n in nm)}
            {names} = {", ".join(combine(nm, "", "r"))}
        {", ".join(f"self.{MS_FIELD[n]}[x]" for n in nm)} = {names}
'''
    if kind == "bitwise":
        return head + "        v = self.val[x]\n" + "".join(
            (["        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)\n"] if "an" in F else []) +
            (["        self.orr[x] = self.orr[l] | v | self.orr[r]\n"] if "orr" in F else []))
    if kind == "brackets":  # (node 0 has every sum 0, so an empty side needs no case)
        return head + ("        v = 1 if self.val[x] == self.oc else -1\n"
                       "        a = self.sm[l] + v  # the left part and the node\n"
                       "        self.mn[x] = min(self.mn[l], a, a + self.mn[r])\n" +
                       ("        self.mx[x] = max(self.mx[l], a, a + self.mx[r])\n" if "mx" in F else "") +
                       ("        b = v + self.sm[r]  # the node and the right part\n"
                        "        self.mnS[x] = min(self.mnS[r], b, b + self.mnS[l])\n" if "mnS" in F else "") +
                       ("        self.mxS[x] = max(self.mxS[r], b, b + self.mxS[l])\n" if "mxS" in F else "") +
                       "        self.sm[x] = a + self.sm[r]\n")
    return head + "        self.sm[x] = (self.sm[l] + self.val[x] + self.sm[r]) % self.mod\n"


def py_apply_push(kind, sp, F, tags):
    """(the apply function for the updates, the update part of _push)"""
    if kind == "maxsub":
        if not sp["asg"]:
            return "", ""
        return ('''
    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x], self.sm[x] = v, v * n
            ''' + " = ".join(f"self.{f}[x]" for f in sp["F"]) + ''' = v * n if v > 0 else v
            self.asg[x], self.hasAsg[x] = v, 1
''', '''        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
''')
    if kind == "bitwise":
        if not sp["U"]:
            return "", ""
        TA, TO = "tA" in tags, "tO" in tags
        body = ["self.val[x] = (self.val[x] & A) | O"] + [f"self.{f}[x] = (self.{f}[x] & A) | O" for f in F]
        body += (["self.tA[x] &= A"] if TA else []) + (["self.tO[x] = (self.tO[x] & A) | O"] if TO else [])
        cond = " or ".join((["self.tA[x] != -1"] if TA else []) + (["self.tO[x]"] if TO else []))
        A, O = ("self.tA[x]" if TA else "-1"), ("self.tO[x]" if TO else "0")
        reset = ", ".join(f"self.{t}[x]" for t in ("tA", "tO") if t in tags) + " = " + ", ".join(IDENT[t] for t in ("tA", "tO") if t in tags)
        return ("\n    def _applyBits(self, x, A, O):  # every value v of x's subtree becomes (v & A) | O\n        if x:\n" +
                "".join(f"            {s}\n" for s in body),
                f"        if {cond}:\n            self._applyBits(self.L[x], {A}, {O})\n            self._applyBits(self.R[x], {A}, {O})\n"
                f"            {reset}\n")
    if kind == "brackets":
        return py_brackets_apply_push(sp, F)
    TM, TC = "tm" in tags, "tc" in tags
    tag = ("self.tm[x], self.tc[x] = self.tm[x] * m % p, (self.tc[x] * m + c) % p" if TM and TC else
           "self.tm[x] = self.tm[x] * m % p" if TM else "self.tc[x] = (self.tc[x] + c) % p")
    cond = " or ".join((["self.tm[x] != 1"] if TM else []) + (["self.tc[x]"] if TC else []))
    M, C = ("self.tm[x]" if TM else "1"), ("self.tc[x]" if TC else "0")
    reset = ", ".join(f"self.{t}[x]" for t in ("tm", "tc") if t in tags) + " = " + ", ".join(IDENT[t] for t in ("tm", "tc") if t in tags)
    return (f'''
    def _applyAff(self, x, m, c):  # every value v of x's subtree becomes v * m + c (% MOD)
        if x:
            p = self.mod
            self.val[x] = (self.val[x] * m + c) % p
            self.sm[x] = (self.sm[x] * m + c * self.sz[x]) % p
            {tag}
''', f"        if {cond}:\n            self._applyAff(self.L[x], {M}, {C})\n            self._applyAff(self.R[x], {M}, {C})\n            {reset}\n")


def py_brackets_apply_push(sp, F):
    apply, push = "", ""
    lows, highs = [f for f in ("mn", "mnS") if f in F], [f for f in ("mx", "mxS") if f in F]
    if "assign" in sp["U"]:
        apply += ('''
    def _applyAssign(self, x, ch):  # every character of x's subtree becomes ch
        if x:
            v = self.sz[x] if ch == self.oc else -self.sz[x]
            self.val[x], self.sm[x] = ch, v
            ''' + " = ".join(f"self.{f}[x]" for f in lows) + " = v if v < 0 else 0\n" +
                  ("            " + " = ".join(f"self.{f}[x]" for f in highs) + " = v if v > 0 else 0\n" if highs else "") +
                  "            self.asg[x], self.hasAsg[x] = ch, 1\n" +
                  ("            self.flp[x] = 0  # (the assign overrides a pending flip)\n" if "flip" in sp["U"] else ""))
        push += '''        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
'''
    if "flip" in sp["U"]:
        apply += ('''
    def _applyFlip(self, x):  # every open of x's subtree becomes a close and vice versa
        if x:
            self.val[x] = self.cc if self.val[x] == self.oc else self.oc
            self.sm[x] = -self.sm[x]
            self.mn[x], self.mx[x] = -self.mx[x], -self.mn[x]
''' + ("            self.mnS[x], self.mxS[x] = -self.mxS[x], -self.mnS[x]\n" if "mnS" in F else "") + "            self.flp[x] ^= 1\n")
        push += '''        if self.flp[x]:  # (after the assign: a pending assign and flip mean assign, then flip)
            self._applyFlip(self.L[x])
            self._applyFlip(self.R[x])
            self.flp[x] = 0
'''
    return apply, push


def slots_line(slots):
    """__slots__ = (...), wrapped at 120 columns"""
    lines, cur = [], "    __slots__ = ("
    for k, s in enumerate(slots):
        piece = repr(s) + (", " if k + 1 < len(slots) else ")")
        if len(cur) + len(piece.rstrip()) > 120:
            lines.append(cur.rstrip())
            cur = " " * 17
        cur += piece
    return "\n".join(lines + [cur]) + "\n\n"


def python(kind, sp):
    ops = ops_of(kind, sp)
    F, tags = fields_tags(kind, sp)
    RV = sp["rev"]
    BR, FL = kind == "brackets", kind == "brackets" and "flip" in sp["U"]
    slots = ["root", "val", "pri", "L", "R", "sz"] + F + tags + (["mod"] if kind == "affine" else ["oc"] + (["cc"] if FL else []) if BR else [])
    ctor = ("def __init__(self, arr=(), mod=None, like=None):" if kind == "affine" else
            "def __init__(self, brackets=(), openChar=\"(\"" + (", closeChar=\")\"" if FL else "") + ", like=None):" if BR else
            "def __init__(self, arr=(), like=None):")
    share = ("        else:\n            self.val, self.pri, self.L, self.R, self.sz = like.val, like.pri, like.L, like.R, like.sz\n" +
             "".join(f"            self.{n} = like.{n}\n" for n in slots[6:]))
    zero = ("        self.mod = mod\n" if kind == "affine" else "") + (
        "        self.oc = openChar\n" + ("        self.cc = closeChar\n" if FL else "") if BR else "") + "".join(
        f"        self.{f} = [{IDENT[f]}]\n" for f in F + tags)
    if BR:  # a lone character: its +-1 is its sum; every prefix / suffix min is min(0, it), every max max(0, it)
        new_extra = ("        w = 1 if v == self.oc else -1\n        self.sm.append(w)\n" +
                     "".join(f"        self.{f}.append(w if w < 0 else 0)\n" for f in F if f in ("mn", "mnS")) +
                     "".join(f"        self.{f}.append(w if w > 0 else 0)\n" for f in F if f in ("mx", "mxS")))
    else:
        new_extra = "".join(f"        self.{f}.append(v)\n" for f in F)
    new_extra += "".join(f"        self.{t}.append({IDENT[t]})\n" for t in tags)
    apply, push = py_apply_push(kind, sp, F, tags)
    rev_def = ""
    if RV:
        rev_def = '''
    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''' + ("            self.pre[x], self.suf[x] = self.suf[x], self.pre[x]\n" if kind == "maxsub" else "") + (
            "            self.mn[x], self.mnS[x] = self.mnS[x], self.mn[x]\n" if BR else "") + (
            "            self.mx[x], self.mxS[x] = self.mxS[x], self.mx[x]\n" if FL else "")
        push = '''        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0
''' + push
    pub = {}
    for q, doc, f in queries(kind, sp):
        pub[q] = f'''    # O(logN) expected -- {doc}
    def {q}(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.{f}[b]
        self._join(a, b, c)
        return res
'''
    if BR:
        pub["isRBS"] = '''    # O(logN) expected -- is a[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.sm[b] == 0 and self.mn[b] >= 0
        self._join(a, b, c)
        return res
'''
    upd_call = {"rangeAssign": ("v", "self._applyAssign(b, v)" if kind in ("maxsub", "brackets") else "self._applyBits(b, 0, v)"),
                "rangeFlip": ("", "self._applyFlip(b)"),
                "rangeAndApply": ("v", "self._applyBits(b, v, 0)"), "rangeOrApply": ("v", "self._applyBits(b, -1, v)"),
                "rangeAddMod": ("v", "self._applyAff(b, 1, v % self.mod)"), "rangeMultMod": ("v", "self._applyAff(b, v % self.mod, 0)"),
                "rangeAffineMod": ("mult, add", "self._applyAff(b, mult % self.mod, add % self.mod)"),
                "rangeAssignMod": ("v", "self._applyAff(b, 0, v % self.mod)")}
    for u, (args, call) in upd_call.items():
        if u in ops:
            pub[u] = f'''    # O(logN) expected -- {UDOC[u]}
    def {u}(self, l, r{", " + args if args else ""}):
        a, b, c = self._cut(l, r)
        {call}
        self._join(a, b, c)
'''
    norm = " % self.mod" if kind == "affine" else ""
    for op, expr, doc in (("pointAssign", f"v{norm}", "a[i] = v"), ("pointAdd", f"(self.val[t] + v){norm}", "a[i] += v"),
                          ("pointChmax", "max(self.val[t], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(self.val[t], v)", "a[i] = min(a[i], v)")):
        if op in ops:
            pub[op] = f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        t, path = self._find(i)
        self.val[t] = {expr}
        self._pull(t)
        for x in reversed(path):
            self._pull(x)
'''
    pub.update(PY_SEQ)
    from gen_treap_algebra import PY_PIECES  # (lazy: gen_treap_algebra imports this module)
    pub.update(PY_PIECES)
    vfix = "v % mod" if kind == "affine" else "v"
    out = (header("#", ops, kind, sp) + "\n" + wrap(describe(kind, sp), "#") + "import random\n\n\nclass ImplicitTreap:\n" +
           slots_line(slots) +
           (f"    # O(N) -- brackets: the sequence, a list of characters like [\"(\", \")\", \"(\"] (a str like \"()(\" works too);\n"
            f"    # openChar: the character that opens (\"(\" unless you pass e.g. \"[\")" + ("" if FL else "; ")
            + ("\n    # closeChar: the character that closes (every character must be one of the two)" if FL else "every other character closes") + f"\n    {ctor}\n" if BR else
            f"    # O(N) -- arr: the initial array (may be empty){'; mod: the modulus p' if kind == 'affine' else ''}\n    {ctor}\n") +
           "    # (like: an ImplicitTreap whose nodes this one shares, so pieces can move between the two; no reset needed)\n" +
           "        if like is None:\n            self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree\n" +
           "".join("    " + ln + "\n" for ln in zero.rstrip("\n").split("\n")) + share +
           (f"        self.root = self._build(list(brackets))\n" if BR else f"        self.root = self._build([{vfix} for v in arr])\n")
           + f"\n    # O(1) -- the current length of the array\n    def size(self):\n"
           "        return self.sz[self.root]\n\n" + "\n".join(pub[op] for op in ops) + '''
    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
''' + new_extra + "        return x\n" + PY_BUILD + '''
    def _pull(self, x):  # recompute x from its children
''' + py_pull(kind, sp, F) + rev_def + apply + ('''
    def _push(self, x):  # hand x's pending tags to its children
''' + push if push else "") + PY_TAIL)
    out = re.sub(r"(    def __init__\(.*\n)(    # \(like: .*\n)", r"\2\1", out)  # (the like note above the def)
    return out if push else no_push(out, "py")


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
    "rangeRotateLeft": '''    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)
''',
    "rangeRotateRight": '''    # O(logN) expected -- cyclic shift a[l..r] right by k; any integer k, negative shifts left
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

PY_BUILD = '''
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
'''

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


# ------------------------------------------------------------------------------------------------ C++

def cpp_pull(kind, sp, F):
    head = "        int l = L[x], r = R[x];\n        sz[x] = sz[l] + sz[r] + 1;\n"
    if kind == "maxsub":
        nm = ["s"] + [MS_NAME[f] for f in sp["F"]]
        cmb = lambda A, B: ", ".join(f"n{n} = {e}" for n, e in zip(nm, combine(nm, A, B))).replace("max(lb, b, lq + p)", "max({lb, b, lq + p})").replace(
            "max(b, rb, q + rp)", "max({b, rb, q + rp})")
        back = ", ".join(f"{n} = n{n}" for n in nm)
        return head + f'''        S v = S(val[x]), {", ".join(f"{n} = v" for n in nm)};  // the node alone, then with its left / right parts
        if (l) {{
            S {", ".join(f"l{n} = {MS_FIELD[n]}[l]" for n in nm)};
            S {cmb("l", "")};
            {back};
        }}
        if (r) {{
            S {", ".join(f"r{n} = {MS_FIELD[n]}[r]" for n in nm)};
            S {cmb("", "r")};
            {back};
        }}
        {", ".join(f"{MS_FIELD[n]}[x] = {n}" for n in nm)};
'''
    if kind == "bitwise":
        return head + "        " + ", ".join((["an[x] = an[l] & val[x] & an[r]"] if "an" in F else []) +
                                            (["orr[x] = orr[l] | val[x] | orr[r]"] if "orr" in F else [])) + ";\n"
    if kind == "brackets":  # (node 0 has every sum 0, so an empty side needs no case)
        return head + ("        // a: the left part and the node" + (", b: the node and the right part" if "mnS" in F else "") + "\n"
                       "        int v = val[x] == oc ? 1 : -1, a = sm[l] + v" + (", b = v + sm[r]" if "mnS" in F else "") + ";\n"
                       "        mn[x] = min({mn[l], a, a + mn[r]});\n" +
                       ("        mx[x] = max({mx[l], a, a + mx[r]});\n" if "mx" in F else "") +
                       ("        mnS[x] = min({mnS[r], b, b + mnS[l]});\n" if "mnS" in F else "") +
                       ("        mxS[x] = max({mxS[r], b, b + mxS[l]});\n" if "mxS" in F else "") +
                       "        sm[x] = a + sm[r];\n")
    return head + "        sm[x] = (sm[l] + (long long)val[x] + sm[r]) % mod;\n"


def cpp_brackets_apply_push(sp, F):
    apply, push = "", ""
    lows, highs = [f for f in ("mn", "mnS") if f in F], [f for f in ("mx", "mxS") if f in F]
    if "assign" in sp["U"]:
        apply += ('''
    void applyAssign(int x, T ch) {  // every character of x's subtree becomes ch
        if (!x) return;
        int v = ch == oc ? sz[x] : -sz[x];
        val[x] = ch, sm[x] = v, ''' + " = ".join(f"{f}[x]" for f in lows) + " = min(v, 0)" +
                  (", " + " = ".join(f"{f}[x]" for f in highs) + " = max(v, 0)" if highs else "") + ''';
        asg[x] = ch, hasAsg[x] = 1''' + (", flp[x] = 0;  // (the assign overrides a pending flip)" if "flip" in sp["U"] else ";") + '''
    }
''')
        push += "        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;\n"
    if "flip" in sp["U"]:
        apply += ('''
    void applyFlip(int x) {  // every open of x's subtree becomes a close and vice versa
        if (!x) return;
        val[x] = val[x] == oc ? cc : oc, sm[x] = -sm[x];
        swap(mn[x], mx[x]), mn[x] = -mn[x], mx[x] = -mx[x];
''' + ("        swap(mnS[x], mxS[x]), mnS[x] = -mnS[x], mxS[x] = -mxS[x];\n" if "mnS" in F else "") + '''        flp[x] ^= 1;
    }
''')
        push += "        if (flp[x]) applyFlip(L[x]), applyFlip(R[x]), flp[x] = 0;  // (after the assign: assign, then flip)\n"
    return apply, push


def cpp_apply_push(kind, sp, F, tags):
    if kind == "maxsub":
        if not sp["asg"]:
            return "", ""
        return (f'''
    void applyAssign(int x, T v) {{  // every value of x's subtree becomes v
        if (!x) return;
        S n = sz[x];
        val[x] = v, sm[x] = S(v) * n;
        {" = ".join(f"{f}[x]" for f in sp["F"])} = v > T(0) ? S(v) * n : S(v);
        asg[x] = v, hasAsg[x] = 1;
    }}
''', "        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;\n")
    if kind == "bitwise":
        if not sp["U"]:
            return "", ""
        TA, TO = "tA" in tags, "tO" in tags
        body = ["val[x] = (val[x] & A) | O"] + [f"{f}[x] = ({f}[x] & A) | O" for f in F]
        tagl = (["tA[x] &= A"] if TA else []) + (["tO[x] = (tO[x] & A) | O"] if TO else [])
        cond = " || ".join((["tA[x] != ~T(0)"] if TA else []) + (["tO[x] != T(0)"] if TO else []))
        A, O = ("tA[x]" if TA else "~T(0)"), ("tO[x]" if TO else "T(0)")
        reset = ", ".join((["tA[x] = ~T(0)"] if TA else []) + (["tO[x] = T(0)"] if TO else []))
        return (f'''
    void applyBits(int x, T A, T O) {{  // every value v of x's subtree becomes (v & A) | O
        if (!x) return;
        {", ".join(body)};
        {", ".join(tagl)};
    }}
''', f"        if ({cond}) {{\n            applyBits(L[x], {A}, {O}), applyBits(R[x], {A}, {O});\n            {reset};\n        }}\n")
    if kind == "brackets":
        return cpp_brackets_apply_push(sp, F)
    TM, TC = "tm" in tags, "tc" in tags
    tagl = ("tm[x] = mul(tm[x], m), tc[x] = (mul(tc[x], m) + c) % mod" if TM and TC else
            "tm[x] = mul(tm[x], m)" if TM else "tc[x] = (tc[x] + c) % mod")
    cond = " || ".join((["tm[x] != 1"] if TM else []) + (["tc[x]"] if TC else []))
    M, C = ("tm[x]" if TM else "1"), ("tc[x]" if TC else "0")
    reset = ", ".join((["tm[x] = 1"] if TM else []) + (["tc[x] = 0"] if TC else []))
    return (f'''
    long long mul(long long a, long long b) const {{ return (long long)((__int128)a * b % mod); }}
    void applyAff(int x, long long m, long long c) {{  // every value v of x's subtree becomes v * m + c (% MOD)
        if (!x) return;
        val[x] = T((mul((long long)val[x], m) + c) % mod);
        sm[x] = (mul(sm[x], m) + mul(c, sz[x])) % mod;
        {tagl};
    }}
    long long norm(long long v) const {{ return ((v % mod) + mod) % mod; }}
''', f"        if ({cond}) {{\n            applyAff(L[x], {M}, {C}), applyAff(R[x], {M}, {C});\n            {reset};\n        }}\n")


def poolify(text, kind):
    """the members of a treap made here -> a node pool shared by the treap and the pieces cut from it (references to
    its arrays keep the code as it is), with the constructors on top of it"""
    a = text.index("    int root = 0;\n")
    b = text.index("\n    static unsigned long long rnd()", a)
    pool, refs, names = [], [], []
    for ln in text[a:b].split("\n")[1:]:
        m = re.match(r"    vector<(.+?)> (.*?);(\s*//.*)?$", ln)
        if m:
            items = re.findall(r"(\w+)\{([^}]*)\}", m.group(2))
            pool.append(f"        vector<{m.group(1)}> {m.group(2)};{m.group(3) or ''}")
            refs += [f"    vector<{m.group(1)}>& {n};" for n, _ in items]
            names += [n for n, _ in items]
            continue
        m = re.match(r"    (long long|T) ([\w, ]+);(\s*//.*)?$", ln)
        if m:
            pool.append(f"        {m.group(1)} {m.group(2)};{m.group(3) or ''}")
            refs += [f"    {m.group(1)}& {n.strip()};" for n in m.group(2).split(",")]
            names += [n.strip() for n in m.group(2).split(",")]
        elif ln.strip():
            pool.append("    " + ln)
    parts, lines = ["pool(p)"] + [f"{n}(p->{n})" for n in names], [""]
    for x in parts:
        if lines[-1] and len(lines[-1]) + len(x) + 2 > 104:
            lines[-1] += ","
            lines.append("")
        lines[-1] += (", " if lines[-1] and not lines[-1].endswith(",") else "") + x
    head = ("    struct Pool {  // the node arrays: node 0 = the empty tree\n" + "\n".join(pool) + "\n    };\n"
            "    shared_ptr<Pool> pool;  // (shared by this treap and every piece cut from it; freed with the last of them)\n" +
            "\n".join(refs) + "\n    int root = 0;\n")
    text = text[:a] + head + text[b:]
    build = ("vector<T> v(arr);\n        for (T& x : v) x = T(norm((long long)x));\n        root = build(v);" if kind == "affine" else
             "root = build(brackets);" if kind == "brackets" else "root = build(arr);")
    arg = "brackets" if kind == "brackets" else "arr"
    if kind == "affine":
        text = text.replace("    ImplicitTreap(const vector<T>& arr, long long mod) : mod(mod) {\n",
                            "    ImplicitTreap(const vector<T>& arr, long long mod) : ImplicitTreap(make_shared<Pool>()) {\n        this->mod = mod;\n", 1)
    elif kind == "brackets":
        text = re.sub(r"\)\n        : oc\(openChar\)(, cc\(closeChar\))? \{\n",
                      lambda m: ")\n        : ImplicitTreap(make_shared<Pool>()) {\n        oc = openChar" + (", cc = closeChar" if m.group(1) else "") + ";\n",
                      text, count=1)
    m = re.search(r"\n    \}\n\n    // O\(1\) -- the current length of the array", text)
    extra = (f"\n    }}\n\n    // O(N) -- a treap over {arg} that shares other's nodes, so pieces can move between the two (pieces cut from a\n"
             f"    // treap share its nodes already); no reset between test cases: a treap's nodes are freed with it\n"
             f"    ImplicitTreap(const vector<T>& {arg}, const ImplicitTreap& other) : ImplicitTreap(other.pool) {{\n        {build}\n    }}\n\n"
             f"    // an empty treap on pool p\n    explicit ImplicitTreap(shared_ptr<Pool> p)\n        : " + "\n          ".join(lines) + " {}\n")
    return text[:m.start()] + extra + text[m.start() + len("\n    }\n"):]


def cpp(kind, sp):
    ops = ops_of(kind, sp)
    F, tags = fields_tags(kind, sp)
    RV = sp["rev"]
    S = "S" if kind == "maxsub" else "T"
    using = "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n" if kind == "maxsub" else ""
    if kind == "maxsub":
        what = ", ".join({"sm": "sum", "pre": "best prefix", "suf": "best suffix", "best": "best subarray"}[f] for f in F)
        fields = f"    vector<S> {', '.join(f + '{0}' for f in F)};  // {what}\n" + (
            "    vector<T> asg{T(0)};\n    vector<char> hasAsg{0};\n" if sp["asg"] else "")
        new_extra = ", ".join(f"{f}.push_back(S(v))" for f in F) + (";\n        asg.push_back(T(0)), hasAsg.push_back(0)" if sp["asg"] else "")
    elif kind == "bitwise":
        aggs = [f + ("{~T(0)}" if f == "an" else "{T(0)}") for f in F]
        what = " / ".join({"an": "AND", "orr": "OR"}[f] for f in F)
        fields = f"    vector<T> {', '.join(aggs)};  // {what} of the subtree (node 0: of nothing)\n"
        tg = [t + ("{~T(0)}" if t == "tA" else "{T(0)}") for t in ("tA", "tO") if t in tags]
        if tg:
            fields += f"    vector<T> {', '.join(tg)};  // the pending x -> (x & {'tA' if 'tA' in tags else '~0'}) | {'tO' if 'tO' in tags else '0'}\n"
        new_extra = ", ".join([f"{f}.push_back(v)" for f in F] + (["tA.push_back(~T(0))"] if "tA" in tags else []) +
                              (["tO.push_back(T(0))"] if "tO" in tags else []))
    elif kind == "brackets":
        FL = "flip" in sp["U"]
        fields = ("    T oc" + (", cc" if FL else "") + ";  // the opening character" + (" and the closing one" if FL else "") + "\n"
                  "    // +-1 sum, min" + (" / max" if FL else "") + " prefix sum" + (", min" + (" / max" if FL else "") + " suffix sum" if sp["rev"] else "") +
                  " (prefixes / suffixes include the empty one)\n" + f"    vector<int> {', '.join(f + '{0}' for f in F)};\n" +
                  ("    vector<T> asg{T(0)};\n    vector<char> hasAsg{0};\n" if "assign" in sp["U"] else "") +
                  ("    vector<char> flp{0};\n" if FL else ""))
        new_extra = ("int w = v == oc ? 1 : -1;\n        sm.push_back(w)" + "".join(f", {f}.push_back(min(w, 0))" for f in F if f in ("mn", "mnS")) +
                     (";\n        " + ", ".join(f"{f}.push_back(max(w, 0))" for f in F if f in ("mx", "mxS")) if FL else "") +
                     (";\n        " + ", ".join((["asg.push_back(T(0)), hasAsg.push_back(0)"] if "assign" in sp["U"] else []) +
                                             (["flp.push_back(0)"] if FL else [])) if sp["U"] else ""))
    else:
        TM, TC = "tm" in tags, "tc" in tags
        tg = (["tm{1}"] if TM else []) + (["tc{0}"] if TC else [])
        fields = (f"    long long mod;\n    vector<long long> sm{{0}};\n    vector<long long> {', '.join(tg)};  // the pending x -> x * "
                  f"{'tm' if TM else '1'} + {'tc' if TC else '0'} (% MOD)\n")
        new_extra = ", ".join(["sm.push_back((long long)v)"] + (["tm.push_back(1)"] if TM else []) + (["tc.push_back(0)"] if TC else []))
    apply, push = cpp_apply_push(kind, sp, F, tags)
    rev_def = ""
    if RV:
        rev_def = '''
    void applyRev(int x) {
        if (x) swap(L[x], R[x]), rev[x] ^= 1''' + (", swap(pre[x], suf[x])" if kind == "maxsub" else "") + (
            ", swap(mn[x], mnS[x])" if kind == "brackets" else "") + (", swap(mx[x], mxS[x])" if "mxS" in F else "") + ''';
    }
'''
        push = "        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;\n" + push
    pub = {}
    for q, doc, f in queries(kind, sp):
        typ = S if kind == "maxsub" else ("long long" if kind == "affine" else "T")
        pub[q] = f'''    // O(logN) expected -- {doc}
    {typ} {q}(int l, int r) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {typ} res = {f}[b];
        root = merge(merge(a, b), c);
        return res;
    }}
'''
    if kind == "brackets":
        pub["isRBS"] = '''    // O(logN) expected -- is a[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    bool isRBS(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = sm[b] == 0 && mn[b] >= 0;
        root = merge(merge(a, b), c);
        return res;
    }
'''
    upd = {"rangeAssign": ("T v", "applyAssign(b, v)" if kind in ("maxsub", "brackets") else "applyBits(b, T(0), v)"),
           "rangeFlip": ("", "applyFlip(b)"),
           "rangeAndApply": ("T v", "applyBits(b, v, T(0))"), "rangeOrApply": ("T v", "applyBits(b, ~T(0), v)"),
           "rangeAddMod": ("T v", "applyAff(b, 1, norm(v))"), "rangeMultMod": ("T v", "applyAff(b, norm(v), 0)"),
           "rangeAffineMod": ("T mult, T add", "applyAff(b, norm(mult), norm(add))"), "rangeAssignMod": ("T v", "applyAff(b, 0, norm(v))")}
    for u, (params, call) in upd.items():
        if u in ops:
            pub[u] = f'''    // O(logN) expected -- {UDOC[u]}
    void {u}(int l, int r{", " + params if params else ""}) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {call};
        root = merge(merge(a, b), c);
    }}
'''
    nv = "T(norm((long long)v))" if kind == "affine" else "v"
    nadd = "T(norm((long long)val[t] + (long long)v))" if kind == "affine" else "val[t] + v"
    for op, expr, doc in (("pointAssign", nv, "a[i] = v"), ("pointAdd", nadd, "a[i] += v"),
                          ("pointChmax", "max(val[t], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(val[t], v)", "a[i] = min(a[i], v)")):
        if op in ops:
            pub[op] = f'''    // O(logN) expected -- {doc}
    void {op}(int i, T v) {{
        vector<int> path;
        int t = find(i, &path);
        val[t] = {expr};
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }}
'''
    pub.update(cpp_seq(nv))
    from gen_treap_algebra import CPP_PIECES
    pub.update(CPP_PIECES)
    BR, FL = kind == "brackets", kind == "brackets" and "flip" in sp["U"]
    ctor_sig = ("ImplicitTreap(const vector<T>& arr, long long mod) : mod(mod)" if kind == "affine" else
                "explicit ImplicitTreap(const vector<T>& brackets, T openChar = T('(')" + (", T closeChar = T(')')" if FL else "") +
                ")\n        : oc(openChar)" + (", cc(closeChar)" if FL else "") if BR else "explicit ImplicitTreap(const vector<T>& arr)")
    init = ("        vector<T> v(arr);\n        for (T& x : v) x = T(norm((long long)x));\n        root = build(v);\n" if kind == "affine"
            else "        root = build(brackets);\n" if BR else "        root = build(arr);\n")
    tline = ("// T: int, long long, ...; sums are kept in S (long long for small T)." if kind == "maxsub" else
             "// T: char (or any type: openChar is the one that opens" + (", closeChar the one that closes)." if FL else ").") if BR else
             "// T: int, long long, ...")
    ctor_doc = ("// O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar: the character that\n"
                "    // opens ('(' unless you pass e.g. '[')" + ("; closeChar: the one that closes (every character must be one of\n    // the two)"
                                                                  if FL else "; every other character closes") if BR else
                "// O(N) -- arr: the initial array (may be empty)" + ("; mod: the modulus p" if kind == "affine" else ""))
    out = (header("//", ops, kind, sp) + "\n" + wrap(describe(kind, sp), "//") + tline +
           "\ntemplate <typename T>\nstruct ImplicitTreap {\n" + using +
           '''    int root = 0;
    vector<T> val{T(0)};  // node 0 is the empty tree
    vector<unsigned long long> pri{0};
    vector<int> L{0}, R{0}, sz{0};
''' + ("    vector<char> rev{0};\n" if RV else "") + fields + '''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    ''' + ctor_doc + f'''
    {ctor_sig} {{
{init}    }}

    // O(1) -- the current length of the array
    int size() const {{ return sz[root]; }}

''' + "\n".join(pub[op] for op in ops) + '''
    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1)''' + (", rev.push_back(0)" if RV else "") + f''';
        {new_extra};
        return (int)val.size() - 1;
    }}
''' + CPP_BUILD + '''
    void pull(int x) {  // recompute x from its children
''' + cpp_pull(kind, sp, F) + '''    }
''' + rev_def + apply + ('''
    void push(int x) {  // hand x's pending tags to its children
''' + push + '''    }
''' if push else "") + CPP_TAIL)
    out = poolify(out, kind)
    return out if push else no_push(out, "cpp")


def cpp_seq(nv):
    return {
        "pointGet": "    // O(logN) expected -- a[i]\n    T pointGet(int i) { return val[find(i)]; }\n",
        "insertAt": f'''    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {{
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode({nv})), c);
    }}
''',
        "insertCopiesAt": f'''    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {{
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, {nv}))), c);
    }}
''',
        "append": f"    // O(logN) expected -- append v to the end\n    void append(T v) {{ root = merge(root, newNode({nv})); }}\n",
        "appendLeft": '''    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }
''',
        "rangeReverse": '''    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }
''',
        "rangeRotateLeft": '''    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
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
        "rangeRotateRight": "    // O(logN) expected -- cyclic shift a[l..r] right by k; any integer k, negative shifts left\n"
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

    int find(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
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


def main():
    for d in os.listdir(DIR):  # this generator's folders, regenerated from scratch (their description is its own)
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and "rotate and move ranges, each in O(logN) expected" in " ".join(open(t).read().replace("#", " ").split()):
            shutil.rmtree(os.path.join(DIR, d))
    for kind, sp in variants():
        ops = ops_of(kind, sp)
        name = folder_name(ops)
        folder = os.path.join(DIR, name if len(name) <= 180 else name_of(kind, sp))
        os.makedirs(folder, exist_ok=True)
        write_template(os.path.join(folder, "template.py"), python(kind, sp))
        write_template(os.path.join(folder, "template.cpp"), cpp(kind, sp))
    print("wrote", len(variants()), "more treaps")


if __name__ == "__main__":
    main()
