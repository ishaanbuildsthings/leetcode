"""Union find templates for the site's Union find tab: one find mode plus any set of extras, in Python and C++.

    find modes   compress     path compression: fastest, but parents get rewritten
                 nocompress   parents never change, so the forest is a record of every merge (parent(i) walks it)
                 rollback     no compression plus an undo stack: rollbackLastUnion()
    extras       values       componentSum / componentMin / componentMax of the elements' values
                 merge        your own Node per component: baseFn(v, i) and combine(big, small), like the generic seg tree
                 members      each component's members linked in a circle: elementsInGroup in O(size of the group)
                 grow         add(val): a new element in its own component

Writes templates/ultimate-template-tool/union-find/<mode>[-extra...]/template.py and template.cpp (folder name: the
mode, then the extras in the order above), the remove-only set (a union find over its range) in union-find/remove-only-set/, and union-find/hdlt/:
templates/union-find/hdlt.* plus unite / areUnioned, the names the others use. Every file carries the picker header
(@operations / @complexities / @memory); site/scripts/build-union-find-templates.mjs reads them for the Union find tab.

    python3 gen_union_find.py
"""
import itertools
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DIR = os.environ.get("UNION_FIND_DIR") or os.path.join(REPO, "templates", "ultimate-template-tool", "union-find")
HDLT = os.path.join(REPO, "templates", "union-find")  # (the hand-written fully dynamic connectivity, shown beside them)
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find"

MODES = ["compress", "nocompress", "rollback"]
FEATS = ["values", "merge", "members", "grow"]
CLASS = {"compress": "DSU", "nocompress": "DSUNoCompress", "rollback": "RollbackDSU"}


def folder(mode, feats):
    return "-".join([mode] + [f for f in FEATS if f in feats])


def combos():
    for mode in MODES:
        for k in range(len(FEATS) + 1):
            for feats in itertools.combinations(FEATS, k):
                yield mode, set(feats)


TYPE = {"compress": "dsu", "nocompress": "dsu-nocompress", "rollback": "dsu-rollback"}


def header(mode, feats, cm):
    """the picker's header for one template: its ops (the method names) with costs, and what it stores"""
    has = feats.__contains__
    F = "α(N) amortized" if mode == "compress" else "log(N)"
    slow = "N" if mode == "compress" else "N*log(N)"
    cost = {"find": F, "unite": F, "areUnioned": F, "size": F,
            "numComponents": "1", "largestSize": "1", "roots": "N", "sizes": "N*log(N)", "groups": slow,
            "elementsInGroup": "K" if has("members") else slow}
    if mode == "rollback":
        cost.update(rollbackLastUnion="1")
    if mode != "compress":
        cost["parent"] = "1"
    if has("values"):
        cost.update(componentSum=F, componentMin=F, componentMax=F)
    if has("merge"):
        cost["componentData"] = F
    if has("grow"):
        cost["add"] = "1 amortized"
    other = ["vals[1*N]"]
    other += ["csum[1*N]", "cmin[1*N]", "cmax[1*N]"] if has("values") else []
    other += ["data[1*N]"] if has("merge") else []
    other += ["nxt[1*N]"] if has("members") else []
    notes = []
    if has("members"):
        notes.append("K = the size of the group")
    if mode == "rollback":
        notes.append("plus the undo stack: one small frame per unite not yet undone" + (", holding a copy of the bigger Node" if has("merge") else ""))
    if has("merge"):
        notes.append("data holds one Node per element")
    ops = sorted(cost)
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {TYPE[mode]}", "@complexities:"]
    lines += [f"  {op}: {cost[op]}" for op in ops]
    lines += ["  build: N", "@memory:", "  layout: none", "  node: par[1*N] sz[1*N]", "  tags: none", f"  other: {' '.join(other)}"]
    lines += [f"  note: {'; '.join(notes)}"] if notes else []
    return [f"{cm} {x}" for x in lines]


def find_cost(mode):
    return "α(n) amortized" if mode == "compress" else "log n"


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


def py_link(win, lose, has):
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
    return out


