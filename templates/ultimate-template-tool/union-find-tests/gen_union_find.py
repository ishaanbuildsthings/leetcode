"""Union find templates for the site's Union find tab: one find mode plus any set of extras, in Python and C++.

    find modes   compress     path compression: fastest, but parents get rewritten
                 nocompress   parents never change, so the forest is a record of every merge (uniteAUnderB too)
                 rollback     no compression plus an undo stack: rollback(), checkpoint(), rollbackTo(k)
    extras       values       componentSum / componentMin / componentMax of the elements' values
                 merge        your own Node per component: baseFn(v, i) and combine(big, small), like the generic seg tree
                 members      each component's members linked in a circle: elementsInGroup in O(size of the group)
                 edges        edgeCount(i) / isTree(i): every unite counts as an edge, merging or not
                 potential    unite(i, j, w) means value[j] - value[i] = w, and diff(i, j) reads it back
                 time         firstConnectedTime(i, j) / connectedAt(i, j, t) (nocompress only)
                 grow         add(val): a new element in its own component

Writes templates/ultimate-template-tool/union-find/<mode>[-extra...]/template.py and template.cpp (folder name: the
mode, then the extras in the order above), the next-free-index DSU in union-find/_next-free/, and the site's
lib/generated/union-find-templates.ts (the ops each mode and extra adds, with their costs), and copies all of it (plus
templates/union-find/hdlt.*) into site/public/union-find-templates/ for the site.

    python3 gen_union_find.py
"""
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DIR = os.environ.get("UNION_FIND_DIR") or os.path.join(REPO, "templates", "ultimate-template-tool", "union-find")
SITE_MANIFEST = os.path.join(REPO, "site", "lib", "generated", "union-find-templates.ts")
SITE_PUBLIC = os.path.join(REPO, "site", "public", "union-find-templates")  # (the copies next dev serves)
HDLT = os.path.join(REPO, "templates", "union-find")  # (the hand-written fully dynamic connectivity, shown beside them)
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find"

MODES = ["compress", "nocompress", "rollback"]
FEATS = ["values", "merge", "members", "edges", "potential", "time", "grow"]
CLASS = {"compress": "DSU", "nocompress": "DSUNoCompress", "rollback": "RollbackDSU"}


def allowed(mode, feats):
    return not ("time" in feats and mode != "nocompress")


def folder(mode, feats):
    return "-".join([mode] + [f for f in FEATS if f in feats])


def combos():
    for mode in MODES:
        for k in range(len(FEATS) + 1):
            for feats in itertools.combinations(FEATS, k):
                if allowed(mode, feats):
                    yield mode, set(feats)


def find_cost(mode):
    return "α(n) amortized" if mode == "compress" else "log n"


# ------------------------------------------------------------------------------------------------ the site's op table
def op_parts():
    """[op, cost] lists: what every template of a mode has, and what each extra adds (or replaces, same op name)"""
    base, extra = {}, {}
    for mode in MODES:
        f = find_cost(mode)
        slow = "n" if mode == "compress" else "n log n"
        ops = [["find(i)", f], ["unite(i, j)", f], ["areUnioned(i, j)", f], ["size(i)", f], ["numComponents()", "1"],
               ["largestSize()", "1"], ["roots()", "n"], ["sizes()", "n log n"], ["groups()", slow],
               ["elementsInGroup(i)", slow]]
        if mode == "nocompress":
            ops.append(["uniteAUnderB(a, b)", "log n (no union by size: depth can degrade)"])
        if mode == "rollback":
            ops += [["rollback()", "1"], ["checkpoint()", "1"], ["rollbackTo(k)", "1 per unite undone"]]
        base[mode] = ops + [["build", "n"]]
        extra[mode] = {
            "values": [["componentSum(i)", f], ["componentMin(i)", f], ["componentMax(i)", f]],
            "merge": [["componentData(i)", f]],
            "members": [["elementsInGroup(i)", "size of the group"]],
            "edges": [["edgeCount(i)", f], ["isTree(i)", f]],
            "potential": [["unite(i, j, w)", f], ["diff(i, j)", f]] +
                         ([["uniteAUnderB(a, b, w)", "log n (no union by size: depth can degrade)"]] if mode == "nocompress" else []),
            "time": [["firstConnectedTime(i, j)", "log n"], ["connectedAt(i, j, t)", "log n"]],
            "grow": [["add(val)", "1"]],
        }
    return base, extra


# ------------------------------------------------------------------------------------------------ Python
PY_STUBS = '''# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# called once per merge: big is the bigger component's Node (on a tie, either one){mutate}
def combine(big: Node, small: Node) -> Node:
    # return (big[0] + small[0], max(big[1], small[1]))
    pass


'''
PY_MUTATE = {
    "compress": ". Mutating big and returning it is fine, e.g.\n# small-to-large: big |= small; return big (O(n log n) in total)",
    "nocompress": ". Mutating big and returning it is fine, e.g.\n# small-to-large: big |= small; return big (O(n log n) in total)",
    "rollback": ". Don't mutate big: rollback keeps the old\n# Node to put it back, so return a new one",
}


def py_link(win, lose, has, wv="w", tv="t"):
    out = [f"self.par[{lose}] = {win}",
           f"self.sz[{win}] += self.sz[{lose}]",
           "self.comps -= 1",
           f"if self.sz[{win}] > self.mx:",
           f"    self.mx = self.sz[{win}]"]
    if has("values"):
        out += [f"self.csum[{win}] += self.csum[{lose}]",
                f"if self.cmin[{lose}] < self.cmin[{win}]:", f"    self.cmin[{win}] = self.cmin[{lose}]",
                f"if self.cmax[{lose}] > self.cmax[{win}]:", f"    self.cmax[{win}] = self.cmax[{lose}]"]
    if has("merge"):
        out.append(f"self.data[{win}] = self.combine(self.data[{win}], self.data[{lose}])")
    if has("members"):
        out.append(f"self.nxt[{win}], self.nxt[{lose}] = self.nxt[{lose}], self.nxt[{win}]  # (joins the two circles)")
    if has("edges"):
        out.append(f"self.edges[{win}] += self.edges[{lose}] + 1")
    if has("potential"):
        out.append(f"self.pot[{lose}] = {wv}")
    if has("time"):
        out.append(f"self.tm[{lose}] = {tv}")
    return out


