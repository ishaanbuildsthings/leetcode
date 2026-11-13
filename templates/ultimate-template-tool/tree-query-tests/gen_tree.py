"""Writes the tree templates that hold values: tree-queries/node-<range folder>/ and edge-<range folder>/, each
template.{py,cpp} (node-: a value per node; edge-: a weight per edge, kept at the edge's lower end), and
both-<range folder>/: node values and edge weights in one Tree, two copies of the same range structure over one
layout, with every node op and every edge op.

Each one is a range-query template (templates/ultimate-template-tool/range-queries/<folder>), copied unchanged, with a
Tree class after it. The Tree lays the nodes out with one heavy-light pass (the same code as the shape templates, see
gen_tree_shape.py) and keeps the node values in the range structure in position order, so

    one node      -> one point op
    a subtree     -> one range op
    a path a..b   -> O(log n) range ops, one per chain piece

An edge template is the same with each edge's weight at its lower end's position: a path's edges are its nodes
without the lca, a subtree's edges are its nodes without its top. A query with no edges to look at (a path a..a, a
leaf's subtree) answers the neutral value in EMPTY, or raises where there is none.

Which tree ops a folder gets depends only on which range ops its template has: the tables below say how each tree op
is built (PATH_FOLDS: how the pieces' answers combine). Nothing is per-template.

    python3 gen_tree.py            # write every folder
    python3 gen_tree.py --check    # exit 1 if a folder on disk differs from what this would write
    python3 gen_tree.py --list     # only print what would be written

A range template that changes (a fix, a new op) reaches the tree templates by rerunning this. A range op that is
renamed has to be renamed in the tables here too: until then this stops with that op's name.
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "set-tests", "generators"))
import gen_tree_shape as shape  # noqa: E402
from format_long_lines import long_lines  # noqa: E402
from gen_sets import check_finished  # noqa: E402

RANGE_DIR = os.path.join(ROOT, "range-queries")
DIR = os.path.join(ROOT, "tree-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries"
RANGE_URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries"

# range ops that edit the sequence (a tree's shape is fixed): a template with one is never wrapped
SEQUENCE_OPS = set("append appendLeft pop popLeft split eraseRange cut trisect merge copy paste insertAt find rangeReverse "
                   "rangeRotateLeft rangeRotateRight insertCopiesAt rangeTwinSpin rangeSortAsc rangeSortDesc moveRange "
                   "copyRange".split())
# constructor arguments (after the array) a Tree can pass straight through
PASS_THROUGH = {"mod", "bits", "valLo", "valHi"}

# ------------------------------------------------------------------------------------------------ the op tables
# One node: (tree op suffix, range op, extra args, what it does)
POINT = [
    ("Get", "pointGet", [], "{val}({at})"),
    ("Assign", "pointAssign", ["{x}"], "{val}({at}) = {x}"),
    ("Add", "pointAdd", ["{x}"], "{val}({at}) += {x}"),
    ("Chmax", "pointChmax", ["{x}"], "{val}({at}) = max({val}, {x})"),
    ("Chmin", "pointChmin", ["{x}"], "{val}({at}) = min({val}, {x})"),
]
# The same update on every node of a path / a subtree: (suffix, range op, extra args, what it does to each value)
UPDATES = [
    ("Assign", "rangeAssign", ["{x}"], "{val} = {x}"),
    ("Add", "rangeAdd", ["{x}"], "{val} += {x}"),
    ("AddMod", "rangeAddMod", ["{x}"], "{val} = ({val} + {x}) % MOD"),
    ("Chmax", "rangeChmax", ["{x}"], "{val} = max({val}, {x})"),
    ("Chmin", "rangeChmin", ["{x}"], "{val} = min({val}, {x})"),
    ("XORApply", "rangeXorApply", ["{x}"], "{val} ^= {x}"),
    ("ORApply", "rangeOrApply", ["{x}"], "{val} |= {x}"),
    ("ANDApply", "rangeAndApply", ["{x}"], "{val} &= {x}"),
    ("MultMod", "rangeMultMod", ["m"], "{val} = ({val} * m) % MOD"),
    ("AffineMod", "rangeAffineMod", ["mult", "add"], "{val} = ({val} * mult + add) % MOD"),
]
# Queries a path and a subtree both have: (suffix, range op, extra args, how a path's pieces combine or None when a
# path cannot be answered piece by piece, what it returns). Subtrees take every one: a subtree is a single range.
QUERIES = [
    ("Sum", "rangeSum", [], "sum", "sum of the {vals} {where}"),
    ("SumMod", "rangeSumMod", [], "summod", "sum of the {vals} {where}, mod MOD"),
    ("Min", "rangeMin", [], "min", "min {one} {value} {where}"),
    ("Max", "rangeMax", [], "max", "max {one} {value} {where}"),
    ("Gcd", "rangeGcd", [], "gcd", "gcd of the {vals} {where}"),
    ("KthSmallest", "kthSmallest", ["k"], None, "kth smallest of the {vals} {where} (1-indexed: k = 1 is the min)"),
    ("KthLargest", "kthLargest", ["k"], None, "kth largest of the {vals} {where} (1-indexed: k = 1 is the max)"),
    ("CountLtX", "countLtX", ["x"], "sum", "how many {vals} {where} are < x"),
    ("CountLteX", "countLteX", ["x"], "sum", "how many {vals} {where} are <= x"),
    ("CountGtX", "countGtX", ["x"], "sum", "how many {vals} {where} are > x"),
    ("CountGteX", "countGteX", ["x"], "sum", "how many {vals} {where} are >= x"),
    ("CountInValRange", "countInValRange", ["low", "high"], "sum", "how many {vals} {where} are in [low, high]"),
    ("SumLtX", "sumLtX", ["x"], "sum", "sum of the {vals} {where} that are < x"),
    ("SumLteX", "sumLteX", ["x"], "sum", "sum of the {vals} {where} that are <= x"),
    ("SumGtX", "sumGtX", ["x"], "sum", "sum of the {vals} {where} that are > x"),
    ("SumGteX", "sumGteX", ["x"], "sum", "sum of the {vals} {where} that are >= x"),
    ("SumInValRange", "sumInValRange", ["low", "high"], "sum", "sum of the {vals} {where} in [low, high]"),
    ("SumSmallestK", "sumSmallestK", ["k"], None, "sum of the k smallest {vals} {where}"),
    ("SumLargestK", "sumLargestK", ["k"], None, "sum of the k largest {vals} {where}"),
    ("SumKthSmallestRange", "sumKthSmallestRange", ["kFrom", "kTo"], None,
     "sum of the kFrom-th ... kTo-th smallest {vals} {where} (1-indexed)"),
    ("SumKthLargestRange", "sumKthLargestRange", ["kFrom", "kTo"], None,
     "sum of the kFrom-th ... kTo-th largest {vals} {where} (1-indexed)"),
    ("SumAbsDiffToX", "sumAbsDiffToX", ["x"], "sum", "sum of |{val} - x| over the {vals} {where}"),
    ("SumAbsDiffToMedian", "sumAbsDiffToMedian", [], None, "sum of |{val} - median| over the {vals} {where}"),
    ("SmallestGteX", "smallestGteX", ["x"], "nearest<", "smallest of the {vals} {where} that is >= x ({none} if none)"),
    ("SmallestGtX", "smallestGtX", ["x"], "nearest<", "smallest of the {vals} {where} that is > x ({none} if none)"),
    ("LargestLteX", "largestLteX", ["x"], "nearest>", "largest of the {vals} {where} that is <= x ({none} if none)"),
    ("LargestLtX", "largestLtX", ["x"], "nearest>", "largest of the {vals} {where} that is < x ({none} if none)"),
    ("CountOccurrences", "countOccurrences", ["x"], "sum", "how many {vals} {where} equal x"),
    ("CountDistinct", "countDistinct", [], None, "number of distinct {vals} {where}"),
    ("AllDistinct", "allDistinct", [], None, "are all the {vals} {where} distinct?"),
    ("Mode", "rangeMode", [], None, "(mode, frequency) of the {vals} {where}"),
    ("AllEvenFrequency", "doAllElementsAppearEvenFrequency", [], None,
     "does every value appear an even number of times {where}?"),
    ("Mex", "rangeMex", [], None, "smallest integer >= 0 missing from the {vals} {where}"),
    ("XOR", "rangeXorQuery", [], "xor", "xor of the {vals} {where}"),
    ("AND", "rangeAndQuery", [], "and", "AND of the {vals} {where}"),
    ("OR", "rangeOrQuery", [], "or", "OR of the {vals} {where}"),
    ("MaxXorAgainstX", "maxXorAgainstX", ["x"], "max", "largest {val} ^ x over the {vals} {where}"),
    ("MinXorAgainstX", "minXorAgainstX", ["x"], "min", "smallest {val} ^ x over the {vals} {where}"),
]
# not on the menu for a path (no fast online way), so a path never gets them even where pieces could combine
SUBTREE_ONLY = {"Mode", "Mex"}
# the comparisons a search can make: (suffix, sign, the range ops that scan a range from its left / from its right)
SEARCHES = [(f"{c}X", sign, f"leftmost{c}X", f"rightmost{c}X") for c, sign in
            (("Gte", ">="), ("Gt", ">"), ("Lte", "<="), ("Lt", "<"))]
SEARCHES.append(("EqX", "=", "leftmostIndexOfInRange", "rightmostIndexOfInRange"))
PREFIX_SEARCHES = [(f"{c}X", sign, f"leftmostPrefixSum{c}X", f"rightmostSuffixSum{c}X") for c, sign in
                   (("Gte", ">="), ("Gt", ">"), ("Lte", "<="), ("Lt", "<"))]

# how a path's pieces combine: fold -> (Python start value, Python step with V = this piece's answer,
#                                       C++ result type R's start value, C++ step with v = this piece's answer)
PATH_FOLDS = {
    "sum": ("0", "res += V", "0", "res += v;"),
    "summod": ("0", "res = (res + V) % self.mod", "0", "res = (res + v) % modulus;"),
    "min": ('float("inf")', "v = V\nif v < res:\n    res = v", "numeric_limits<R>::max()", "if (v < res) res = v;"),
    "max": ('float("-inf")', "v = V\nif v > res:\n    res = v", "numeric_limits<R>::lowest()", "if (v > res) res = v;"),
    "gcd": ("0", "res = gcd(res, V)", "0", "res = std::gcd(res, v);"),
    "xor": ("0", "res ^= V", "0", "res ^= v;"),
    "or": ("0", "res |= V", "0", "res |= v;"),
    "and": ("-1", "res &= V", "~R(0)", "res &= v;"),
    # (the range op answers None / nullopt when a piece has no such value)
    "nearest<": ("None", "v = V\nif v is not None and (res is None or v < res):\n    res = v", "R()",
                 "if (v && (!res || *v < *res)) res = v;"),
    "nearest>": ("None", "v = V\nif v is not None and (res is None or v > res):\n    res = v", "R()",
                 "if (v && (!res || *v > *res)) res = v;"),
}

# What an edge query answers when it has no edges to look at (a path a..a, a leaf's subtree), by how its pieces combine:
# (Python value, C++ value of the result type R, how the comment says it in Python, in C++). The values are the ones
# PATH_FOLDS starts from, so a path needs no extra code; a subtree returns them itself.
EMPTY = {
    "sum": ("0", "R(0)", "0", "0"),
    "min": ('float("inf")', "numeric_limits<R>::max()", "inf", "the largest value of its type"),
    "max": ('float("-inf")', "numeric_limits<R>::lowest()", "-inf", "the smallest value of its type"),
    "and": ("-1", "~R(0)", "-1 (every bit set)", "-1 (every bit set)"),
    "nearest<": ("None", "R()", "None", "nullopt"),
    "true": ("True", "true", "True", "true"),
}
EMPTY.update({fold: EMPTY["sum"] for fold in ("summod", "gcd", "xor", "or")})
EMPTY["nearest>"] = EMPTY["nearest<"]
WORD = {key: re.sub(r"\W", "", key) + ("lo" if "<" in key else "hi" if ">" in key else "") for key in EMPTY}  # a name for each
# queries a path cannot answer piece by piece but that still mean something on no edges; every other such query
# (kth smallest, mode, ...) raises when there are no edges
EMPTY_OTHER = {"CountDistinct": "sum", "Mex": "sum", "AllDistinct": "true", "AllEvenFrequency": "true"}

SHAPE_OPS = sorted(shape.COSTS)  # every value template has every shape op too (the layout is already there)
LAYOUT_ARRAYS = f"{shape.LAYOUT_ARRAYS} {shape.OTHER_ARRAYS[0]}"

# ------------------------------------------------------------------------------------------------ costs
FACTOR_VALUES = {"1": 1, "α(N)": 3, "K": 20, "N": 2e5, "log(N)": 17.6, "log^2(N)": 17.6 ** 2, "log^3(N)": 17.6 ** 3,
                 "sqrt(N)": 447, "sqrt(NlogN)": 1876, "sqrt(N/logN)": 107, "U": 1e9, "U/64": 1e9 / 64, "log(U)": 30,
                 "log64(U)": 5, "log(log(U))": 5, "U^(1/4)": 178}
SUFFIX = re.compile(r"( (?:amortized expected|amortized|expected))?( \?)?$")


def split_cost(cost):
    m = SUFFIX.search(cost)
    return cost[:m.start()], cost[m.start():]


def cost_value(cost):
    total = 0
    for term in split_cost(cost)[0].split("+"):
        prod = 1
        for f in term.split("*"):
            prod *= float(f) if f.isdigit() else FACTOR_VALUES[f]
        total += prod
    return total


def times_log(cost):
    """cost * log(N), as a cost string the site can read (log(N) * log(N) is written log^2(N), and so on)."""
    body, suffix = split_cost(cost)
    up = {"log(N)": "log^2(N)", "log^2(N)": "log^3(N)"}
    terms = []
    for term in body.split("+"):
        fs = term.split("*")
        k = next((i for i, f in enumerate(fs) if f in up), None)
        if k is not None:
            fs[k] = up[fs[k]]
        elif fs == ["1"]:
            fs = ["log(N)"]
        else:
            fs.append("log(N)")
        terms.append("*".join(fs))
    return "+".join(terms) + suffix


def worst(*costs):
    return max(costs, key=cost_value)


PRETTY = {"N": "n", "log(N)": "log n", "log^2(N)": "log^2 n", "log^3(N)": "log^3 n", "sqrt(N)": "sqrt(n)",
          "sqrt(NlogN)": "sqrt(n log n)", "sqrt(N/logN)": "sqrt(n / log n)", "log(U)": "log U", "log64(U)": "log64 U",
          "log(log(U))": "log log U"}


def big_o(cost):
    """A cost string as it reads in a comment: "log^2(N)" -> "O(log^2 n)"."""
    body = split_cost(cost)[0]
    return "O(" + " + ".join(" * ".join(PRETTY.get(f, f) for f in term.split("*")) for term in body.split("+")) + ")"


# ------------------------------------------------------------------------------------------------ reading a range folder
def split_top(s):
    """"a, b = f(1, 2), vector<pair<int, T>> c" -> its top-level comma-separated pieces."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def paren_args(text, at):
    """The text between the "(" at or after index at and its matching ")"."""
    start = text.index("(", at)
    depth = 0
    for k in range(start, len(text)):
        if text[k] == "(":
            depth += 1
        elif text[k] == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1:k]
    raise ValueError("unbalanced parentheses")