def py(mode, feats):
    has = feats.__contains__
    cls, comp, nc, roll = CLASS[mode], mode == "compress", mode == "nocompress", mode == "rollback"
    F = "O(α(n)) amortized" if comp else "O(log n)"
    name = folder(mode, feats)
    L = ["# Template by https://github.com/ishaanbuildsthings", f"# {URL}/{name}/template.py"] + header(mode, feats, "#") + [""]
    if has("merge"):
        L += PY_STUBS.replace("{mutate}", PY_MUTATE[mode]).rstrip("\n").split("\n") + ["", ""]
    ctor = f"{cls}(vals, baseFn, combine)" if has("merge") else f"{cls}(vals)"
    L += [f"# dsu = {ctor}",
          "# vals: the elements (" + ("numbers: componentSum / Min / Max are over them" if has("values") else "any values: numbers, strings, tuples, ...") +
          "); everything works on their indices 0..n-1" + (", and add(val) appends more" if has("grow") else "")]
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
    if roll:
        L += [I * 2 + "self.stk = []  # one frame per unite, so rollback can undo it"]
    L.append("")
    # ---- find
    if comp:
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
    # ---- unite
    doc = [f"{F}, merges the two components, " + ("returns (winner, loser): the new root and the old root now under it, or\n# None if they were already together" if nc else "False if i and j were already together")]
    if roll:
        doc.append("either way it records a frame, so it always takes exactly one rollbackLastUnion to undo")
    L += [I + "# " + line.replace("\n", "\n" + I) for line in doc]
    L.append(I + "def unite(self, i, j):")
    body = []
    body += ["i, j = self.find(i), self.find(j)"]
    body.append("if i == j:")
    if roll:
        body.append("    self.stk.append(" + "None)")
    body.append("    return None" if nc else "    return False")
    body += ["if self.sz[i] < self.sz[j]:", "    i, j = j, i"]
    if roll:
        frame = ["i", "j", "self.mx"] + (["self.cmin[i]", "self.cmax[i]"] if has("values") else []) + (["self.data[i]"] if has("merge") else [])
        body.append(f"self.stk.append(({', '.join(frame)}))")
    body += py_link("i", "j", has)
    body.append("return i, j" if nc else "return True")
    L += [I * 2 + b for b in body]
    L.append("")
    # ---- rollback
    if roll:
        L += [I + "# O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last",
              I + "# k unites" + (" (an add is never undone)" if has("grow") else "") + "; IndexError if there's no unite left to undo",
              I + "def rollbackLastUnion(self):",
              I * 2 + "frame = self.stk.pop()"]
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
        L += [""]
    # ---- the base queries
    slow = "O(n)" if comp else "O(n log n)"
    if not comp:
        L += [I + "# O(1), i's parent pointer (i itself if it's a root): without path compression the pointers never change",
              I + "# once set" + (" (until rolled back)" if roll else "") + ", so you can walk them and keep your own data per pointer",
              I + "def parent(self, i):",
              I * 2 + "return self.par[i]",
              ""]
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
          I + f"# {slow}, one list of values per component (no empty lists), e.g. vals [10, 20, 30, 40] with 0-2 and 1-3",
          I + "# united -> [[10, 30], [20, 40]]; components ordered by their smallest index, values in index order",
          I + "def groups(self):",
          I * 2 + "n = len(self.par)",
          I * 2 + "slot = [-1] * n  # slot[rt] = where root rt's list sits in groupsArr",
          I * 2 + "groupsArr = []",
          I * 2 + "for i in range(n):",
          I * 3 + "rt = self.find(i)",
          I * 3 + "if slot[rt] == -1:",
          I * 4 + "slot[rt] = len(groupsArr)",
          I * 4 + "groupsArr.append([])",
          I * 3 + "groupsArr[slot[rt]].append(self.vals[i])",
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


def cpp_link(win, lose, has):
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
    return out