def py(mode, feats):
    has = feats.__contains__
    cls, comp, nc, roll = CLASS[mode], mode == "compress", mode == "nocompress", mode == "rollback"
    F = "O(α(n)) amortized" if comp else "O(log n)"
    name = folder(mode, feats)
    L = ["# Template by https://github.com/ishaanbuildsthings", f"# {URL}/{name}/template.py", ""]
    if has("time"):
        L += ["_NEVER = 1 << 62  # (the time of a root: it never got a parent)", "", ""]
    if has("merge"):
        L += PY_STUBS.replace("{mutate}", PY_MUTATE[mode]).rstrip("\n").split("\n") + ["", ""]
    ctor = f"{cls}(vals, baseFn, combine)" if has("merge") else f"{cls}(vals)"
    L += [f"# dsu = {ctor}",
          "# vals: the elements (" + ("numbers: componentSum / Min / Max are over them" if has("values") else "any values: numbers, strings, tuples, ...") +
          "); everything works on their indices 0..n-1" + (", and add(val) appends more" if has("grow") else "")]
    if has("potential"):
        L += ["# potential: every element has a hidden number value[i]; unite(i, j, w) says value[j] - value[i] = w and diff(i, j)",
              "# reads it back (for parity / two-colouring, swap + and - for ^ throughout)"]
    L += ["", "", f"class {cls}:"]
    I = "    "
    # ---- constructor
    L += [I + "# O(n), every element starts in its own component",
          I + ("def __init__(self, vals, baseFn, combine):" if has("merge") else "def __init__(self, vals):"),
          I * 2 + "self.vals = list(vals)",
          I * 2 + "n = len(self.vals)",
          I * 2 + "self.par = list(range(n))",
          I * 2 + "self.sz = [1] * n",
          I * 2 + "self.comps = n",
          I * 2 + "self.mx = 1 if n else 0"]
    if has("values"):
        L += [I * 2 + "# at each root: the sum, min and max of its component's values",
              I * 2 + "self.csum = list(self.vals)", I * 2 + "self.cmin = list(self.vals)", I * 2 + "self.cmax = list(self.vals)"]
    if has("merge"):
        L += [I * 2 + "self.baseFn, self.combine = baseFn, combine",
              I * 2 + "self.data = [baseFn(v, i) for i, v in enumerate(self.vals)]  # data[root]: the Node of root's component"]
    if has("members"):
        L += [I * 2 + "self.nxt = list(range(n))  # each component's members linked in a circle: i -> nxt[i] -> ... -> i"]
    if has("edges"):
        L += [I * 2 + "self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not"]
    if has("potential"):
        L += [I * 2 + "self.pot = [0] * n  # pot[i] = value[i] - value[par[i]] (0 at a root)"]
    if has("time"):
        L += [I * 2 + "self.time = 0  # how many unites so far, failed ones too",
              I * 2 + "self.tm = [_NEVER] * n  # tm[i]: the unite (0, 1, 2, ...) that gave i its parent"]
    if roll:
        L += [I * 2 + "self.stk = []  # one frame per unite, so rollback can undo it"]
    L.append("")
    # ---- find
    if comp and has("potential"):
        L += [I + f"# {F}, effectively O(1): index of the representative of i's component (compresses fully, keeping pot right)",
              I + "def find(self, i):",
              I * 2 + "par, pot = self.par, self.pot",
              I * 2 + "path = []",
              I * 2 + "while par[i] != i:",
              I * 3 + "path.append(i)",
              I * 3 + "i = par[i]",
              I * 2 + "for x in reversed(path):  # nearest the root first, so its parent's pot is already relative to the root",
              I * 3 + "p = par[x]",
              I * 3 + "if p != i:",
              I * 4 + "pot[x] += pot[p]",
              I * 4 + "par[x] = i",
              I * 2 + "return i"]
    elif comp:
        L += [I + f"# {F}, effectively O(1): index of the representative of i's component",
              I + "def find(self, i):",
              I * 2 + "par = self.par",
              I * 2 + "while par[i] != i:",
              I * 3 + "par[i] = par[par[i]]",
              I * 3 + "i = par[i]",
              I * 2 + "return i"]
    else:
        why = "so the forest records every merge" if nc else "so any unite can be undone"
        L += [I + f"# O(log n), index of the representative of i's component; parents are never rewritten, {why}",
              I + "def find(self, i):",
              I * 2 + "par = self.par",
              I * 2 + "while par[i] != i:",
              I * 3 + "i = par[i]",
              I * 2 + "return i"]
    L.append("")
    if has("potential"):
        L += [I + "# (root of i, value[i] - value[root])", I + "def _rootAndWeight(self, i):"]
        if comp:
            L += [I * 2 + "r = self.find(i)", I * 2 + "return r, self.pot[i]"]
        else:
            L += [I * 2 + "par, pot = self.par, self.pot", I * 2 + "w = 0",
                  I * 2 + "while par[i] != i:", I * 3 + "w += pot[i]", I * 3 + "i = par[i]", I * 2 + "return i, w"]
        L.append("")
    # ---- unite
    doc = [f"{F}, merges the two components, " + ("returns (winner, loser): the new root and the old root now under it, or\n# None if they were already together" if nc else "False if i and j were already together")]
    if has("potential"):
        doc.append("w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)")
    if has("edges"):
        doc.append("either way it counts as an edge of the component (edgeCount)")
    if has("time"):
        doc.append("each call is the next unite in time (0, 1, 2, ...), failed ones too")
    if roll:
        doc.append("either way it records a frame, so it always takes exactly one rollback to undo")
    L += [I + "# " + line.replace("\n", "\n" + I) for line in doc]
    L.append(I + ("def unite(self, i, j, w):" if has("potential") else "def unite(self, i, j):"))
    body = []
    if has("time"):
        body += ["t = self.time", "self.time += 1"]
    if has("potential"):
        body += ["i, wi = self._rootAndWeight(i)", "j, wj = self._rootAndWeight(j)"]
    else:
        body += ["i, j = self.find(i), self.find(j)"]
    body.append("if i == j:")
    if has("edges"):
        body.append("    self.edges[i] += 1")
    if roll:
        body.append("    self.stk.append(" + ("i)  # (an int frame: only the edge count to undo)" if has("edges") else "None)"))
    body.append("    return None" if nc else "    return False")
    if has("potential"):
        body.append("w += wi - wj  # now value[j's root] - value[i's root]")
    body += ["if self.sz[i] < self.sz[j]:", "    i, j = j, i"]
    if has("potential"):
        body.append("    w = -w")
    if roll:
        frame = ["i", "j", "self.mx"] + (["self.cmin[i]", "self.cmax[i]"] if has("values") else []) + (["self.data[i]"] if has("merge") else [])
        body.append(f"self.stk.append(({', '.join(frame)}))")
    body += py_link("i", "j", has)
    body.append("return i, j" if nc else "return True")
    L += [I * 2 + b for b in body]
    L.append("")
    # ---- uniteAUnderB
    if nc:
        L += [I + "# O(log n), forces a's root under b's root, False if already together",
              I + "# skips union by size, so depth can degrade to O(n) and every walk with it"]
        if has("potential"):
            L.append(I + "# w: value[b] - value[a] = w")
        if has("merge"):
            L.append(I + "# combine gets b's component's Node first here, even when it's the smaller one")
        L.append(I + ("def uniteAUnderB(self, a, b, w):" if has("potential") else "def uniteAUnderB(self, a, b):"))
        body = []
        if has("time"):
            body += ["t = self.time", "self.time += 1"]
        if has("potential"):
            body += ["a, wa = self._rootAndWeight(a)", "b, wb = self._rootAndWeight(b)"]
        else:
            body += ["a, b = self.find(a), self.find(b)"]
        body.append("if a == b:")
        if has("edges"):
            body.append("    self.edges[a] += 1")
        body.append("    return False")
        if has("potential"):
            body.append("w = wb - wa - w  # now value[a's root] - value[b's root]")
        body += py_link("b", "a", has)
        body.append("return True")
        L += [I * 2 + b for b in body]
        L.append("")
    # ---- rollback
    if roll:
        L += [I + "# O(1), undoes the most recent unite, whether or not it merged anything: k rollbacks always undo the last",
              I + "# k unites" + (" (an add is never undone)" if has("grow") else "") + "; IndexError if you roll back more unites than you made",
              I + "def rollback(self):",
              I * 2 + "frame = self.stk.pop()"]
        if has("edges"):
            L += [I * 2 + "if type(frame) is int:", I * 3 + "self.edges[frame] -= 1", I * 3 + "return"]
        else:
            L += [I * 2 + "if frame is None:", I * 3 + "return"]
        unpack = ["i", "j", "mx"] + (["lo", "hi"] if has("values") else []) + (["data"] if has("merge") else [])
        L += [I * 2 + f"{', '.join(unpack)} = frame",
              I * 2 + "self.par[j] = j",
              I * 2 + "self.sz[i] -= self.sz[j]",
              I * 2 + "self.comps += 1",
              I * 2 + "self.mx = mx"]
        if has("values"):
            L += [I * 2 + "self.csum[i] -= self.csum[j]", I * 2 + "self.cmin[i] = lo", I * 2 + "self.cmax[i] = hi"]
        if has("merge"):
            L += [I * 2 + "self.data[i] = data"]
        if has("members"):
            L += [I * 2 + "self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (the same swap splits them again)"]
        if has("edges"):
            L += [I * 2 + "self.edges[i] -= self.edges[j] + 1"]
        if has("potential"):
            L += [I * 2 + "self.pot[j] = 0"]
        L += ["",
              I + "# O(1), a point to roll back to later: how many unites can be undone right now",
              I + "def checkpoint(self):",
              I * 2 + "return len(self.stk)",
              "",
              I + "# O(1) per unite undone, undoes every unite made since checkpoint() returned k",
              I + "def rollbackTo(self, k):",
              I * 2 + "while len(self.stk) > k:",
              I * 3 + "self.rollback()",
              ""]
    # ---- the base queries
    slow = "O(n)" if comp else "O(n log n)"
    L += [I + f"# {F}, True if i and j are in the same component",
          I + "def areUnioned(self, i, j):",
          I * 2 + "return self.find(i) == self.find(j)",
          "",
          I + f"# {F}, how many elements are in i's component",
          I + "def size(self, i):",
          I * 2 + "return self.sz[self.find(i)]",
          "",
          I + "# O(1), how many components exist right now",
          I + "def numComponents(self):",
          I * 2 + "return self.comps",
          "",
          I + "# O(1), size of the biggest component" + (", restored by rollback" if roll else ", maintained in unite"),
          I + "def largestSize(self):",
          I * 2 + "return self.mx",
          "",
          I + "# O(n), one index per component: the representative each member's find returns",
          I + "def roots(self):",
          I * 2 + "return [i for i in range(len(self.par)) if self.par[i] == i]",
          "",
          I + "# O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]",
          I + "def sizes(self):",
          I * 2 + "return sorted((self.sz[i] for i in range(len(self.par)) if self.par[i] == i), reverse=True)",
          "",
          I + f"# {slow}, groupsArr[rt] = list of values whose root is rt, [] if rt is not a root",
          I + "def groups(self):",
          I * 2 + "n = len(self.par)",
          I * 2 + "groupsArr = [[] for _ in range(n)]",
          I * 2 + "for i in range(n):",
          I * 3 + "groupsArr[self.find(i)].append(self.vals[i])",
          I * 2 + "return groupsArr",
          ""]
    if has("members"):
        L += [I + "# O(size of the group), the values of every element in the same group as index i, starting at i",
              I + "def elementsInGroup(self, i):",
              I * 2 + "vals, nxt = self.vals, self.nxt",
              I * 2 + "res = [vals[i]]",
              I * 2 + "j = nxt[i]",
              I * 2 + "while j != i:",
              I * 3 + "res.append(vals[j])",
              I * 3 + "j = nxt[j]",
              I * 2 + "return res",
              ""]
    else:
        L += [I + f"# {slow}, the values of every element sitting in the same group as index i",
              I + "def elementsInGroup(self, i):",
              I * 2 + "rt = self.find(i)",
              I * 2 + "return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]",
              ""]
    # ---- the extras' queries
    if has("values"):
        for fn, arr, what in (("componentSum", "csum", "sum"), ("componentMin", "cmin", "smallest"), ("componentMax", "cmax", "largest")):
            L += [I + f"# {F}, the {what} of the values in i's component", I + f"def {fn}(self, i):",
                  I * 2 + f"return self.{arr}[self.find(i)]", ""]
    if has("merge"):
        L += [I + f"# {F}, the Node of i's component: every member's baseFn, combined",
              I + "def componentData(self, i):", I * 2 + "return self.data[self.find(i)]", ""]
    if has("edges"):
        L += [I + f"# {F}, how many unites have touched i's component (merging or not): its edges, if each unite is an edge",
              I + "def edgeCount(self, i):", I * 2 + "return self.edges[self.find(i)]", "",
              I + f"# {F}, True if i's component has no cycle: exactly size - 1 edges",
              I + "def isTree(self, i):", I * 2 + "r = self.find(i)", I * 2 + "return self.edges[r] == self.sz[r] - 1", ""]
    if has("potential"):
        L += [I + f"# {F}, value[j] - value[i] from the unites so far, None if i and j aren't together",
              I + "def diff(self, i, j):",
              I * 2 + "ri, wi = self._rootAndWeight(i)",
              I * 2 + "rj, wj = self._rootAndWeight(j)",
              I * 2 + "return wj - wi if ri == rj else None", ""]
    if has("time"):
        L += [I + "# O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if",
              I + "# they still aren't. Climbs from both ends, always moving the one that got its parent first",
              I + "def firstConnectedTime(self, i, j):",
              I * 2 + "if self.find(i) != self.find(j):",
              I * 3 + "return -1",
              I * 2 + "par, tm = self.par, self.tm",
              I * 2 + "last = -1",
              I * 2 + "while i != j:",
              I * 3 + "if tm[i] < tm[j]:",
              I * 4 + "last = max(last, tm[i])",
              I * 4 + "i = par[i]",
              I * 3 + "else:",
              I * 4 + "last = max(last, tm[j])",
              I * 4 + "j = par[j]",
              I * 2 + "return last + 1",
              "",
              I + "# O(log n), were i and j together after the first t unites",
              I + "def connectedAt(self, i, j, t):",
              I * 2 + "f = self.firstConnectedTime(i, j)",
              I * 2 + "return f != -1 and f <= t",
              ""]
    if has("grow"):
        L += [I + "# O(1), adds a new element in its own component and returns its index",
              I + "def add(self, val):",
              I * 2 + "i = len(self.par)",
              I * 2 + "self.vals.append(val)",
              I * 2 + "self.par.append(i)",
              I * 2 + "self.sz.append(1)",
              I * 2 + "self.comps += 1",
              I * 2 + "if self.mx < 1:",
              I * 3 + "self.mx = 1"]
        if has("values"):
            L += [I * 2 + "self.csum.append(val)", I * 2 + "self.cmin.append(val)", I * 2 + "self.cmax.append(val)"]
        if has("merge"):
            L += [I * 2 + "self.data.append(self.baseFn(val, i))"]
        if has("members"):
            L += [I * 2 + "self.nxt.append(i)"]
        if has("edges"):
            L += [I * 2 + "self.edges.append(0)"]
        if has("potential"):
            L += [I * 2 + "self.pot.append(0)"]
        if has("time"):
            L += [I * 2 + "self.tm.append(_NEVER)"]
        L += [I * 2 + "return i", ""]
    while L[-1] == "":
        L.pop()
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ C++
CPP_STUBS = '''// e.g. long long, string, pair, struct, ...
using RawVal = long long;

struct Node {
    // long long tot;
    // long long mx;
};

Node baseFn(const RawVal& v, int i) {
    // Node res;
    // res.tot = v, res.mx = v;
    // return res;
}

// called once per merge: big is the bigger component's Node (on a tie, either one). big is moved in, so adding small's
// items into big and returning it costs O(size of small) (small-to-large: O(n log n) in total){roll}
Node combine(Node big, const Node& small) {
    // Node res;
    // res.tot = big.tot + small.tot;
    // res.mx = max(big.mx, small.mx);
    // return res;
}

'''
CPP_ROLL_NOTE = "\n// rollback keeps a copy of\n// the bigger Node every unite, so keep Nodes small here"