def read_header(text, cm):
    """ops, type, {op: cost} (with "build") and the @memory fields of a template's header."""
    tags, blocks, block = {}, {"complexities": {}, "memory": {}}, None
    for line in text.split("\n"):
        m = re.match(rf"\s*{re.escape(cm)} @([a-z-]+):\s*(.*?)\s*$", line)
        if m:
            tags[m.group(1)] = m.group(2)
            block = m.group(1) if m.group(1) in blocks else None
            continue
        m = block and re.match(rf"\s*{re.escape(cm)}\s+([A-Za-z]\w*):\s*(.+?)\s*$", line)
        if m:
            blocks[block][m.group(1)] = m.group(2)
        elif tags and not line.strip().startswith(cm):
            break
    return tags["operations"].split(), tags["data-structure-type"], blocks["complexities"], blocks["memory"]


class Range:
    """One range-query folder: its ops, costs, and the class a Tree wraps (None for .cls when it cannot be wrapped)."""

    def __init__(self, folder):
        self.folder = folder
        base = os.path.join(RANGE_DIR, folder)
        self.py = open(os.path.join(base, "template.py"), encoding="utf-8").read()
        fast = os.path.join(base, "fast.cpp")
        self.cpp_name = "fast.cpp" if os.path.exists(fast) else "template.cpp"
        self.cpp = open(os.path.join(base, self.cpp_name), encoding="utf-8").read()
        self.ops, self.kind, self.costs, self.memory = read_header(self.py, "#")
        self.cls = self.why = None
        if SEQUENCE_OPS & set(self.ops):
            self.why = "edits the sequence"
            return
        # the Python class holding the ops, its constructor and methods
        classes, cur = [], None
        for line in self.py.split("\n"):
            m = re.match(r"class (\w+)", line)
            if m:
                cur = {"name": m.group(1), "ctor": None, "methods": set()}
                classes.append(cur)
                continue
            if re.match(r"[^\s#]", line):
                cur = None
            m = cur and re.match(r"    def (\w+)\(self(?:,\s*)?(.*)\):", line)
            if m and m.group(1) == "__init__":
                cur["ctor"] = m.group(2)
            elif m:
                cur["methods"].add(m.group(1))
        owners = [c for c in classes if c["methods"] & set(self.ops)]
        if len(owners) != 1 or owners[0]["ctor"] is None:
            self.why = "its ops are split over several classes"
            return
        owner = owners[0]
        params = split_top(owner["ctor"])
        self.py_extra = params[1:]  # "mod=10**9 + 7", "valLo", ...
        names = [p.split("=")[0].strip() for p in self.py_extra]
        if not params or set(names) - PASS_THROUGH:
            self.why = f"constructor takes ({owner['ctor']})"
            return
        self.extra_names = names
        self.methods = owner["methods"]
        # the same struct in C++: its constructor's extra arguments and each op's argument types
        at = self.cpp.find(f"template <typename T>\nstruct {owner['name']} {{")
        if at < 0:
            self.why = f"no C++ struct {owner['name']}<T>"
            return
        body = self.cpp[at:]
        ctor = re.search(rf"^    (?:explicit )?{owner['name']}\((?=const vector<T>&)", body, re.M)
        if not ctor:
            self.why = "no C++ constructor from a vector"
            return
        cparams = split_top(paren_args(body, ctor.start()))
        self.cpp_extra = cparams[1:]  # "T mod = 1000000007", "long long valLo", ...
        cnames = [re.match(r".*?(\w+)\s*(?:=.*)?$", p).group(1) for p in self.cpp_extra]
        if cnames != names:
            self.why = f"constructor arguments differ: Python {names}, C++ {cnames}"
            return
        self.cpp_args, documented = {}, set()
        for m in re.finditer(r"^    (?:LEETCODE_NO_SANITIZE )?[\w:<>, *&]+? (\w+)\(", body, re.M):
            op = m.group(1)
            # (an op may have a private overload too: the public one is the one with a comment right above it)
            public = body[:m.start()].rstrip("\n").rsplit("\n", 1)[-1].lstrip().startswith("//")
            if op in self.ops and (op not in self.cpp_args or (public and op not in documented)):
                self.cpp_args[op] = [re.match(r"(.*?)\s*\b\w+$", p.split("=")[0].strip()).group(1) for p in
                                     split_top(paren_args(body, m.start()))]
                if public:
                    documented.add(op)
        self.cls = owner["name"]

    def has(self, *ops):
        return all(op in self.methods and op in self.cpp_args for op in ops)

    def extra_types(self, op, skip):
        """The C++ types of op's arguments after its first skip ones (the index, or l and r)."""
        return self.cpp_args[op][skip:]

    def py_inner(self):
        """template.py without its header: the description, the imports, the class."""
        return self.py[self.py.index("\n\n") + 2:]

    def cpp_inner(self):
        """The C++ file without its header and includes; the fast-mode note goes (the tree file has its own)."""
        t = self.cpp[self.cpp.index("\n\n", self.cpp.index("// @operations:")) + 2:]
        if "FAST MODE drawbacks" in t:
            t, hits = re.subn(r"// FAST MODE drawbacks compared with [\w.-]+:\n(?://.*\n)*?// Same public operations"
                              r"(?:.*\n)(?://.*C\+\+17\.\n)?", "", t)
            assert hits == 1 and "FAST MODE drawbacks" not in t, f"{self.folder}: fast-mode note not removed"
        return t