def cpp(mode, feats):
    has = feats.__contains__
    cls, comp, nc, roll = CLASS[mode], mode == "compress", mode == "nocompress", mode == "rollback"
    F = "O(α(n)) amortized" if comp else "O(log n)"
    name = folder(mode, feats)
    I = "    "
    L = ["// Template by https://github.com/ishaanbuildsthings", f"// {URL}/{name}/template.cpp"] + header(mode, feats, "//") + [
         "#include <bits/stdc++.h>", "using namespace std;", "using ll = long long;", ""]
    if has("merge"):
        L += CPP_STUBS.replace("{roll}", CPP_ROLL_NOTE if roll else "").split("\n")
        L += [f"// {cls} dsu(vals);"]
    else:
        L += [f"// {cls}<int> dsu(vals);"]
    L += ["// vals: the elements (" + ("numbers: componentSum / Min / Max are over them" if has("values") else "any type: numbers, strings, pairs, ...") +
          "); everything works on their indices 0..n-1" + (", and add(val) appends more" if has("grow") else "")]
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
    if roll:
        fields = "int i, j, mx;" + (" T lo, hi;" if has("values") else "") + (" Node data;" if has("merge") else "")
        why = "i < 0: a unite that found them already together"
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
    L += [I + "}", ""]
    # ---- find
    if comp:
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
    # ---- unite
    doc = [f"{F}, merges the two components, " + ("returns {winner, loser}: the new root and the old root now under it,\n// or {-1, -1} if they were already together" if nc else "false if i and j were already together")]
    if roll:
        doc.append("either way it records a frame, so it always takes exactly one rollbackLastUnion to undo")
    L += [I + "// " + line.replace("\n", "\n" + I) for line in doc]
    ret = "pair<int, int>" if nc else "bool"
    L.append(I + f"{ret} unite(int i, int j) {{")
    body = []
    body.append("i = find(i), j = find(j);")
    body.append("if (i == j) {")
    if roll:
        body.append("    stk.push_back({-1, " + "-1" + ", mx});")
    body += ["    return {-1, -1};" if nc else "    return false;", "}"]
    body.append("if (sz[i] < sz[j]) swap(i, j);")
    if roll:
        frame = ["i", "j", "mx"] + (["cmin[i]", "cmax[i]"] if has("values") else []) + (["data[i]"] if has("merge") else [])
        body.append(f"stk.push_back({{{', '.join(frame)}}});")
    body += cpp_link("i", "j", has)
    body.append("return {i, j};" if nc else "return true;")
    L += [I * 2 + b for b in body]
    L += [I + "}", ""]
    # ---- rollback
    if roll:
        L += [I + "// O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last",
              I + "// k unites" + (" (an add is never undone)" if has("grow") else "") + "; out_of_range if there's no unite left to undo",
              I + "void rollbackLastUnion() {",
              I * 2 + 'if (stk.empty()) throw out_of_range("rollbackLastUnion: no unite left to undo");',
              I * 2 + "Frame f = stk.back();",
              I * 2 + "stk.pop_back();"]
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
        L += [I + "}", ""]
    # ---- base queries
    slow = "O(n)" if comp else "O(n log n)"
    if not comp:
        L += [I + "// O(1), i's parent pointer (i itself if it's a root): without path compression the pointers never change",
              I + "// once set" + (" (until rolled back)" if roll else "") + ", so you can walk them and keep your own data per pointer",
              I + "int parent(int i) { return par[i]; }", ""]
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
          I + f"// {slow}, one vector of values per component (no empty ones), e.g. vals {{10, 20, 30, 40}} with 0-2 and 1-3",
          I + "// united -> {{10, 30}, {20, 40}}; components ordered by their smallest index, values in index order",
          I + "vector<vector<T>> groups() {",
          I * 2 + "int n = par.size();",
          I * 2 + "vector<int> slot(n, -1);  // slot[rt] = where root rt's vector sits in groupsArr",
          I * 2 + "vector<vector<T>> groupsArr;",
          I * 2 + "for (int i = 0; i < n; i++) {",
          I * 3 + "int rt = find(i);",
          I * 3 + "if (slot[rt] == -1) {",
          I * 4 + "slot[rt] = groupsArr.size();",
          I * 4 + "groupsArr.emplace_back();",
          I * 3 + "}",
          I * 3 + "groupsArr[slot[rt]].push_back(vals[i]);",
          I * 2 + "}",
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
        L += [I * 2 + "return i;", I + "}", ""]
    while L[-1] == "":
        L.pop()
    L.append("};")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ remove-only set