def cpp_link(win, lose, has, wv="w", tv="t"):
    out = [f"par[{lose}] = {win};",
           f"sz[{win}] += sz[{lose}];",
           "comps--;",
           f"mx = max(mx, sz[{win}]);"]
    if has("values"):
        out += [f"csum[{win}] += csum[{lose}];",
                f"cmin[{win}] = min(cmin[{win}], cmin[{lose}]);",
                f"cmax[{win}] = max(cmax[{win}], cmax[{lose}]);"]
    if has("merge"):
        out.append(f"data[{win}] = combine(move(data[{win}]), data[{lose}]);")
    if has("members"):
        out.append(f"swap(nxt[{win}], nxt[{lose}]);  // (joins the two circles)")
    if has("edges"):
        out.append(f"edges[{win}] += edges[{lose}] + 1;")
    if has("potential"):
        out.append(f"pot[{lose}] = {wv};")
    if has("time"):
        out.append(f"tm[{lose}] = {tv};")
    return out


def cpp(mode, feats):
    has = feats.__contains__
    cls, comp, nc, roll = CLASS[mode], mode == "compress", mode == "nocompress", mode == "rollback"
    F = "O(α(n)) amortized" if comp else "O(log n)"
    name = folder(mode, feats)
    I = "    "
    L = ["// Template by https://github.com/ishaanbuildsthings", f"// {URL}/{name}/template.cpp",
         "#include <bits/stdc++.h>", "using namespace std;", "using ll = long long;", ""]
    if has("merge"):
        L += CPP_STUBS.replace("{roll}", CPP_ROLL_NOTE if roll else "").split("\n")
        L += [f"// {cls} dsu(vals);"]
    else:
        L += [f"// {cls}<int> dsu(vals);"]
    L += ["// vals: the elements (" + ("numbers: componentSum / Min / Max are over them" if has("values") else "any type: numbers, strings, pairs, ...") +
          "); everything works on their indices 0..n-1" + (", and add(val) appends more" if has("grow") else "")]
    if has("potential"):
        L += ["// potential: every element has a hidden number value[i]; unite(i, j, w) says value[j] - value[i] = w and diff(i, j)",
              "// reads it back (for parity / two-colouring, swap + and - for ^ throughout)"]
    if has("merge"):
        L += [f"struct {cls} {{", I + "using T = RawVal;"]
    else:
        L += ["template <typename T>", f"struct {cls} {{"]
    L += [I + "vector<T> vals;", I + "vector<int> par, sz;", I + "int comps, mx;"]
    if has("values"):
        L += [I + "vector<long long> csum;  // at each root: the sum, min and max of its component's values", I + "vector<T> cmin, cmax;"]
    if has("merge"):
        L += [I + "vector<Node> data;  // data[root]: the Node of root's component"]
    if has("members"):
        L += [I + "vector<int> nxt;  // each component's members linked in a circle: i -> nxt[i] -> ... -> i"]
    if has("edges"):
        L += [I + "vector<int> edges;  // edges[root]: how many unites touched root's component, merging or not"]
    if has("potential"):
        L += [I + "vector<long long> pot;  // pot[i] = value[i] - value[par[i]] (0 at a root)"]
    if has("time"):
        L += [I + "int time = 0;  // how many unites so far, failed ones too",
              I + "vector<int> tm;  // tm[i]: the unite (0, 1, 2, ...) that gave i its parent, INT_MAX at a root"]
    if roll:
        fields = "int i, j, mx;" + (" T lo, hi;" if has("values") else "") + (" Node data;" if has("merge") else "")
        why = "i < 0: a unite that found them already together" + (" (j: its root, for the edge count)" if has("edges") else "")
        L += [I + f"struct Frame {{ {fields} }};  // {why}", I + "vector<Frame> stk;  // one frame per unite, so rollback can undo it"]
    L += ["",
          I + "// O(n), every element starts in its own component",
          I + f"{cls}(const vector<T>& vals{' = {}' if has('grow') else ''}) : vals(vals) {{",
          I * 2 + "int n = vals.size();",
          I * 2 + "par.resize(n);",
          I * 2 + "iota(par.begin(), par.end(), 0);",
          I * 2 + "sz.assign(n, 1);",
          I * 2 + "comps = n;",
          I * 2 + "mx = n ? 1 : 0;"]
    if has("values"):
        L += [I * 2 + "csum.assign(vals.begin(), vals.end());", I * 2 + "cmin = cmax = vals;"]
    if has("merge"):
        L += [I * 2 + "for (int i = 0; i < n; i++) data.push_back(baseFn(vals[i], i));"]
    if has("members"):
        L += [I * 2 + "nxt = par;"]
    if has("edges"):
        L += [I * 2 + "edges.assign(n, 0);"]
    if has("potential"):
        L += [I * 2 + "pot.assign(n, 0);"]
    if has("time"):
        L += [I * 2 + "tm.assign(n, INT_MAX);"]
    L += [I + "}", ""]
    # ---- find
    if comp and has("potential"):
        L += [I + f"// {F}, effectively O(1): index of the representative of i's component (compresses fully, keeping pot",
              I + "// right; union by size keeps the recursion log n deep)",
              I + "int find(int i) {",
              I * 2 + "if (par[i] == i) return i;",
              I * 2 + "int r = find(par[i]);",
              I * 2 + "pot[i] += pot[par[i]];  // (par[i] now hangs straight off r)",
              I * 2 + "return par[i] = r;",
              I + "}"]
    elif comp:
        L += [I + f"// {F}, effectively O(1): index of the representative of i's component",
              I + "int find(int i) {",
              I * 2 + "while (par[i] != i) {",
              I * 3 + "par[i] = par[par[i]];",
              I * 3 + "i = par[i];",
              I * 2 + "}",
              I * 2 + "return i;",
              I + "}"]
    else:
        why = "so the forest records every merge" if nc else "so any unite can be undone"
        L += [I + f"// O(log n), index of the representative of i's component; parents are never rewritten, {why}",
              I + "int find(int i) {",
              I * 2 + "while (par[i] != i) i = par[i];",
              I * 2 + "return i;",
              I + "}"]
    L.append("")
    if has("potential"):
        L += [I + "// {root of i, value[i] - value[root]}", I + "pair<int, long long> rootAndWeight(int i) {"]
        if comp:
            L += [I * 2 + "int r = find(i);", I * 2 + "return {r, pot[i]};"]
        else:
            L += [I * 2 + "long long w = 0;", I * 2 + "for (; par[i] != i; i = par[i]) w += pot[i];", I * 2 + "return {i, w};"]
        L += [I + "}", ""]
    # ---- unite
    doc = [f"{F}, merges the two components, " + ("returns {winner, loser}: the new root and the old root now under it,\n// or {-1, -1} if they were already together" if nc else "false if i and j were already together")]
    if has("potential"):
        doc.append("w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)")
    if has("edges"):
        doc.append("either way it counts as an edge of the component (edgeCount)")
    if has("time"):
        doc.append("each call is the next unite in time (0, 1, 2, ...), failed ones too")
    if roll:
        doc.append("either way it records a frame, so it always takes exactly one rollback to undo")
    L += [I + "// " + line.replace("\n", "\n" + I) for line in doc]
    ret = "pair<int, int>" if nc else "bool"
    L.append(I + f"{ret} unite(int i, int j{', long long w' if has('potential') else ''}) {{")
    body = []
    if has("time"):
        body.append("int t = time++;")
    if has("potential"):
        body += ["auto [ri, wi] = rootAndWeight(i);", "auto [rj, wj] = rootAndWeight(j);", "i = ri, j = rj;"]
    else:
        body.append("i = find(i), j = find(j);")
    body.append("if (i == j) {")
    if has("edges"):
        body.append("    edges[i]++;")
    if roll:
        body.append("    stk.push_back({-1, " + ("i" if has("edges") else "-1") + ", mx});")
    body += ["    return {-1, -1};" if nc else "    return false;", "}"]
    if has("potential"):
        body.append("w += wi - wj;  // now value[j's root] - value[i's root]")
    if has("potential"):
        body += ["if (sz[i] < sz[j]) {", "    swap(i, j);", "    w = -w;", "}"]
    else:
        body.append("if (sz[i] < sz[j]) swap(i, j);")
    if roll:
        frame = ["i", "j", "mx"] + (["cmin[i]", "cmax[i]"] if has("values") else []) + (["data[i]"] if has("merge") else [])
        body.append(f"stk.push_back({{{', '.join(frame)}}});")
    body += cpp_link("i", "j", has)
    body.append("return {i, j};" if nc else "return true;")
    L += [I * 2 + b for b in body]
    L += [I + "}", ""]
    # ---- uniteAUnderB
    if nc:
        L += [I + "// O(log n), forces a's root under b's root, false if already together",
              I + "// skips union by size, so depth can degrade to O(n) and every walk with it"]
        if has("potential"):
            L.append(I + "// w: value[b] - value[a] = w")
        if has("merge"):
            L.append(I + "// combine gets b's component's Node first here, even when it's the smaller one")
        L.append(I + f"bool uniteAUnderB(int a, int b{', long long w' if has('potential') else ''}) {{")
        body = []
        if has("time"):
            body.append("int t = time++;")
        if has("potential"):
            body += ["auto [ra, wa] = rootAndWeight(a);", "auto [rb, wb] = rootAndWeight(b);", "a = ra, b = rb;"]
        else:
            body.append("a = find(a), b = find(b);")
        if has("edges"):
            body += ["if (a == b) {", "    edges[a]++;", "    return false;", "}"]
        else:
            body.append("if (a == b) return false;")
        if has("potential"):
            body.append("w = wb - wa - w;  // now value[a's root] - value[b's root]")
        body += cpp_link("b", "a", has)
        body.append("return true;")
        L += [I * 2 + b for b in body]
        L += [I + "}", ""]
    # ---- rollback
    if roll:
        L += [I + "// O(1), undoes the most recent unite, whether or not it merged anything: k rollbacks always undo the last",
              I + "// k unites" + (" (an add is never undone)" if has("grow") else "") + "; out_of_range if you roll back more unites than you made",
              I + "void rollback() {",
              I * 2 + 'if (stk.empty()) throw out_of_range("rollback: no unite left to undo");',
              I * 2 + "Frame f = stk.back();",
              I * 2 + "stk.pop_back();"]
        if has("edges"):
            L += [I * 2 + "if (f.i < 0) {", I * 3 + "edges[f.j]--;", I * 3 + "return;", I * 2 + "}"]
        else:
            L += [I * 2 + "if (f.i < 0) return;"]
        L += [I * 2 + "int i = f.i, j = f.j;",
              I * 2 + "par[j] = j;",
              I * 2 + "sz[i] -= sz[j];",
              I * 2 + "comps++;",
              I * 2 + "mx = f.mx;"]
        if has("values"):
            L += [I * 2 + "csum[i] -= csum[j];", I * 2 + "cmin[i] = f.lo;", I * 2 + "cmax[i] = f.hi;"]
        if has("merge"):
            L += [I * 2 + "data[i] = move(f.data);"]
        if has("members"):
            L += [I * 2 + "swap(nxt[i], nxt[j]);  // (the same swap splits them again)"]
        if has("edges"):
            L += [I * 2 + "edges[i] -= edges[j] + 1;"]
        if has("potential"):
            L += [I * 2 + "pot[j] = 0;"]
        L += [I + "}", "",
              I + "// O(1), a point to roll back to later: how many unites can be undone right now",
              I + "int checkpoint() { return stk.size(); }", "",
              I + "// O(1) per unite undone, undoes every unite made since checkpoint() returned k",
              I + "void rollbackTo(int k) {",
              I * 2 + "while ((int)stk.size() > k) rollback();",
              I + "}", ""]
    # ---- base queries
    slow = "O(n)" if comp else "O(n log n)"
    L += [I + f"// {F}, true if i and j are in the same component",
          I + "bool areUnioned(int i, int j) { return find(i) == find(j); }", "",
          I + f"// {F}, how many elements are in i's component",
          I + "int size(int i) { return sz[find(i)]; }", "",
          I + "// O(1), how many components exist right now",
          I + "int numComponents() { return comps; }", "",
          I + "// O(1), size of the biggest component" + (", restored by rollback" if roll else ", maintained in unite"),
          I + "int largestSize() { return mx; }", "",
          I + "// O(n), one index per component: the representative each member's find returns",
          I + "vector<int> roots() {",
          I * 2 + "vector<int> res;",
          I * 2 + "for (int i = 0; i < (int)par.size(); i++)",
          I * 3 + "if (par[i] == i) res.push_back(i);",
          I * 2 + "return res;",
          I + "}", "",
          I + "// O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]",
          I + "vector<int> sizes() {",
          I * 2 + "vector<int> res;",
          I * 2 + "for (int i = 0; i < (int)par.size(); i++)",
          I * 3 + "if (par[i] == i) res.push_back(sz[i]);",
          I * 2 + "sort(res.rbegin(), res.rend());",
          I * 2 + "return res;",
          I + "}", "",
          I + f"// {slow}, groupsArr[rt] = values whose root is rt, empty if rt is not a root",
          I + "vector<vector<T>> groups() {",
          I * 2 + "int n = par.size();",
          I * 2 + "vector<vector<T>> groupsArr(n);",
          I * 2 + "for (int i = 0; i < n; i++) groupsArr[find(i)].push_back(vals[i]);",
          I * 2 + "return groupsArr;",
          I + "}", ""]
    if has("members"):
        L += [I + "// O(size of the group), the values of every element in the same group as index i, starting at i",
              I + "vector<T> elementsInGroup(int i) {",
              I * 2 + "vector<T> res = {vals[i]};",
              I * 2 + "for (int j = nxt[i]; j != i; j = nxt[j]) res.push_back(vals[j]);",
              I * 2 + "return res;",
              I + "}", ""]
    else:
        L += [I + f"// {slow}, the values of every element sitting in the same group as index i",
              I + "vector<T> elementsInGroup(int i) {",
              I * 2 + "int rt = find(i);",
              I * 2 + "vector<T> res;",
              I * 2 + "for (int j = 0; j < (int)par.size(); j++)",
              I * 3 + "if (find(j) == rt) res.push_back(vals[j]);",
              I * 2 + "return res;",
              I + "}", ""]
    if has("values"):
        L += [I + f"// {F}, the sum of the values in i's component",
              I + "long long componentSum(int i) { return csum[find(i)]; }", "",
              I + f"// {F}, the smallest value in i's component",
              I + "T componentMin(int i) { return cmin[find(i)]; }", "",
              I + f"// {F}, the largest value in i's component",
              I + "T componentMax(int i) { return cmax[find(i)]; }", ""]
    if has("merge"):
        L += [I + f"// {F}, the Node of i's component: every member's baseFn, combined",
              I + "Node componentData(int i) { return data[find(i)]; }", ""]
    if has("edges"):
        L += [I + f"// {F}, how many unites have touched i's component (merging or not): its edges, if each unite is an edge",
              I + "int edgeCount(int i) { return edges[find(i)]; }", "",
              I + f"// {F}, true if i's component has no cycle: exactly size - 1 edges",
              I + "bool isTree(int i) {",
              I * 2 + "int r = find(i);",
              I * 2 + "return edges[r] == sz[r] - 1;",
              I + "}", ""]
    if has("potential"):
        L += [I + f"// {F}, value[j] - value[i] from the unites so far, nullopt if i and j aren't together",
              I + "optional<long long> diff(int i, int j) {",
              I * 2 + "auto [ri, wi] = rootAndWeight(i);",
              I * 2 + "auto [rj, wj] = rootAndWeight(j);",
              I * 2 + "if (ri != rj) return nullopt;",
              I * 2 + "return wj - wi;",
              I + "}", ""]
    if has("time"):
        L += [I + "// O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if",
              I + "// they still aren't. Climbs from both ends, always moving the one that got its parent first",
              I + "int firstConnectedTime(int i, int j) {",
              I * 2 + "if (find(i) != find(j)) return -1;",
              I * 2 + "int last = -1;",
              I * 2 + "while (i != j) {",
              I * 3 + "if (tm[i] < tm[j]) last = max(last, tm[i]), i = par[i];",
              I * 3 + "else last = max(last, tm[j]), j = par[j];",
              I * 2 + "}",
              I * 2 + "return last + 1;",
              I + "}", "",
              I + "// O(log n), were i and j together after the first t unites",
              I + "bool connectedAt(int i, int j, int t) {",
              I * 2 + "int f = firstConnectedTime(i, j);",
              I * 2 + "return f != -1 && f <= t;",
              I + "}", ""]
    if has("grow"):
        L += [I + "// O(1), adds a new element in its own component and returns its index",
              I + "int add(const T& val) {",
              I * 2 + "int i = par.size();",
              I * 2 + "vals.push_back(val);",
              I * 2 + "par.push_back(i);",
              I * 2 + "sz.push_back(1);",
              I * 2 + "comps++;",
              I * 2 + "mx = max(mx, 1);"]
        if has("values"):
            L += [I * 2 + "csum.push_back(val);", I * 2 + "cmin.push_back(val);", I * 2 + "cmax.push_back(val);"]
        if has("merge"):
            L += [I * 2 + "data.push_back(baseFn(val, i));"]
        if has("members"):
            L += [I * 2 + "nxt.push_back(i);"]
        if has("edges"):
            L += [I * 2 + "edges.push_back(0);"]
        if has("potential"):
            L += [I * 2 + "pot.push_back(0);"]
        if has("time"):
            L += [I * 2 + "tm.push_back(INT_MAX);"]
        L += [I * 2 + "return i;", I + "}", ""]
    while L[-1] == "":
        L.pop()
    L.append("};")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ next free index