# ------------------------------------------------------------------------------------------------ one tree op
class Op:
    """A tree op for one folder: its name, args, cost, doc and the two method texts."""

    def __init__(self, name, args, cost, doc, py, cpp, returns=False):
        self.name, self.args, self.cost, self.doc, self.py, self.cpp = name, args, cost, doc, py, cpp
        self.returns = returns  # it answers something (a template whose ops are all updates has nothing to read)


def indent(text, by):
    return "\n".join(by * " " + line if line else line for line in text.split("\n"))


def py_check(name, nodes):
    if len(nodes) > 3:  # (four nodes: the bounds as locals, to stay within the line)
        cond = " and ".join(f"lo <= {v} <= hi" for v in nodes)
        return ("        lo, hi = self.lo, self.hi\n"
                f"        if not ({cond}):\n            self._bad(\"{name}\", {', '.join(nodes)})\n")
    cond = " and ".join(f"self.lo <= {v} <= self.hi" for v in nodes)
    if len(nodes) > 1:
        cond = f"({cond})"
    return f"        if not {cond}:\n            self._bad(\"{name}\", {', '.join(nodes)})\n"


def cpp_check(name, nodes):
    return f"        if ({' || '.join(f'{v} < lo || {v} > hi' for v in nodes)}) bad(\"{name}\");\n"


def comment(cm, cost, doc, width=120, pad=4):
    """"<cm> O(cost) -- doc", wrapped to the line width."""
    words = f"{big_o(cost)} -- {doc}".split(" ")
    lines, cur = [], f"{' ' * pad}{cm}"
    for w in words:
        if len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = f"{' ' * pad}{cm}"
        cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


# the walk a -> b one chain piece at a time, in order: UP is a piece on a's side (positions l..r, read from r down to
# l), DOWN a piece on b's side (read from l up to r). Both snippets see l and r.
PY_WALK = '''\
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
@UP@
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
@UP2@
        else:
            l, r = pos[a], pos[b]
@DOWN2@
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
@DOWN@
'''
CPP_WALK = '''\
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
@UP@
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
@UP2@
        } else {
            int l = pos[a], r = pos[b];
@DOWN2@
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
@DOWN@
        }
'''


# for edges, the piece holding the lca starts one position after the lca (the lca's own position is the edge above it)
EDGE_LCA_PIECE = {
    PY_WALK: (("        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top\n            l, r = pos[b], pos[a]\n",
               "        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position\n"
               "            l, r = pos[b] + 1, pos[a]\n"),
              ("        else:\n            l, r = pos[a], pos[b]\n",
               "        elif pos[a] < pos[b]:\n            l, r = pos[a] + 1, pos[b]\n")),
    CPP_WALK: (("        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top\n            int l = pos[b], r = pos[a];\n",
                "        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position\n"
                "            int l = pos[b] + 1, r = pos[a];\n"),
               ("        } else {\n            int l = pos[a], r = pos[b];\n",
                "        } else if (pos[a] < pos[b]) {\n            int l = pos[a] + 1, r = pos[b];\n")),
}


def walk(template, up, down, edge=False):
    """The ordered walk with the two snippets put in at their indentation (16 in the loops, 12 after them)."""
    text = template
    if edge:
        for old, new in EDGE_LCA_PIECE[template]:
            assert text.count(old) == 1, old
            text = text.replace(old, new)
    return (text.replace("@UP@", indent(up, 16)).replace("@UP2@", indent(up, 12))
            .replace("@DOWN2@", indent(down, 12)).replace("@DOWN@", indent(down, 12)))


# the Tree's own fields: no method argument may share a name with one (in C++ it would hide it)
MEMBERS = {"n", "lo", "hi", "root", "par", "dep", "sz", "head", "pos", "order", "depthStart", "depthPos", "seg", "modulus",
           "mod", "nodeSeg", "edgeSeg", "hashPow"}