REMOVE_ONLY_PY = '''# Template by https://github.com/ishaanbuildsthings
# {URL}/remove-only-set/template.py
# @operations: contains largestLtX largestLteX max min popInValRange popMax popMin remove smallestGtX smallestGteX
# @data-structure-type: remove-only-set
# @complexities:
#   contains: 1
#   largestLtX: α(N) amortized
#   largestLteX: α(N) amortized
#   max: α(N) amortized
#   min: α(N) amortized
#   popInValRange: α(N) amortized
#   popMax: α(N) amortized
#   popMin: α(N) amortized
#   remove: α(N) amortized
#   smallestGtX: α(N) amortized
#   smallestGteX: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] lo[1*N] hi[1*N]
#   tags: none
#   other: present[1*N]
#   note: popInValRange costs α(N) per value it removes, and a value is only removed once, so O(N α(N)) over every call together

# s = RemoveOnlySet(10)  # holds 0, 1, 2, ..., 9
# A set of 0..n-1 that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the
# nearest value still in it from any x, present or not.
# Union find underneath: a removed value joins the group to its right, so each group is a run of removed values plus
# the one present value at its right end; the root keeps the group's two ends, and groups are linked by size.


class RemoveOnlySet:
    # O(n) -- holds 0, 1, ..., n-1
    def __init__(self, n):
        self.n = self.cnt = n
        self.present = bytearray([1]) * (n + 1)  # index n: a stand-in that never leaves, so every group has a right end
        self.par = list(range(n + 1))
        self.lo = list(range(n + 1))  # at a root: the group's smallest value
        self.hi = list(range(n + 1))  # at a root: the group's largest value, the only one still present

    def _find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(1) -- True if x is in the set (any x is fine)
    def contains(self, x):
        return 0 <= x < self.n and self.present[x] == 1

    # O(1) -- how many values are still in the set
    def size(self):
        return self.cnt

    # O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    def remove(self, x):
        if not self.contains(x):
            return 0
        self.present[x] = 0
        self.cnt -= 1
        left = self._find(x)
        right = self._find(x + 1)
        lo, hi = self.lo, self.hi
        if hi[left] - lo[left] > hi[right] - lo[right]:
            self.par[right] = left
            hi[left] = hi[right]
        else:
            self.par[left] = right
            lo[right] = lo[left]
        return 1

    # O(α(N)) amortized -- smallest value >= x; None if there is none (any x is fine)
    def smallestGteX(self, x):
        if x >= self.n:
            return None
        found = self.hi[self._find(max(x, 0))]
        return None if found == self.n else found

    # O(α(N)) amortized -- smallest value > x; None if there is none (any x is fine)
    def smallestGtX(self, x):
        return self.smallestGteX(x + 1)

    # O(α(N)) amortized -- largest value <= x; None if there is none (any x is fine)
    def largestLteX(self, x):
        x = min(x, self.n - 1)
        if x < 0:
            return None
        if self.present[x]:
            return x
        found = self.lo[self._find(x)] - 1
        return None if found < 0 else found

    # O(α(N)) amortized -- largest value < x; None if there is none (any x is fine)
    def largestLtX(self, x):
        return self.largestLteX(x - 1)

    # O(α(N)) amortized -- the smallest value; raises IndexError if empty
    def min(self):
        if not self.cnt:
            raise IndexError("min: the set is empty")
        return self.smallestGteX(0)

    # O(α(N)) amortized -- the largest value; raises IndexError if empty
    def max(self):
        if not self.cnt:
            raise IndexError("max: the set is empty")
        return self.largestLteX(self.n - 1)

    # O(α(N)) amortized -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        x = self.min()
        self.remove(x)
        return x

    # O(α(N)) amortized -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        x = self.max()
        self.remove(x)
        return x

    # O(α(N)) per value removed, amortized -- remove every value in [lo, hi] and return them in increasing order
    # ([] if lo > hi)
    def popInValRange(self, lo, hi):
        res = []
        x = self.smallestGteX(lo)
        while x is not None and x <= hi:
            self.remove(x)
            res.append(x)
            x = self.smallestGteX(x + 1)
        return res
'''