NEXT_FREE_PY = '''# Template by https://github.com/ishaanbuildsthings
# {URL}/_next-free/template.py

# nf = NextFree(n)
# Indices 0..n-1 start free; take(i) / takeRange(l, r) use them up, and nextFree / prevFree jump straight to the
# nearest index still free (painting intervals, "assign each query to the first unused slot", ...)


class NextFree:
    # O(n), every index 0..n-1 starts free
    def __init__(self, n):
        self.n = n
        self.nxt = list(range(n + 1))  # follow nxt to the first free index >= i (n: none)
        self.prv = list(range(n + 1))  # follow prv to (the last free index <= i - 1) + 1, shifted so 0 means none

    def _up(self, i):
        nxt = self.nxt
        while nxt[i] != i:
            nxt[i] = nxt[nxt[i]]
            i = nxt[i]
        return i

    def _down(self, i):
        prv = self.prv
        while prv[i] != i:
            prv[i] = prv[prv[i]]
            i = prv[i]
        return i

    # O(α(n)) amortized, the smallest free index >= i, n if there's none; needs 0 <= i <= n, else IndexError
    def nextFree(self, i):
        if not 0 <= i <= self.n:
            raise IndexError(f"nextFree: needs 0 <= i <= n, got i = {i}, n = {self.n}")
        return self._up(i)

    # O(α(n)) amortized, the largest free index <= i, -1 if there's none; needs -1 <= i < n, else IndexError
    def prevFree(self, i):
        if not -1 <= i < self.n:
            raise IndexError(f"prevFree: needs -1 <= i < n, got i = {i}, n = {self.n}")
        return self._down(i + 1) - 1

    # O(α(n)) amortized, True if i hasn't been taken; needs 0 <= i < n, else IndexError
    def isFree(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"isFree: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self._up(i) == i

    # O(α(n)) amortized, uses up index i (nothing if it was already taken); needs 0 <= i < n, else IndexError
    def take(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"take: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if self._up(i) == i:
            self.nxt[i] = i + 1
            self.prv[i + 1] = i

    # O((how many were free) * α(n)) amortized, so O(n α(n)) over every call: uses up every free index in l..r and
    # returns them in order; needs 0 <= l <= r < n, else IndexError
    def takeRange(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"takeRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        res = []
        i = self._up(l)
        while i <= r:
            res.append(i)
            self.nxt[i] = i + 1
            self.prv[i + 1] = i
            i = self._up(i + 1)
        return res
'''