class Maker:
    """Builds every tree op one range folder supports, for one target ("node" or "edge")."""

    def __init__(self, rng, target="node"):
        self.r, self.t, self.edge = rng, target, target == "edge"
        self.words = ({"val": "weight", "vals": "edge weights", "one": "edge", "value": "weight", "x": "w", "at": "a - b"}
                      if self.edge else
                      {"val": "val", "vals": "node values", "one": "node", "value": "value", "x": "x", "at": "node"})
        self.ops, self.odd = [], []  # odd: ops left out because the range method's arguments are not as expected
        self.helpers = []  # (Python name, C++ name) of each private walk it wrote (a both- template renames them)

    def walk(self, template, up, down):
        return walk(template, up, down, self.edge)

    def empty(self, suffix, fold, where):
        """(the EMPTY entry or None, the words a query's comment ends with) for an edge query on no edges."""
        if not self.edge:
            return None, ""
        when = "a == b" if where == "path" else "node is a leaf"
        key = fold or EMPTY_OTHER.get(suffix)
        if key is None:
            return None, f"; needs at least one edge (not {when}), else {{raises}}"
        return EMPTY[key], f"; {{empty_{WORD[key]}}} when {when} (no edges)"

    def text(self, s, where="", lang="py"):
        py = lang == "py"
        w = dict(self.words, where=where, none="None" if py else "nullopt",
                 raises="IndexError" if py else "throws out_of_range")
        w.update({f"empty_{WORD[key]}": e[2 if py else 3] for key, e in EMPTY.items()})
        return s.format(**w)

    def add(self, name, args, cost, doc, py_body, cpp_body, cpp_types, cpp_ret="auto", nodes=("node",), where="",
            check=True):
        """A public method: the node checks (unless the body does its own), then the body (already indented by 8)."""
        full = self.t + name
        taken = set(args) & MEMBERS
        assert not taken, f"{full}: an argument named {taken} would hide the Tree's own field"
        if len(cpp_types) != len(args):
            self.odd.append(f"{full}: the range method takes {cpp_types} where ({', '.join(args)}) was expected")
            return
        params = list(nodes) + args
        py = (comment("#", cost, self.text(doc, where, "py")) + f"    def {full}(self, {', '.join(params)}):\n"
              + (py_check(full, nodes) if check else "") + py_body)
        decl = ", ".join([f"int {v}" for v in nodes] + [f"{ty} {a}" for ty, a in zip(cpp_types, args)])
        cpp = (comment("//", cost, self.text(doc, where, "cpp")) + f"    LEETCODE_NO_SANITIZE {cpp_ret} {full}({decl}) {{\n"
               + (cpp_check(full, nodes) if check else "") + cpp_body + "    }\n")
        self.ops.append(Op(full, params, cost, doc, py, cpp, returns=cpp_ret != "void"))

    def cost(self, op):
        return self.r.costs[op]

    # ---- one node, or one edge (kept at its lower end: the helper finds which end that is)
    def point(self):
        r = self.r
        if self.edge and any(r.has(op) for _, op, _, _ in POINT):
            self.ops.append(Op(None, None, None, None,
                               "    # the position that holds the edge a - b: its lower end's (a and b in either order)\n"
                               "    def _edge(self, name, a, b):\n"
                               "        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):\n"
                               "            self._bad(name, a, b)\n"
                               "        if self.par[a] == b:\n"
                               "            return self.pos[a]\n"
                               "        if self.par[b] == a:\n"
                               "            return self.pos[b]\n"
                               '        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")\n',
                               "    // the position that holds the edge a - b: its lower end's (a and b in either order)\n"
                               "    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {\n"
                               "        if (a < lo || a > hi || b < lo || b > hi) bad(name);\n"
                               "        if (par[a] == b) return pos[a];\n"
                               "        if (par[b] == a) return pos[b];\n"
                               '        throw out_of_range(string(name) + ": needs an edge between a and b");\n'
                               "    }\n"))
        for suffix, op, args, doc in POINT:
            if not r.has(op):
                continue
            args = [self.text(a) for a in args]
            full = self.t + suffix
            at, cat = (f'self._edge("{full}", a, b)', f'edgeAt("{full}", a, b)') if self.edge else ("self.pos[node]", "pos[node]")
            call = f"self.seg.{op}({', '.join([at] + args)})"
            ccall = f"seg.{op}({', '.join([cat] + args)})"
            ret = "return " if suffix == "Get" else ""
            if self.edge:
                doc += "; a and b are the edge's two ends, in either order"
            self.add(suffix, args, self.cost(op), doc, f"        {ret}{call}\n", f"        {ret}{ccall};\n",
                     r.extra_types(op, 1), "auto" if suffix == "Get" else "void",
                     nodes=("a", "b") if self.edge else ("node",), check=not self.edge)

    # ---- a subtree: one range op (for edges: without the subtree's own top, whose position is the edge above it)
    def subtree(self):
        r = self.r
        entries = [(s, op, a, f"{d} for every {{one}} in node's subtree", None, False) for s, op, a, d in UPDATES]
        entries += [(s, op, a, d, fold, True) for s, op, a, fold, d in QUERIES]
        for suffix, op, args, doc, fold, query in entries:
            if not r.has(op):
                continue
            args = [self.text(a) for a in args]
            tail = "".join(f", {a}" for a in args)
            ret = "return " if query else ""
            if not self.edge:
                py = f"        l = self.pos[node]\n        {ret}self.seg.{op}(l, l + self.sz[node] - 1{tail})\n"
                cpp = f"        int l = pos[node];\n        {ret}seg.{op}(l, l + sz[node] - 1{tail});\n"
            else:
                full = f"{self.t}Subtree{suffix}"
                empty, words = self.empty(suffix, fold, "subtree") if query else (None, "")
                doc += words
                if not query:
                    py_none, cpp_none = "return", "if (l > r) return;"
                elif empty:
                    py_none = f"return {empty[0]}"
                    cpp_none = f"using R = decltype(seg.{op}(0, 0{tail}));\n        if (l > r) return R({empty[1]});"
                    if empty[1].startswith(("R(", "numeric_limits", "~R")):
                        cpp_none = f"using R = decltype(seg.{op}(0, 0{tail}));\n        if (l > r) return {empty[1]};"
                else:
                    msg = f"{full}: needs at least one edge in node's subtree"
                    py_none, cpp_none = f'raise IndexError("{msg}")', f'if (l > r) throw out_of_range("{msg}");'
                py = ("        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1\n"
                      "        if l > r:  # a leaf: no edges below it\n"
                      f"            {py_none}\n"
                      f"        {ret}self.seg.{op}(l, r{tail})\n")
                cpp = ("        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)\n"
                       f"        {cpp_none}\n"
                       f"        {ret}seg.{op}(l, r{tail});\n")
            self.add("Subtree" + suffix, args, self.cost(op), doc, py, cpp, r.extra_types(op, 2),
                     "auto" if query else "void", where="in node's subtree")

    # ---- a path: the same update on every piece, or the pieces' answers combined (the order does not matter)
    def path_unordered(self):
        r = self.r
        for suffix, op, args, doc in UPDATES:
            if r.has(op):
                self.unordered(suffix, op, [self.text(a) for a in args], f"{doc} for every {{one}} on the path a..b", None)
        for suffix, op, args, fold, doc in QUERIES:
            if fold and suffix not in SUBTREE_ONLY and r.has(op) and (fold != "summod" or "mod" in r.extra_names):
                self.unordered(suffix, op, args, doc + self.empty(suffix, fold, "path")[1], fold)

    def unordered(self, suffix, op, args, doc, fold):
        tail = "".join(f", {a}" for a in args)
        if fold:
            start, step, cstart, cstep = PATH_FOLDS[fold]
            py_step = lambda call: indent(step.replace("V", call), 0)  # noqa: E731
            py = (f"        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.{op}\n"
                  f"        res = {start}\n"
                  "        while head[a] != head[b]:\n"
                  "            if dep[head[a]] < dep[head[b]]:\n"
                  "                a, b = b, a\n"
                  + indent(py_step(f"query(pos[head[a]], pos[a]{tail})"), 12) + "\n"
                  "            a = par[head[a]]\n"
                  "        l, r = pos[a], pos[b]\n"
                  "        if l > r:\n"
                  "            l, r = r, l\n"
                  + (("        if l < r:  # (the lca's own position is the edge above it)\n"
                      + indent(py_step(f"query(l + 1, r{tail})"), 12)) if self.edge else indent(py_step(f"query(l, r{tail})"), 8))
                  + "\n        return res\n")
            cpp = (f"        using R = decltype(seg.{op}(0, 0{tail}));\n"
                   f"        R res = {cstart};\n"
                   "        while (head[a] != head[b]) {\n"
                   "            if (dep[head[a]] < dep[head[b]]) {\n"
                   "                int t = a;\n"
                   "                a = b, b = t;\n"
                   "            }\n"
                   f"            R v = seg.{op}(pos[head[a]], pos[a]{tail});\n"
                   f"            {cstep}\n"
                   "            a = par[head[a]];\n"
                   "        }\n"
                   "        int l = pos[a], r = pos[b];\n"
                   "        if (l > r) {\n"
                   "            int t = l;\n"
                   "            l = r, r = t;\n"
                   "        }\n"
                   + (("        if (l < r) {  // (the lca's own position is the edge above it)\n"
                       f"            R v = seg.{op}(l + 1, r{tail});\n"
                       f"            {cstep}\n"
                       "        }\n") if self.edge else
                      (f"        R v = seg.{op}(l, r{tail});\n"
                       f"        {cstep}\n"))
                   + "        return res;\n")
        else:
            py = (f"        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.{op}\n"
                  "        while head[a] != head[b]:\n"
                  "            if dep[head[a]] < dep[head[b]]:\n"
                  "                a, b = b, a\n"
                  f"            apply(pos[head[a]], pos[a]{tail})\n"
                  "            a = par[head[a]]\n"
                  "        l, r = pos[a], pos[b]\n"
                  + (("        if l != r:  # (the lca's own position is the edge above it)\n"
                      f"            apply(l + 1, r{tail}) if l < r else apply(r + 1, l{tail})\n") if self.edge else
                     f"        apply(l, r{tail}) if l <= r else apply(r, l{tail})\n"))
            cpp = ("        while (head[a] != head[b]) {\n"
                   "            if (dep[head[a]] < dep[head[b]]) {\n"
                   "                int t = a;\n"
                   "                a = b, b = t;\n"
                   "            }\n"
                   f"            seg.{op}(pos[head[a]], pos[a]{tail});\n"
                   "            a = par[head[a]];\n"
                   "        }\n"
                   "        int l = pos[a], r = pos[b];\n"
                   + ((f"        if (l < r) seg.{op}(l + 1, r{tail});  // (the lca's own position is the edge above it)\n"
                       f"        else if (l > r) seg.{op}(r + 1, l{tail});\n") if self.edge else
                      (f"        if (l <= r) seg.{op}(l, r{tail});\n"
                       f"        else seg.{op}(r, l{tail});\n")))
        self.add("Path" + suffix, args, times_log(self.cost(op)), doc, py, cpp, self.r.extra_types(op, 2),
                 "auto" if fold else "void", nodes=("a", "b"), where="on the path a..b")

    # ---- a path, walked in order
    def path_arith(self):
        r = self.r
        for suffix, op, mod in (("AddArithSeq", "rangeAddArithSeq", False), ("AddArithSeqMod", "rangeAddArithSeqMod", True)):
            if not r.has(op) or (mod and "mod" not in r.extra_names):
                continue
            # a piece read backwards gets the sequence from its far end, with the step negated
            if mod:
                up = "apply(l, r, (start + (done + r - l) * step) % mod, -step % mod)\ndone += r - l + 1"
                down = "apply(l, r, (start + done * step) % mod, step % mod)\ndone += r - l + 1"
                cup = ("T first = (start + (T)((done + r - l) % modulus) * step) % modulus;\n"
                       f"seg.{op}(l, r, first, (modulus - step) % modulus);\ndone += r - l + 1;")
                cdown = (f"T first = (start + (T)(done % modulus) * step) % modulus;\nseg.{op}(l, r, first, step);\n"
                         "done += r - l + 1;")
                pre = "        mod = self.mod\n"
                cpre = "        start %= modulus, step %= modulus;  // (both >= 0)\n"
            else:
                up = "apply(l, r, start + (done + r - l) * step, -step)\ndone += r - l + 1"
                down = "apply(l, r, start + done * step, step)\ndone += r - l + 1"
                cup = f"seg.{op}(l, r, start + (T)(done + r - l) * step, -step);\ndone += r - l + 1;"
                cdown = f"seg.{op}(l, r, start + (T)done * step, step);\ndone += r - l + 1;"
                pre = cpre = ""
            py = (f"        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.{op}\n" + pre
                  + f"        done = 0  # how many {self.words['one']}s of the walk already have their term\n" + self.walk(PY_WALK, up, down))
            cpp = cpre + f"        long long done = 0;  // how many {self.words['one']}s of the walk already have their term\n" + self.walk(CPP_WALK, cup, cdown)
            doc = ("walking a -> b, the {one}s get start, start + step, start + 2 * step, ... added"
                   + (" (mod MOD; needs start, step >= 0)" if mod else ""))
            types = r.extra_types(op, 2)
            self.add("Path" + suffix, ["start", "step"], times_log(self.cost(op)), doc, py, cpp, types, "void", nodes=("a", "b"))

    def searches(self):
        r = self.r
        for table, kind in ((SEARCHES, "value"), (PREFIX_SEARCHES, "prefix")):
            for suffix, sign, left, right in table:
                acc = kind == "prefix"
                need = (left, right, "rangeSum") if acc else (left, right)
                # up the chains only: the nearest ancestor (a value search needs just the right-to-left op)
                if not acc and r.has(right):
                    if self.edge:  # (position 0 is the root's: it holds no edge)
                        py = ("        head, par, pos, find = self.head, self.par, self.pos, self.seg." + right + "\n"
                              "        while node != -1:\n"
                              "            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)\n"
                              "            if l <= pos[node]:\n"
                              "                i = find(l, pos[node], x)\n"
                              "                if i != -1:\n"
                              "                    return self.order[i]\n"
                              "            node = par[head[node]]\n"
                              "        return -1\n")
                        cpp = ("        while (node != -1) {\n"
                               "            int l = pos[head[node]] ? pos[head[node]] : 1;  // (position 0 is the root's: it holds no edge)\n"
                               "            if (l <= pos[node]) {\n"
                               f"                int i = seg.{right}(l, pos[node], x);\n"
                               "                if (i != -1) return order[i];\n"
                               "            }\n"
                               "            node = par[head[node]];\n"
                               "        }\n"
                               "        return -1;\n")
                        near = f"nearest edge above node (toward the root) with {{val}} {sign} x, as its lower end (-1 if none)"
                    else:
                        py = ("        head, par, pos, find = self.head, self.par, self.pos, self.seg." + right + "\n"
                              "        while node != -1:\n"
                              "            i = find(pos[head[node]], pos[node], x)\n"
                              "            if i != -1:\n"
                              "                return self.order[i]\n"
                              "            node = par[head[node]]\n"
                              "        return -1\n")
                        cpp = ("        while (node != -1) {\n"
                               f"            int i = seg.{right}(pos[head[node]], pos[node], x);\n"
                               "            if (i != -1) return order[i];\n"
                               "            node = par[head[node]];\n"
                               "        }\n"
                               "        return -1;\n")
                        near = f"nearest ancestor of node (node included) with {{val}} {sign} x (-1 if none)"
                    self.add("NearestAncestor" + suffix, ["x"], times_log(self.cost(right)), near, py, cpp,
                             r.extra_types(right, 2), "int")
                if not r.has(*need):
                    continue
                cost = times_log(worst(*[self.cost(o) for o in need]))
                types = r.extra_types(left, 2)
                if acc:
                    up = ("i = last(l, r, x - run)\nif i != -1:\n    return order[i]\nrun += total(l, r)")
                    down = ("i = first(l, r, x - run)\nif i != -1:\n    return order[i]\nrun += total(l, r)")
                    cup = (f"int i = seg.{right}(l, r, x - run);\nif (i != -1) return order[i];\nrun += seg.rangeSum(l, r);")
                    cdown = (f"int i = seg.{left}(l, r, x - run);\nif (i != -1) return order[i];\nrun += seg.rangeSum(l, r);")
                    head = ("        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order\n"
                            "        seg = self.seg\n"
                            f"        first, last, total = seg.{left}, seg.{right}, seg.rangeSum\n"
                            "        run = 0  # the sum of the pieces already walked\n")
                    chead = "        decltype(seg.rangeSum(0, 0)) run = 0;  // the sum of the pieces already walked\n"
                    helper, what = f"_firstPrefixSum{suffix}", f"the sum from a to it is {sign} x"
                else:
                    up = "i = last(l, r, x)\nif i != -1:\n    return order[i]"
                    down = "i = first(l, r, x)\nif i != -1:\n    return order[i]"
                    cup = f"int i = seg.{right}(l, r, x);\nif (i != -1) return order[i];"
                    cdown = f"int i = seg.{left}(l, r, x);\nif (i != -1) return order[i];"
                    head = ("        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order\n"
                            f"        first, last = self.seg.{left}, self.seg.{right}\n")
                    chead = ""
                    helper, what = f"_first{suffix}", f"{{val}} {sign} x"
                # the private walk a -> b, then the public ops: first on a -> b, and last = first on b -> a
                chelper = helper[1:]
                self.helpers.append((helper, chelper))
                self.ops.append(Op(None, None, None, None,
                                   f"    def {helper}(self, a, b, x):\n" + head + self.walk(PY_WALK, up, down) + "        return -1\n",
                                   f"    LEETCODE_NO_SANITIZE int {chelper}(int a, int b, {types[0]} x) {{\n" + chead
                                   + self.walk(CPP_WALK, cup, cdown) + "        return -1;\n    }\n"))
                needs = " (needs every {val} >= 0)" if acc and sign in (">=", ">") else ""
                if acc:
                    names = ((f"FirstPrefixSum{suffix}", "a, b", f"first {{one}} walking a -> b where the sum from a to it is {sign} x"),
                             (f"LastSuffixSum{suffix}", "b, a", f"last {{one}} walking a -> b where the sum from it to b is {sign} x"))
                else:
                    names = ((f"First{suffix}", "a, b", f"first {{one}} walking a -> b with {what}"),
                             (f"Last{suffix}", "b, a", f"last {{one}} walking a -> b with {what}"))
                found = ", as its lower end (-1 if none)" if self.edge else " (-1 if none)"
                for name, order_, doc in names:
                    self.add("Path" + name, ["x"], cost, doc + found + needs,
                             f"        return self.{helper}({order_}, x)\n", f"        return {chelper}({order_}, x);\n",
                             types, "int", nodes=("a", "b"))

    def prefix_sums(self):
        r = self.r
        for big, sign in (("Max", ">"), ("Min", "<")):
            pre, suf = f"{big.lower()}PrefixSum", f"{big.lower()}SuffixSum"
            if not r.has(pre, suf, "rangeSum"):
                continue
            cost = times_log(worst(self.cost(pre), self.cost(suf), self.cost("rangeSum")))
            start = 'float("-inf")' if big == "Max" else 'float("inf")'
            cstart = "numeric_limits<R>::lowest()" if big == "Max" else "numeric_limits<R>::max()"
            up = f"v = run + ending(l, r)\nif v {sign} best:\n    best = v\nrun += total(l, r)"
            down = f"v = run + starting(l, r)\nif v {sign} best:\n    best = v\nrun += total(l, r)"
            cup = f"R v = run + seg.{suf}(l, r);\nif (v {sign} best) best = v;\nrun += seg.rangeSum(l, r);"
            cdown = f"R v = run + seg.{pre}(l, r);\nif (v {sign} best) best = v;\nrun += seg.rangeSum(l, r);"
            helper = f"_{big.lower()}PrefixSum"
            self.helpers.append((helper, helper[1:]))
            # a piece read backwards: its prefixes along the walk are its suffixes in the array
            self.ops.append(Op(None, None, None, None,
                               f"    def {helper}(self, a, b):\n"
                               "        head, par, dep, pos = self.head, self.par, self.dep, self.pos\n"
                               f"        starting, ending, total = self.seg.{pre}, self.seg.{suf}, self.seg.rangeSum\n"
                               f"        run, best = 0, {start}  # the sum of the pieces already walked; the best prefix so far\n"
                               + self.walk(PY_WALK, up, down) + "        return best\n",
                               f"    LEETCODE_NO_SANITIZE auto {helper[1:]}(int a, int b) {{\n"
                               "        using R = decltype(seg.rangeSum(0, 0));\n"
                               f"        R run = 0, best = {cstart};  // the sum of the pieces already walked; the best prefix so far\n"
                               + self.walk(CPP_WALK, cup, cdown) + "        return best;\n    }\n"))
            for name, order_, doc in ((f"{big}PrefixSum", "a, b", f"{big.lower()} sum of a prefix of the path a -> b (a stretch starting at a)"),
                                      (f"{big}SuffixSum", "b, a", f"{big.lower()} sum of a suffix of the path a -> b (a stretch ending at b)")):
                self.add("Path" + name, [], cost, doc + self.empty(name, big.lower(), "path")[1],
                         f"        return self.{helper}({order_})\n",
                         f"        return {helper[1:]}({order_});\n", [], "auto", nodes=("a", "b"))

    # ---- a path's best stretch: each piece gives its sum, its best prefix, suffix and inner stretch (four range ops),
    # and the walk keeps the best stretch so far and the best one ending at the last value walked
    def subarray_sums(self):
        r = self.r
        for big, sign in (("Max", ">"), ("Min", "<")):
            low = big.lower()
            pre, suf, sub = f"{low}PrefixSum", f"{low}SuffixSum", f"{low}SubarraySum"
            if not r.has(pre, suf, sub, "rangeSum"):
                continue
            cost = times_log(worst(*[self.cost(o) for o in (pre, suf, sub, "rangeSum")]))
            start = 'float("-inf")' if big == "Max" else 'float("inf")'
            cnone = "numeric_limits<R>::lowest()" if big == "Max" else "numeric_limits<R>::max()"
            # (a piece read backwards: the stretch that reaches into it from behind is its array suffix, and the one it
            # leaves open at the end of the walk is its array prefix)
            py_piece = ("s, inner = total(l, r), inside(l, r)\n"
                        f"if inner {sign} best:\n    best = inner\n"
                        "v = tail + {lead}(l, r)\n"
                        f"if v {sign} best:\n    best = v\n"
                        "v = {trail}(l, r)\n"
                        f"tail = v if v {sign} tail + s else tail + s")
            cpp_piece = (f"R s = seg.rangeSum(l, r), inner = seg.{sub}(l, r);\n"
                         "R lead = seg.{lead}(l, r), trail = seg.{trail}(l, r);\n"
                         f"if (none || inner {sign} best) best = inner;\n"
                         f"if (!none && tail + lead {sign} best) best = tail + lead;\n"
                         f"tail = none || trail {sign} tail + s ? trail : tail + s;\n"
                         "none = false;")
            py = ("        head, par, dep, pos, seg = self.head, self.par, self.dep, self.pos, self.seg\n"
                  f"        total, starting, ending, inside = seg.rangeSum, seg.{pre}, seg.{suf}, seg.{sub}\n"
                  f"        best = tail = {start}  # the best stretch so far; the best one ending at the last {self.words['one']} walked\n"
                  + self.walk(PY_WALK, py_piece.format(lead="ending", trail="starting"),
                              py_piece.format(lead="starting", trail="ending"))
                  + "        return best\n")
            cpp = ("        using R = decltype(seg.rangeSum(0, 0));\n"
                   f"        R best = 0, tail = 0;  // the best stretch so far; the best one ending at the last {self.words['one']} walked\n"
                   "        bool none = true;  // nothing walked yet\n"
                   + self.walk(CPP_WALK, cpp_piece.format(lead=suf, trail=pre), cpp_piece.format(lead=pre, trail=suf))
                   + f"        return none ? {cnone} : best;\n")
            name = f"{big}SubarraySum"
            self.add("Path" + name, [], cost, f"{low} sum of a non-empty stretch of the path a..b" + self.empty(name, low, "path")[1],
                     py, cpp, [], "auto", nodes=("a", "b"))

    # ---- a path's hash: each piece's own hash (its reversed hash when the piece is read backwards), joined piece after
    # piece the way the range structure joins two halves: hash(A then B) = hash(A) * base^len(B) + hash(B)
    def path_hash(self):
        r = self.r
        if not r.has("rangeHash", "rangeHashReversed"):
            return
        cost = times_log(worst(self.cost("rangeHash"), self.cost("rangeHashReversed")))
        up = "res = (res * pow(_HB, r - l + 1, _HP) + back(l, r)) % _HP"
        down = "res = (res * pow(_HB, r - l + 1, _HP) + forward(l, r)) % _HP"
        cup = "res = joined(res, seg.rangeHashReversed(l, r), r - l + 1);"
        cdown = "res = joined(res, seg.rangeHash(l, r), r - l + 1);"
        self.helpers.append(("_hash", "hashOf"))
        self.ops.append(Op(None, None, None, None,
                           f"    # the hash of the {self.words['vals']} read walking a -> b\n"
                           "    def _hash(self, a, b):\n"
                           "        head, par, dep, pos = self.head, self.par, self.dep, self.pos\n"
                           "        forward, back = self.seg.rangeHash, self.seg.rangeHashReversed\n"
                           "        res = 0\n" + self.walk(PY_WALK, up, down) + "        return res\n",
                           f"    // the hash of the {self.words['vals']} read walking a -> b\n"
                           "    LEETCODE_NO_SANITIZE unsigned long long hashOf(int a, int b) {\n"
                           "        unsigned long long res = 0;\n" + self.walk(CPP_WALK, cup, cdown) + "        return res;\n    }\n"))
        vals = self.words["vals"]
        none = "; 0 when a == b (no edges)" if self.edge else ""
        same = " (two paths with no edges are equal)" if self.edge else ""
        size = "self._dist({}, {})"  # (the number of values on a path follows its number of edges)
        for name, args, nodes, doc, py, cpp, ret in (
            ("Hash", "a, b", ("a", "b"), f"hash of the {vals} read a -> b: equal sequences hash equal, and it equals the "
             f"range structure's rangeHash of the same values{none}",
             "        return self._hash(a, b)\n", "        return hashOf(a, b);\n", "unsigned long long"),
            ("HashReversed", "a, b", ("a", "b"), f"hash of the {vals} read b -> a (equal to {self.t}PathHash(b, a)){none}",
             "        return self._hash(b, a)\n", "        return hashOf(b, a);\n", "unsigned long long"),
            ("IsPalindrome", "a, b", ("a", "b"), f"do the {vals} read the same a -> b and b -> a?"
             + (" (True when a == b: no edges)" if self.edge else ""),
             "        return self._hash(a, b) == self._hash(b, a)\n", "        return hashOf(a, b) == hashOf(b, a);\n", "bool"),
        ):
            self.add("Path" + name, [], cost, doc, py, cpp, [], ret, nodes=nodes)
        self.add("PathsEqual", [], cost, f"do the {vals} read a -> b equal those read c -> d?{same}",
                 f"        return {size.format('a', 'b')} == {size.format('c', 'd')} and self._hash(a, b) == self._hash(c, d)\n",
                 "        return distOf(a, b) == distOf(c, d) && hashOf(a, b) == hashOf(c, d);\n", [], "bool",
                 nodes=("a", "b", "c", "d"))

    def build(self):
        self.point()
        self.path_unordered()
        self.path_arith()
        self.subarray_sums()
        self.path_hash()
        self.prefix_sums()
        self.searches()
        self.subtree()
        return self.ops