REMOVE_ONLY_CPP = '''// Template by https://github.com/ishaanbuildsthings
// {URL}/remove-only-set/template.cpp
// @operations: contains largestLtX largestLteX max min popInValRange popMax popMin remove smallestGtX smallestGteX
// @data-structure-type: remove-only-set
// @complexities:
//   contains: 1
//   largestLtX: α(N) amortized
//   largestLteX: α(N) amortized
//   max: α(N) amortized
//   min: α(N) amortized
//   popInValRange: α(N) amortized
//   popMax: α(N) amortized
//   popMin: α(N) amortized
//   remove: α(N) amortized
//   smallestGtX: α(N) amortized
//   smallestGteX: α(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] lo[1*N] hi[1*N]
//   tags: none
//   other: present[1*N]
//   note: popInValRange costs α(N) per value it removes, and a value is only removed once, so O(N α(N)) over every call together
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// RemoveOnlySet s(10);  // holds 0, 1, 2, ..., 9
// A set of 0..n-1 that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the
// nearest value still in it from any x, present or not. Searches that find nothing return -1.
// Union find underneath: a removed value joins the group to its right, so each group is a run of removed values plus
// the one present value at its right end; the root keeps the group's two ends, and groups are linked by size.
struct RemoveOnlySet {
    int n, cnt;
    vector<int> par;
    vector<int> lo;        // at a root: the group's smallest value
    vector<int> hi;        // at a root: the group's largest value, the only one still present
    vector<char> present;  // present[n] = 1: a stand-in that never leaves, so every group has a right end

    // O(n) -- holds 0, 1, ..., n-1
    explicit RemoveOnlySet(int n) : n(n), cnt(n), par(n + 1), lo(n + 1), hi(n + 1), present(n + 1, 1) {
        iota(par.begin(), par.end(), 0), iota(lo.begin(), lo.end(), 0), iota(hi.begin(), hi.end(), 0);
    }

    int find(int i) {
        while (par[i] != i) i = par[i] = par[par[i]];
        return i;
    }

    // O(1) -- true if x is in the set (any x is fine)
    bool contains(int x) { return x >= 0 && x < n && present[x]; }

    // O(1) -- how many values are still in the set
    int size() { return cnt; }

    // O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    int remove(int x) {
        if (!contains(x)) return 0;
        present[x] = 0;
        cnt--;
        int left = find(x), right = find(x + 1);
        if (hi[left] - lo[left] > hi[right] - lo[right]) par[right] = left, hi[left] = hi[right];
        else par[left] = right, lo[right] = lo[left];
        return 1;
    }

    // O(α(N)) amortized -- smallest value >= x; -1 if there is none (any x is fine)
    int smallestGteX(int x) {
        if (x >= n) return -1;
        int found = hi[find(std::max(x, 0))];
        return found == n ? -1 : found;
    }

    // O(α(N)) amortized -- smallest value > x; -1 if there is none (any x is fine)
    int smallestGtX(int x) { return x >= n ? -1 : smallestGteX(x + 1); }

    // O(α(N)) amortized -- largest value <= x; -1 if there is none (any x is fine)
    int largestLteX(int x) {
        x = std::min(x, n - 1);
        if (x < 0) return -1;
        if (present[x]) return x;
        return lo[find(x)] - 1;
    }

    // O(α(N)) amortized -- largest value < x; -1 if there is none (any x is fine)
    int largestLtX(int x) { return x <= 0 ? -1 : largestLteX(x - 1); }

    // O(α(N)) amortized -- the smallest value; out_of_range if empty
    int min() {
        if (!cnt) throw out_of_range("min: the set is empty");
        return smallestGteX(0);
    }

    // O(α(N)) amortized -- the largest value; out_of_range if empty
    int max() {
        if (!cnt) throw out_of_range("max: the set is empty");
        return largestLteX(n - 1);
    }

    // O(α(N)) amortized -- remove and return the smallest value; out_of_range if empty
    int popMin() {
        int x = min();
        remove(x);
        return x;
    }

    // O(α(N)) amortized -- remove and return the largest value; out_of_range if empty
    int popMax() {
        int x = max();
        remove(x);
        return x;
    }

    // O(α(N)) per value removed, amortized -- remove every value in [lo, hi] and return them in increasing order
    // (empty if lo > hi)
    vector<int> popInValRange(int lo, int hi) {
        vector<int> res;
        for (int x = smallestGteX(lo); x != -1 && x <= hi; x = smallestGtX(x)) remove(x), res.push_back(x);
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


HDLT_HEADER = [
    "@operations: areUnioned elementsInGroup groups numComponents removeEdge roots size sizes unite",
    "@data-structure-type: hdlt",
    "@complexities:",
    "  areUnioned: log(N)",
    "  elementsInGroup: N*log(N)",
    "  groups: N*log(N)",
    "  numComponents: 1",
    "  removeEdge: log^2(N) amortized",
    "  roots: N*log(N)",
    "  size: log(N)",
    "  sizes: N*log(N)",
    "  unite: log^2(N) amortized",
    "  build: N*log(N)",
    "@memory:",
    "  layout: none",
    "  node: forests[3*N*log(N)]",
    "  tags: none",
    "  other: vals[1*N]",
    "  note: about log N levels, each an Euler-tour treap of up to 3N nodes, plus a few arrays per edge: n = 1e5 is roughly 80 MB in C++",
]
HDLT_PY_ALIASES = """

    # O(log^2 n) amortized, adds an edge between u and v (even if they're already together, and even a second copy of
    # the same edge); True if it joined two components
    def unite(self, u, v):
        merged = not self.areConnected(u, v)
        self._addEdge(u, v)
        return merged

    # O(log^2 n) amortized, removes one edge between u and v (with several copies, one of them); True if its component
    # split in two. Raises KeyError if there is no edge between u and v
    def removeEdge(self, u, v):
        ids = self._byPair.get(self._pairKey(u, v))
        if not ids:
            raise KeyError(f"removeEdge: no edge between {u} and {v}")
        return self._removeEdgeById(ids[-1])

    # same as areConnected (the name the other union finds use)
    def areUnioned(self, u, v):
        return self.areConnected(u, v)
"""
HDLT_CPP_ALIASES = """
    // O(log^2 n) amortized, adds an edge between u and v (even if they're already together, and even a second copy of
    // the same edge); true if it joined two components
    bool unite(int u, int v) {
        bool merged = !areConnected(u, v);
        addEdgeId(u, v);
        return merged;
    }

    // O(log^2 n) amortized, removes one edge between u and v (with several copies, one of them); true if its component
    // split in two. Throws out_of_range if there is no edge between u and v
    bool removeEdge(int u, int v) {
        auto it = byPair.find({min(u, v), max(u, v)});
        if (it == byPair.end() || it->second.empty()) throw out_of_range("removeEdge: no edge between u and v");
        return removeEdgeById(it->second.back());
    }

    // same as areConnected (the name the other union finds use)
    bool areUnioned(int u, int v) { return areConnected(u, v); }
};
"""


def hdlt():
    """templates/union-find/hdlt.* with the picker header and the C++ prelude. Edges are named by their two ends only:
    the id-based addEdge / removeEdge(e) and componentId become internal (_addEdge / _removeEdgeById, addEdgeId / removeEdgeById), and
    unite(u, v) / removeEdge(u, v) / areUnioned are added at the end"""
    py_src = open(os.path.join(HDLT, "hdlt.py")).read().rstrip("\n")
    cpp_src = open(os.path.join(HDLT, "hdlt.cpp")).read().rstrip("\n")
    assert cpp_src.endswith("};") and "#include" not in cpp_src

    def swap(src, pairs):
        for old, new in pairs:
            assert src.count(old) == 1, old
            src = src.replace(old, new)
        return src

    py_src = swap(py_src, [
        ("    # O(log^2 n) amortized, returns an edge id you hand back to removeEdge\n    def addEdge(self, u, v):",
         "    # O(log^2 n) amortized, adds an edge and returns its internal id (unite is the public way in)\n    def _addEdge(self, u, v):"),
        ("    # O(log^2 n) amortized, true if the component actually split in two\n    def removeEdge(self, e):",
         "    # O(log^2 n) amortized, removes the edge with this internal id; true if the component actually split in two\n    def _removeEdgeById(self, e):"),
    ])
    k = py_src.index("    # O(log^2 n) amortized, removes one edge between u and v, false if there was none\n    def removeEdgeBetween(")
    j = py_src.index("\n\n", k)
    py_src = py_src[:k] + py_src[j + 2:]
    py_src = py_src.replace("Public: addEdge, removeEdge, removeEdgeBetween,", "Public: unite, removeEdge,")
    # componentId (an internal label, not an element) is only a helper for roots / groups / sizes / elementsInGroup
    py_src = py_src.replace("componentId, roots, groups,", "roots, groups,")
    py_src = py_src.replace("def componentId(", "def _componentId(").replace("self.componentId(", "self._componentId(")
    assert "removeEdgeBetween" not in py_src and "def addEdge" not in py_src and "self.addEdge(" not in py_src
    assert "self.removeEdge(" not in py_src

    cpp_src = swap(cpp_src, [
        ("    // O(log^2 n) amortized, returns an edge id you hand back to removeEdge\n    int addEdge(int u, int v) {",
         "    // O(log^2 n) amortized, adds an edge and returns its internal id (unite is the public way in)\n    int addEdgeId(int u, int v) {"),
        ("    // O(log^2 n) amortized, true if the component actually split in two\n    bool removeEdge(int e) {",
         "    // O(log^2 n) amortized, removes the edge with this internal id; true if the component actually split in two\n    bool removeEdgeById(int e) {"),
    ])
    k = cpp_src.index("    // O(log^2 n) amortized, removes one edge between u and v, false if there was none\n    bool removeEdge(int u, int v) {")
    j = cpp_src.index("\n\n", k)
    cpp_src = cpp_src[:k] + cpp_src[j + 2:]
    cpp_src = cpp_src.replace("componentId(", "componentKey(")
    assert "removeEdge(" not in cpp_src and "addEdge(" not in cpp_src, [l for l in cpp_src.split("\n") if "removeEdge(" in l or "addEdge(" in l]

    def top(cm, f):
        return (f"{cm} Template by https://github.com/ishaanbuildsthings\n{cm} {URL}/hdlt/{f}\n" +
                "".join(f"{cm} {x}\n" for x in HDLT_HEADER))

    note = "(templates/union-find/hdlt.{}, with edges named by their two ends: unite / removeEdge / areUnioned at the end)"
    py_out = top("#", "template.py") + "# " + note.format("py") + "\n\n" + py_src + HDLT_PY_ALIASES
    cpp_out = (top("//", "template.cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" +
               "// " + note.format("cpp") + "\n" + cpp_src[:-2].rstrip("\n") + "\n" + HDLT_CPP_ALIASES)
    return py_out, cpp_out


def main():
    written = count = 0
    keep = {"remove-only-set", "hdlt"}
    for mode, feats in combos():
        name = folder(mode, feats)
        keep.add(name)
        written += write(os.path.join(DIR, name, "template.py"), py(mode, feats))
        written += write(os.path.join(DIR, name, "template.cpp"), cpp(mode, feats))
        count += 1
    written += write(os.path.join(DIR, "remove-only-set", "template.py"), REMOVE_ONLY_PY.replace("{URL}", URL))
    written += write(os.path.join(DIR, "remove-only-set", "template.cpp"), REMOVE_ONLY_CPP.replace("{URL}", URL))
    py_h, cpp_h = hdlt()
    written += write(os.path.join(DIR, "hdlt", "template.py"), py_h)
    written += write(os.path.join(DIR, "hdlt", "template.cpp"), cpp_h)
    stale = [d for d in os.listdir(DIR) if d not in keep]
    assert not stale, f"folders no combination makes any more (delete them): {stale[:5]}"
    print(f"{count} union finds + remove-only set + HDLT, {written} files written (then npm run gen:union-find in site/)")


if __name__ == "__main__":
    main()