NEXT_FREE_CPP = '''// Template by https://github.com/ishaanbuildsthings
// {URL}/_next-free/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// NextFree nf(n);
// Indices 0..n-1 start free; take(i) / takeRange(l, r) use them up, and nextFree / prevFree jump straight to the
// nearest index still free (painting intervals, "assign each query to the first unused slot", ...)
struct NextFree {
    int n;
    vector<int> nxt;  // follow nxt to the first free index >= i (n: none)
    vector<int> prv;  // follow prv to (the last free index <= i - 1) + 1, shifted so 0 means none

    // O(n), every index 0..n-1 starts free
    explicit NextFree(int n) : n(n), nxt(n + 1), prv(n + 1) {
        iota(nxt.begin(), nxt.end(), 0);
        iota(prv.begin(), prv.end(), 0);
    }

    int up(int i) {
        while (nxt[i] != i) i = nxt[i] = nxt[nxt[i]];
        return i;
    }

    int down(int i) {
        while (prv[i] != i) i = prv[i] = prv[prv[i]];
        return i;
    }

    // O(α(n)) amortized, the smallest free index >= i, n if there's none; needs 0 <= i <= n, else out_of_range
    int nextFree(int i) {
        if (i < 0 || i > n) throw out_of_range("nextFree: needs 0 <= i <= n");
        return up(i);
    }

    // O(α(n)) amortized, the largest free index <= i, -1 if there's none; needs -1 <= i < n, else out_of_range
    int prevFree(int i) {
        if (i < -1 || i >= n) throw out_of_range("prevFree: needs -1 <= i < n");
        return down(i + 1) - 1;
    }

    // O(α(n)) amortized, true if i hasn't been taken; needs 0 <= i < n, else out_of_range
    bool isFree(int i) {
        if (i < 0 || i >= n) throw out_of_range("isFree: needs 0 <= i < n");
        return up(i) == i;
    }

    // O(α(n)) amortized, uses up index i (nothing if it was already taken); needs 0 <= i < n, else out_of_range
    void take(int i) {
        if (i < 0 || i >= n) throw out_of_range("take: needs 0 <= i < n");
        if (up(i) == i) nxt[i] = i + 1, prv[i + 1] = i;
    }

    // O((how many were free) * α(n)) amortized, so O(n α(n)) over every call: uses up every free index in l..r and
    // returns them in order; needs 0 <= l <= r < n, else out_of_range
    vector<int> takeRange(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("takeRange: needs 0 <= l <= r < n");
        vector<int> res;
        for (int i = up(l); i <= r; i = up(i + 1)) {
            res.push_back(i);
            nxt[i] = i + 1, prv[i + 1] = i;
        }
        return res;
    }
};
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or open(path).read() != text:
        open(path, "w").write(text)
        return 1
    return 0


def main():
    written = count = 0
    keep = set()
    for mode, feats in combos():
        name = folder(mode, feats)
        keep.add(name)
        written += write(os.path.join(DIR, name, "template.py"), py(mode, feats))
        written += write(os.path.join(DIR, name, "template.cpp"), cpp(mode, feats))
        count += 1
    written += write(os.path.join(DIR, "_next-free", "template.py"), NEXT_FREE_PY.replace("{URL}", URL))
    written += write(os.path.join(DIR, "_next-free", "template.cpp"), NEXT_FREE_CPP.replace("{URL}", URL))
    stale = [d for d in os.listdir(DIR) if not d.startswith("_") and d not in keep]
    assert not stale, f"folders no combination makes any more (delete them): {stale[:5]}"
    base, extra = op_parts()
    ts = ("// Generated by templates/ultimate-template-tool/union-find-tests/gen_union_find.py. Do not edit.\n"
          "// The ops every union find of a find mode has, and what each extra adds (an op of the same name replaces it).\n"
          f"export const UNION_FIND_MODES = {json.dumps(MODES)} as const;\n"
          f"export const UNION_FIND_EXTRAS = {json.dumps(FEATS)} as const;\n"
          f"export const UNION_FIND_CLASS: Record<string, string> = {json.dumps(CLASS)};\n"
          f"export const UNION_FIND_BASE_OPS: Record<string, [string, string][]> = {json.dumps(base)};\n"
          f"export const UNION_FIND_EXTRA_OPS: Record<string, Record<string, [string, string][]>> = {json.dumps(extra)};\n")
    written += write(SITE_MANIFEST, ts)
    for d in sorted(keep) + ["_next-free"]:
        for f in ("template.py", "template.cpp"):
            written += write(os.path.join(SITE_PUBLIC, d, f), open(os.path.join(DIR, d, f)).read())
    for f in ("hdlt.py", "hdlt.cpp"):
        written += write(os.path.join(SITE_PUBLIC, "_hdlt", f), open(os.path.join(HDLT, f)).read())
    stale = [d for d in os.listdir(SITE_PUBLIC) if d not in keep and d not in ("_next-free", "_hdlt")]
    assert not stale, f"stale site copies (delete them): {stale[:5]}"
    print(f"{count} union finds (+ next free), {written} files written")


if __name__ == "__main__":
    main()