# ------------------------------------------------------------------------------------------------ one file
EXTRA_NOTES = {
    # (each ends its sentence: format_long_lines.py joins a comment line with the next one otherwise)
    "mod": "mod: the modulus MOD (every value is kept in [0, MOD)).",
    "bits": "bits: values live in [0, 2^bits).",
    "valLo": "valLo: every value ever held is >= valLo (any integer, negative is fine).",
    "valHi": "valHi: every value ever held is <= valHi.",
}
PY_DOC = '''\
# tree = Tree(@SIG@)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
@EXTRA@#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30]@EX@)       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30]@EX@)    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
@HOW@'''
CPP_DOC = '''\
// Tree tree(@SIG@);
//
// edges: the tree's n - 1 edges, vector<vector<int>> (vector<vector<long long>> works too). Whether nodes are 0..n-1
//        or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with
//        no edges, from root)
//   {{a, b}, ...}        e.g. {{0, 1}, {1, 2}}
//   {{a, b, w}, ...}     also accepted: the weights are ignored here
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
@EXTRA@//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30}@EX@);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30}@EX@);    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
@HOW@'''


PY_DOC_EDGE = '''\
# tree = Tree(@SIG@)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
@EXTRA@#
#   Tree([(0, 1, 5), (1, 2, 7)], 0@EX@)    # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1@EX@)    # nodes 1..3, rooted at 1
#
@NOTES@#
@HOW@'''
CPP_DOC_EDGE = '''\
// Tree<long long> tree(@SIG@);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
@EXTRA@//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0@EX@);    // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1@EX@);    // nodes 1..3, rooted at 1
//
// T is the type the weights are kept in (long long, or int).
@NOTES@//
@HOW@'''
PY_DOC_BOTH = '''\
# tree = Tree(@SIG@)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
@EXTRA@#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30]@EX@)       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30]@EX@)    # nodes 1..3, rooted at 1
#
@NOTES@#
@HOW@'''
CPP_DOC_BOTH = '''\
// Tree tree(@SIG@);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int; the weights are kept as T too), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
@EXTRA@//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, {10, 20, 30}@EX@);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, {0, 10, 20, 30}@EX@);    // nodes 1..3, rooted at 1
//
@NOTES@//
@HOW@'''
BOTH_NOTES = ("The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each "
              "other. For nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and "
              "b and a subtree the edges below node; an edge is named by its two ends in either order, a search that finds "
              "an edge returns its lower end (the end farther from the root), and a query with no edges to look at (a path "
              "a..a, a leaf's subtree) says what it returns. Nodes go in and come out with your labels, -1 means \"none\", "
              "and a label that is not in the tree {raises}. Nothing recurses, so a 10^6-node chain is fine.")
HOW_BOTH = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is "
            "one stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above "
            "({cls}) sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight "
            "at its lower end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) "
            "ranges, one per chain it crosses.")
EDGE_NOTES = ("An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the "
              "edges between a and b, and a subtree covers the edges below node. A search that finds an edge returns its "
              "lower end (the end farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) "
              "says what it returns. Nodes go in and come out with your labels, -1 means \"none\", and a label that is not "
              "in the tree {raises}. Nothing recurses, so a 10^6-node chain is fine.")
HOW_EDGE = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is "
            "one stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Each edge's weight sits at its lower end's "
            "position in the range structure above ({cls}); the root's position holds no edge. The edges below node are "
            "one range of it, and the edges of a path a..b are O(log n) ranges, one per chain it crosses.")


def both_ops(rng):
    """Every node op and every edge op of one range folder, for a Tree that keeps two copies of the range structure
    (nodeSeg, edgeSeg): the same methods the node- and edge- templates have, each reading its own copy, and the
    private walks named for their side (both sides write a _firstGteX)."""
    out, odd = [], []
    for target in ("node", "edge"):
        maker = Maker(rng, target)
        odd += maker.odd
        for op in maker.build():
            py = re.sub(r"\bself\.seg\b", f"self.{target}Seg", op.py)
            cpp = re.sub(r"\bseg\.", f"{target}Seg.", op.cpp)
            for pn, cn in maker.helpers:
                py = re.sub(rf"\b{pn}\(", f"_{target}{pn[1].upper()}{pn[2:]}(", py)
                cpp = re.sub(rf"(?<![.\w]){cn}\(", f"{target}{cn[0].upper()}{cn[1:]}(", cpp)
            out.append(Op(op.name, op.args, op.cost, op.doc, py, cpp, op.returns))
    return out, odd


def twice(arrays):
    """A @memory array list for two copies of the structure: "sm[2*N] add[1*N]" -> "sm[4*N] add[2*N]"."""
    if arrays == "none":
        return arrays
    out = []
    for item in arrays.split():
        name, size = item[:-1].split("[", 1)
        terms = []
        for term in size.split("+"):
            fs = term.split("*")
            terms.append("*".join([str(2 * int(fs[0]))] + fs[1:] if fs[0].isdigit() else ["2"] + fs))
        out.append(f"{name}[{'+'.join(terms)}]")
    return " ".join(out)


def header(cm, folder, rng, ops, ext, both=False):
    costs = {op.name: op.cost for op in ops if op.name}
    costs.update({op: shape.COSTS[op][0] for op in SHAPE_OPS})
    build = worst(rng.costs["build"], "N")
    mem = dict(rng.memory)
    if both:  # two copies of the range structure
        mem.update({k: twice(mem.get(k, "none")) for k in ("node", "tags", "other")})
    other = LAYOUT_ARRAYS if mem.get("other", "none") == "none" else f"{mem['other']} {LAYOUT_ARRAYS}"
    lines = [
        "Template by https://github.com/ishaanbuildsthings",
        f"{URL}/{folder}/template.{ext}",
        f"The range structure inside is {RANGE_URL}/{rng.folder}/{'template.py' if ext == 'py' else rng.cpp_name}",
        "@operations: " + " ".join(sorted(costs)),
        f"@data-structure-type: {rng.kind}",
        "@complexities:",
        *[f"  {op}: {costs[op]}" for op in sorted(costs)],
        f"  build: {build}",
        "@memory:",
        f"  layout: {mem['layout']}",
        f"  node: {mem.get('node', 'none')}",
        f"  tags: {mem.get('tags', 'none')}",
        f"  other: {other}",
    ]
    if mem.get("note"):
        lines.append(f"  note: {mem['note']}")
    return "".join(f"{cm} {line}\n" for line in lines), build


HOW = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one "
       "stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above ({cls}) "
       "in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it crosses.")


def wrap(cm, text, width=120):
    lines, cur = [], cm
    for w in text.split(" "):
        if len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = cm
        cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def fill_doc(doc, cm, rng, sig, example, target="node"):
    extra = "".join(f"{cm} {EXTRA_NOTES[n]}\n" for n in rng.extra_names)
    raises = "raises IndexError" if cm == "#" else "throws out_of_range"
    notes = {"edge": EDGE_NOTES, "both": BOTH_NOTES}.get(target, "")
    how = {"edge": HOW_EDGE, "both": HOW_BOTH}.get(target, HOW)
    return (doc.replace("@SIG@", sig).replace("@EXTRA@", extra).replace("@EX@", example)
            .replace("@NOTES@", wrap(cm, notes.format(raises=raises))).replace("@HOW@", wrap(cm, how.format(cls=rng.cls))))


PY_WEIGHTS = ("        for e in edges:\n"
              "            if len(e) != 3:\n"
              '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
              "        arr = [edges[0][2] if edges else 0] * n  # (position 0 is the root's: it holds no edge, never read)\n"
              "        for e in edges:\n"
              "            a, b = e[0], e[1]\n"
              "            arr[pos[a] if par[a] == b else pos[b]] = e[2]\n")
PY_VALS = ("        if len(vals) != hi + 1:\n"
           '            raise ValueError(f"Tree: vals[node] is node\'s value, so nodes {lo}..{hi} need len(vals) = {hi + 1}"\n'
           '                             f"{\' (vals[0] is ignored)\' if lo else \'\'}, got {len(vals)}")\n')


def make_py(folder, rng, ops, target="node"):
    edge = target == "edge"
    head, build = header("#", folder, rng, ops, "py", both=target == "both")
    extra = "".join(f", {p}" for p in rng.py_extra)
    names = "".join(f", {n}" for n in rng.extra_names)
    imports = "from bisect import bisect_left\n" + ("from math import gcd\n" if any("gcd(res" in o.py for o in ops) else "")
    if target == "both":
        doc = fill_doc(PY_DOC_BOTH, "#", rng, "edges, root, vals" + names, names, "both")
        ctor = (comment("#", build, "builds the layout and the two range structures; raises ValueError when the edges are "
                        "not one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length")
                + f"    def __init__(self, edges, root, vals{extra}):\n" + shape.py_layout_body() + PY_VALS + PY_WEIGHTS
                + f"        self.nodeSeg = {rng.cls}([vals[v] for v in order]{names})  # the node values, in position order\n"
                f"        self.edgeSeg = {rng.cls}(arr{names})  # each edge's weight, at its lower end's position\n")
    elif edge:
        doc = fill_doc(PY_DOC_EDGE, "#", rng, "edges, root" + names, names, "edge")
        ctor = (comment("#", build, "builds the layout and the range structure; raises ValueError when the edges are not "
                        "one tree on nodes 0..n-1 or 1..n, or an edge has no weight")
                + f"    def __init__(self, edges, root{extra}):\n" + shape.py_layout_body() + PY_WEIGHTS
                + f"        self.seg = {rng.cls}(arr{names})  # each edge's weight, at its lower end's position\n")
    else:
        doc = fill_doc(PY_DOC, "#", rng, "edges, root, vals" + names, names)
        ctor = (comment("#", build, "builds the layout and the range structure; raises ValueError when the edges are not "
                        "one tree on nodes 0..n-1 or 1..n, or vals has the wrong length")
                + f"    def __init__(self, edges, root, vals{extra}):\n" + shape.py_layout_body() + PY_VALS
                + f"        self.seg = {rng.cls}([vals[v] for v in order]{names})  # the values, in position order\n")
    ctor += "        self.mod = mod\n" if "mod" in rng.extra_names else ""
    methods = "\n".join(op.py for op in ops)
    return (head + "\n" + rng.py_inner().rstrip("\n") + "\n\n\n" + imports + "\n\n" + doc + "class Tree:\n" + ctor + "\n"
            + methods + "\n" + shape.py_shape_methods())


CPP_WEIGHTS = ("        for (const auto& e : edges)\n"
               '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
               "        // (position 0 is the root's: it holds no edge and is never read)\n"
               "        vector<T> inOrder(n, edges.empty() ? T(0) : (T)edges[0][2]);\n"
               "        for (const auto& e : edges) {\n"
               "            int a = (int)e[0], b = (int)e[1];\n"
               "            inOrder[par[a] == b ? pos[a] : pos[b]] = (T)e[2];\n"
               "        }\n"
               "        return inOrder;\n")
CPP_VALS = ("        if ((int)vals.size() != hi + 1)\n"
            '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
            "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
            "        vector<T> inOrder(n);\n"
            "        for (int i = 0; i < n; i++) inOrder[i] = vals[order[i]];\n"
            "        return inOrder;\n")


def make_cpp(folder, rng, ops, target="node"):
    edge, both = target == "edge", target == "both"
    head, build = header("//", folder, rng, ops, "cpp", both=both)
    inner = rng.cpp_inner().rstrip("\n")
    if "struct HotVector" not in inner:
        inner = shape.PRELUDE.rstrip("\n") + "\n\n" + inner
    extra = "".join(f", {p}" for p in rng.cpp_extra)
    names = "".join(f", {n}" for n in rng.extra_names)
    has_mod = "mod" in rng.extra_names
    weights_at = "each edge's weight, at its lower end's position"
    if both:
        held = (f"    {rng.cls}<T> nodeSeg;  // the node values, in position order\n"
                f"    {rng.cls}<T> edgeSeg;  // {weights_at}\n")
        init = f"nodeSeg(layout(edges, root, vals){names}), edgeSeg(weights(edges){names})"
    else:
        held = f"    {rng.cls}<T> seg;  // {weights_at if edge else 'the values, in position order'}\n"
        init = f"seg(layout({'edges, root' if edge else 'edges, root, vals'}){names})"
    members = shape.cpp_members().rstrip("\n") + "\n" + held + ("    T modulus;\n" if has_mod else "")
    init += ", modulus(mod)" if has_mod else ""
    params = "const vector<vector<E>>& edges, int root" + ("" if edge else ", const vector<T>& vals")
    sig = f"    template <typename E = int> Tree({params}{extra})"
    if len(sig) > 118:
        sig = f"    template <typename E = int> Tree({params},\n                                    {', '.join(rng.cpp_extra)})"
    init = "\n        : " + init + " {}\n\n"
    if len(init.split("\n")[1]) > 120:  # (the both- templates: one member per line)
        init = init.replace("), edgeSeg(", "),\n          edgeSeg(")
    values_layout = ("    // lays the tree out (fills the arrays above) and returns the values in position order\n"
                     "    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root, const vector<T>& vals) {\n"
                     "        this->root = root;\n" + shape.cpp_layout_body() + "\n" + CPP_VALS + "    }\n")
    if both:
        doc = fill_doc(CPP_DOC_BOTH, "//", rng, "edges, root, vals" + names, names, "both")
        ctor = (comment("//", build, "builds the layout and the two range structures; throws invalid_argument when the "
                        "edges are not one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size")
                + sig + init + values_layout + "\n"
                f"    // {weights_at} (the layout is built by the time this runs)\n"
                "    template <typename E> vector<T> weights(const vector<vector<E>>& edges) {\n" + CPP_WEIGHTS + "    }\n")
    elif edge:
        doc = fill_doc(CPP_DOC_EDGE, "//", rng, "edges, root" + names, names, "edge")
        ctor = (comment("//", build, "builds the layout and the range structure; throws invalid_argument when the edges "
                        "are not one tree on nodes 0..n-1 or 1..n, or an edge has no weight")
                + sig + init
                + "    // lays the tree out (fills the arrays above) and returns each edge's weight at its lower end's position\n"
                "    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root) {\n"
                "        this->root = root;\n" + shape.cpp_layout_body() + "\n" + CPP_WEIGHTS + "    }\n")
    else:
        doc = fill_doc(CPP_DOC, "//", rng, "edges, root, vals" + names, names)
        ctor = (comment("//", build, "builds the layout and the range structure; throws invalid_argument when the edges "
                        "are not one tree on nodes 0..n-1 or 1..n, or vals has the wrong size")
                + sig + init + values_layout)
    if any(op.name and op.name.endswith("PathHash") for op in ops):  # hashing: base powers, and how two hashes join
        members += "    HotVector<unsigned long long> hashPow;  // hashPow[k] = base^k, the range structure's own base\n"
        assert init.endswith(" {}\n\n")
        init = (init[:-len(" {}\n\n")] + " {\n"
                "        hashPow.assign(n + 1, 1);\n"
                f"        for (int k = 1; k <= n; k++) hashPow[k] = {rng.cls}<T>::hmul(hashPow[k - 1], {rng.cls}<T>::HB());\n"
                "    }\n\n")
        ctor_was = ctor
        ctor = ctor.replace(" {}\n\n", init[init.index(" {\n"):], 1)
        assert ctor != ctor_was
        ctor += ("\n    // the hash of a sequence followed by one of `len` more values: hash(A then B) = hash(A) * base^len(B) + hash(B)\n"
                 "    LEETCODE_NO_SANITIZE unsigned long long joined(unsigned long long front, unsigned long long back, int len) const {\n"
                 f"        return {rng.cls}<T>::hadd({rng.cls}<T>::hmul(front, hashPow[len]), back);\n"
                 "    }\n")
    methods = "\n".join(op.cpp for op in ops)
    return (head + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE + "\n"
            + inner + "\n\n" + doc + "template <typename T>\nstruct Tree {\n" + members + "\n" + ctor + "\n" + methods + "\n"
            + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")


# ------------------------------------------------------------------------------------------------ every folder
ODD = []  # ops left out because a range method's arguments are not what the tables expect


TARGETS = ("node", "edge")


def plan():
    """{tree folder: (Range, [Op], target)}: per target, one tree folder per (structure type, set of tree ops), from
    the lightest range folder that gives it; plus why each range folder that was looked at is left out."""
    best, skipped = {}, {}
    for folder in sorted(os.listdir(RANGE_DIR)):
        base = os.path.join(RANGE_DIR, folder)
        if not (os.path.exists(os.path.join(base, "template.py")) and os.path.exists(os.path.join(base, "template.cpp"))):
            continue
        rng = Range(folder)
        if rng.cls is None:
            skipped[folder] = rng.why
            continue
        for target in TARGETS:
            maker = Maker(rng, target)
            ops = maker.build()
            ODD.extend(f"{folder}: {o}" for o in maker.odd)
            names = frozenset(op.name for op in ops if op.name)
            if not any("Path" in n or "Subtree" in n for n in names):
                skipped[folder] = "no path or subtree op"
                continue
            if not any(op.returns for op in ops):
                skipped[folder] = "only updates: nothing reads a value back"
                continue
            key = (target, rng.kind, names, tuple(rng.extra_names))
            rank = (len(rng.ops), len(folder), folder)
            if key not in best or rank < best[key][0]:
                best[key] = (rank, rng, ops, target)
    # node values and edge weights together: for every range folder that made a node- folder, one both- folder
    for (target, kind, names, extras), (rank, rng, _, _) in list(best.items()):
        if target == "node":
            ops, _ = both_ops(rng)
            best[("both", kind, names, extras)] = (rank, rng, ops, "both")
    return {f"{target}-{rng.folder}": (rng, ops, target) for _, rng, ops, target in best.values()}, skipped


def main():
    check, only_list = "--check" in sys.argv, "--list" in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    folders, skipped = plan()
    if want:
        folders = {f: v for f, v in folders.items() if any(w in f for w in want)}
    stale = []
    for folder, (rng, ops, target) in sorted(folders.items()):
        texts = {"template.py": shape.tidy(make_py(folder, rng, ops, target), f"{folder}/template.py"),
                 "template.cpp": shape.tidy(make_cpp(folder, rng, ops, target), f"{folder}/template.cpp")}
        for name, text in texts.items():
            path = os.path.join(DIR, folder, name)
            if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
                continue
            stale.append(f"{folder}/{name}")
            if not check and not only_list:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "w", encoding="utf-8").write(text)
    # a node-* / edge-* / both-* folder no range folder gives any more is stale too
    made = tuple(f"{t}-" for t in TARGETS + ("both",))
    gone = [] if want else [f for f in sorted(os.listdir(DIR)) if f.startswith(made) and f not in folders]
    for folder in gone:
        stale.append(folder + "/ (no longer generated)")
        if not check and not only_list:
            shutil.rmtree(os.path.join(DIR, folder))
    if check:
        for rel in stale[:40]:
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree.py writes (rerun it)")
        print(f"{len(stale)} stale tree files" if stale else f"{len(folders)} node-, edge- and both-value tree folders are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(folders)} node-, edge- and both-value tree folders, {len(stale)} files {'would be ' if only_list else ''}written or removed; "
          f"{len(skipped)} range folders left out")
    if only_list:
        why = {}
        for reason in skipped.values():
            why[reason.split(" (")[0]] = why.get(reason.split(" (")[0], 0) + 1
        for reason, count in sorted(why.items(), key=lambda kv: -kv[1]):
            print(f"  {count:6} left out: {reason}")
        print(f"  {len(ODD)} ops left out for an unexpected argument list")
        for line in ODD[:10]:
            print("    " + line[:200])


if __name__ == "__main__":
    main()
