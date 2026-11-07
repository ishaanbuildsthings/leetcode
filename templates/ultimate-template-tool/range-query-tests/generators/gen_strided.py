"""Strided queries: an aggregate of a[l], a[l + step], a[l + 2 * step], ... up to at most r, in O(sqrt(N)) or so.

    python3 gen_strided.py            # then gen_fast.py, then npm run gen:range-queries in site/

Fix a stride and split the array into one list per position mod stride, laid end to end: a strided query is then a
contiguous range of that stride's list, so small strides are ordinary range queries. A stride above the cutoff visits
few positions, so it just walks them.

Templates, for every non-empty subset of {sum, xor, min, max, gcd, and, or}:
  sqrt-strided-updates-<subset>: point updates. Sum and xor keep block sums per stride (cutoff sqrt(N), no log); the
      others keep a seg tree per stride (cutoff sqrt(N / log N), so updates and queries both cost sqrt(N log N)).
  sqrt-strided-static-<subset>: no updates and linear memory. One prefix array / sparse table per aggregate, rebuilt
      when the step changes, so asking the queries grouped by step (sort them offline) costs one build per distinct step.
And:
  sqrt-strided-prefix-<sum / xor / sum-xor>: no updates, every small stride's prefix array built up front: O(1) for a small
      stride, at N sqrt(N) memory. The updates template beats it on paper, so check_catalog.py keeps it on purpose.
  sqrt-strided-add: stridedAdd with point reads and writes (a Fenwick tree of differences per small stride).
"""
import itertools
import os
import sys

DIR = os.environ.get("RANGE_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries"
FAMS = ["sum", "xor", "min", "max", "gcd", "and", "or"]
BLOCK = {"sum", "xor"}
OP = {"sum": "stridedSum", "xor": "stridedXorQuery", "min": "stridedMin", "max": "stridedMax", "gcd": "stridedGcd",
      "and": "stridedAndQuery", "or": "stridedOrQuery"}
WHAT = {"sum": "a[l] + a[l + step] + ...", "xor": "a[l] ^ a[l + step] ^ ...", "min": "min of a[l], a[l + step], ...",
        "max": "max of a[l], a[l + step], ...", "gcd": "gcd of a[l], a[l + step], ...",
        "and": "a[l] & a[l + step] & ...", "or": "a[l] | a[l + step] | ..."}
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
RANGE_RULE = "needs 0 <= l <= r < n and step >= 1"
WALK = {"cpp": 32, "py": 1024}  # a query this short never rebuilds a cached table: walking it is cheaper

CPP_OP = {"min": "min({a}, {b})", "max": "max({a}, {b})", "gcd": "std::gcd({a}, {b})", "and": "({a} & {b})", "or": "({a} | {b})"}
PY_INLINE = {"min": "{a} if {a} < {b} else {b}", "max": "{a} if {a} > {b} else {b}", "gcd": "gcd({a}, {b})",
             "and": "{a} & {b}", "or": "{a} | {b}"}
PY_FN = {"min": "min", "max": "max", "gcd": "gcd", "and": "and_", "or": "or_"}
PY_WALK = {"sum": "sum({s})", "xor": "reduce(xor, {s})", "min": "min({s})", "max": "max({s})", "gcd": "gcd(*{s})",
           "and": "reduce(and_, {s})", "or": "reduce(or_, {s})"}


def header(c, ops, costs, memory, note):
    lines = [f"@operations: {' '.join(sorted(ops))}", "@data-structure-type: sqrt", "@complexities:"]
    lines += [f"  {op}: {costs[op]}" for op in sorted(ops)] + [f"  build: {costs['build']}", "@memory:", "  layout: none"]
    lines += [f"  {k}: {memory[k]}" for k in ("node", "tags", "other")] + [f"  note: {note}"]
    return "\n".join(f"{c} {x}" for x in lines) + "\n"


def write(folder, py_body, cpp_body, ops, costs, memory, notes, about):
    path = os.path.join(DIR, folder)
    os.makedirs(path, exist_ok=True)
    def attribution(c, name):
        return f"{c} Template by https://github.com/ishaanbuildsthings\n{c} {URL}/{folder}/{name}\n"
    def comment(c):
        return "".join(f"{c} {x}\n" for x in about)
    py = attribution("#", "template.py") + header("#", ops, costs, memory, notes["py"]) + "\n" + comment("#") + py_body
    cpp = (attribution("//", "template.cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" +
           header("//", ops, costs, memory, notes["cpp"]) + "\n" + comment("//") + cpp_body)
    for name, text in (("template.py", py), ("template.cpp", cpp)):
        with open(os.path.join(path, name), "w") as f:
            f.write(text)


def check_cpp(op):  # (the range check in the catalog's standard form, so the bounds pass recognizes it)
    return (f'if (l < 0 || l > r || r >= n) throw out_of_range("{op}: needs 0 <= l <= r < n");\n'
            f'        if (step < 1) throw out_of_range("{op}: needs step >= 1");')


def check_py(op):
    return (f'if not 0 <= l <= r < self.n:\n            raise IndexError(f"{op}: needs 0 <= l <= r < n, got l = {{l}}, r = {{r}}, n = {{self.n}}")\n'
            f'        if step < 1:\n            raise IndexError(f"{op}: needs step >= 1, got step = {{step}}")')


def cpp_walk(f):
    if f == "sum":
        return "S res = 0;\n        for (int i = l; i <= last; i += step) res += A[i];"
    if f == "xor":
        return "T res = 0;\n        for (int i = l; i <= last; i += step) res ^= A[i];"
    return "T res = A[l];\n        for (int i = l + step; i <= last; i += step) res = " + CPP_OP[f].format(a="res", b="A[i]") + ";"


def imports(fams, extra=()):
    from_math = sorted({"gcd"} & set(fams) | {x for x in extra if x in ("log2", "sqrt")})
    ops = sorted(({"xor"} & set(fams)) | ({"and_"} if "and" in fams else set()) | ({"or_"} if "or" in fams else set()))
    out = ""
    if "accumulate" in extra:
        out += "from itertools import accumulate\n"
    if {"xor", "and", "or"} & set(fams):
        out += "from functools import reduce\n"
    if from_math:
        out += f"from math import {', '.join(from_math)}\n"
    if ops:
        out += f"from operator import {', '.join(ops)}\n"
    return out + "\n\n" if out else "\n"


# ------------------------------------------------------------------------------------------------ with updates

def updates_cpp(fams):
    blocks = [f for f in fams if f in BLOCK]
    trees = [f for f in fams if f not in BLOCK]
    s = "template <typename T>\nstruct StridedQueries {\n    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n"
    s += "    int n, blockStrides = 0, blockSize = 1, numBlocks = 0, treeStrides = 0;\n    vector<T> A;\n"
    s += "    vector<int> offsets;  // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list\n"
    for f in blocks:
        s += f"    vector<{'S' if f == 'sum' else 'T'}> {f}Blocks;\n"
    for f in trees:
        s += f"    vector<T> {f}Tree;\n"
    cutoff_param = ", int cutoff = -1" if trees else ""
    s += "\n"
    if trees:
        s += "    // O(build) -- arr: the initial array. cutoff: seg trees are kept for steps up to it (more memory and slower\n"
        s += "    // updates, faster big-step queries); leave it out for sqrt(n / log n)\n"
    else:
        s += "    // O(build) -- arr: the initial array\n"
    s += f"    explicit StridedQueries(const vector<T>& arr{cutoff_param}) {{\n        n = (int)arr.size();\n        A = arr;\n"
    if blocks:
        s += "        blockStrides = max(1, min(n, (int)sqrt((double)n)));\n        blockSize = blockStrides;\n        numBlocks = n / blockSize + 1;\n"
    if trees:
        s += "        treeStrides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt(n / max(1.0, log2(n + 1.0)))));\n"
        s += '        if (treeStrides < 0 || treeStrides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");\n'
    s += "        int strides = max(blockStrides, treeStrides);\n        offsets.assign((size_t)strides * (strides + 1) / 2, 0);\n"
    s += "        for (int step = 1; step <= strides; step++) {\n            int used = 0;\n            for (int residue = 0; residue < step; residue++) {\n"
    s += "                offsets[step * (step - 1) / 2 + residue] = used;\n                if (residue < n) used += (n - residue + step - 1) / step;\n            }\n        }\n"
    for f in blocks:
        s += f"        {f}Blocks.assign((size_t)blockStrides * numBlocks, 0);\n"
    if blocks:
        s += "        for (int step = 1; step <= blockStrides; step++) {\n            size_t base = (size_t)(step - 1) * numBlocks;\n            int index = 0;\n"
        s += "            for (int residue = 0; residue < step; residue++) {\n                for (int i = residue; i < n; i += step, index++) {\n"
        for f in blocks:
            s += f"                    {f}Blocks[base + index / blockSize] {'+' if f == 'sum' else '^'}= A[i];\n"
        s += "                }\n            }\n        }\n"
    for f in trees:
        s += f"        {f}Tree.assign((size_t)treeStrides * 2 * n, T(0));\n"
        s += f"        for (int step = 1; step <= treeStrides; step++) {{\n            T* tree = {f}Tree.data() + (size_t)(step - 1) * 2 * n;\n            int index = n;\n"
        s += "            for (int residue = 0; residue < step; residue++) {\n                for (int i = residue; i < n; i += step) tree[index++] = A[i];\n            }\n"
        s += "            for (int node = n - 1; node >= 1; node--) tree[node] = " + CPP_OP[f].format(a="tree[2 * node]", b="tree[2 * node + 1]") + ";\n        }\n"
    s += "    }\n\n"
    s += "    // O(n) -- the whole array\n    vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }\n\n"
    s += '    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range\n    T pointGet(int i) const {\n        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");\n        return A[i];\n    }\n\n'
    for op, doc, value in (("pointAssign", "a[i] = v (overwrite)", "v"), ("pointAdd", "a[i] += v", "T(A[i] + v)"),
                           ("pointChmax", "a[i] = max(a[i], v)", "max(A[i], v)"), ("pointChmin", "a[i] = min(a[i], v)", "min(A[i], v)")):
        s += f"    // {doc}; needs 0 <= i < n, else throws out_of_range\n    void {op}(int i, T v) {{\n"
        s += f'        if (i < 0 || i >= n) throw out_of_range("{op}: needs 0 <= i < n");\n        write(i, {value});\n    }}\n\n'
    for f in fams:
        op = OP[f]
        s += f"    // {WHAT[f]}, up to at most r; {RANGE_RULE}, else throws out_of_range\n"
        s += f"    {'S' if f == 'sum' else 'T'} {op}(int l, int r, int step) {{\n        {check_cpp(op)}\n        int last = l + (r - l) / step * step;\n"
        if f in BLOCK:
            eq = "+=" if f == "sum" else "^="
            s += f"""        if (step > blockStrides) {{
            {cpp_walk(f).replace(chr(10) + '        ', chr(10) + '            ')}
            return res;
        }}
        int first = listIndex(step, l), final = listIndex(step, last);
        int firstBlock = first / blockSize, lastBlock = final / blockSize;
        {'S' if f == 'sum' else 'T'} res = 0;
        if (firstBlock == lastBlock) {{
            for (int i = l; i <= last; i += step) res {eq} A[i];
            return res;
        }}
        const {'S' if f == 'sum' else 'T'}* blocks = {f}Blocks.data() + (size_t)(step - 1) * numBlocks;
        int leftCount = (firstBlock + 1) * blockSize - first, rightCount = final - lastBlock * blockSize + 1;
        for (int k = 0, i = l; k < leftCount; k++, i += step) res {eq} A[i];
        for (int block = firstBlock + 1; block < lastBlock; block++) res {eq} blocks[block];
        for (int k = 0, i = last; k < rightCount; k++, i -= step) res {eq} A[i];
        return res;
    }}

"""
        else:
            combine_l = CPP_OP[f].format(a="res", b="tree[low++]")
            combine_h = CPP_OP[f].format(a="res", b="tree[--high]")
            s += f"""        if (step > treeStrides) {{
            {cpp_walk(f).replace(chr(10) + '        ', chr(10) + '            ')}
            return res;
        }}
        const T* tree = {f}Tree.data() + (size_t)(step - 1) * 2 * n;
        int low = n + listIndex(step, l), high = n + listIndex(step, last) + 1;
        T res = A[l];  // (every aggregate here keeps a value it has already seen)
        while (low < high) {{
            if (low & 1) res = {combine_l};
            if (high & 1) res = {combine_h};
            low /= 2, high /= 2;
        }}
        return res;
    }}

"""
    s += "    // ---- internals ----\n\n"
    s += "    int listIndex(int step, int i) const { return offsets[step * (step - 1) / 2 + i % step] + i / step; }\n\n"
    s += "    void write(int i, T v) {\n"
    if "sum" in blocks:
        s += "        S sumDelta = S(v) - S(A[i]);\n"
    if "xor" in blocks:
        s += "        T xorDelta = A[i] ^ v;\n"
    s += "        A[i] = v;\n"
    if blocks:
        s += "        for (int step = 1; step <= blockStrides; step++) {\n            int block = listIndex(step, i) / blockSize;\n"
        for f in blocks:
            s += f"            {f}Blocks[(size_t)(step - 1) * numBlocks + block] {'+' if f == 'sum' else '^'}= {f}Delta;\n"
        s += "        }\n"
    if trees:
        s += "        for (int step = 1; step <= treeStrides; step++) {\n            int leaf = n + listIndex(step, i);\n"
        for f in trees:
            merged = CPP_OP[f].format(a="tree[2 * node]", b="tree[2 * node + 1]")
            s += f"""            {{
                T* tree = {f}Tree.data() + (size_t)(step - 1) * 2 * n;
                tree[leaf] = v;
                for (int node = leaf / 2; node >= 1; node /= 2) {{
                    T merged = {merged};
                    if (merged == tree[node]) break;  // (nothing above can change either)
                    tree[node] = merged;
                }}
            }}
"""
        s += "        }\n"
    s += "    }\n};\n"
    return s


def updates_py(fams):
    blocks = [f for f in fams if f in BLOCK]
    trees = [f for f in fams if f not in BLOCK]
    extra = {"sqrt"} | ({"log2"} if trees else set())
    s = imports(fams, extra)
    s += "class StridedQueries:\n"
    param = ", cutoff=None" if trees else ""
    if trees:
        s += "    # O(build) -- arr: the initial array. cutoff: seg trees are kept for steps up to it (more memory and slower\n"
        s += "    # updates, faster big-step queries); leave it out for a quarter of sqrt(n / log n)\n"
    else:
        s += "    # O(build) -- arr: the initial array\n"
    s += f"    def __init__(self, arr{param}):\n        self.A = A = list(arr)\n        self.n = n = len(A)\n"
    s += "        self.blockStrides = self.treeStrides = 0\n"
    if blocks:
        s += "        self.blockSize = blockSize = max(1, min(n, int(sqrt(n))))\n"
        s += "        self.blockStrides = max(1, min(n, int(sqrt(n)) // 8))  # (slices walk big steps fast; every stride kept slows updates)\n"
    if trees:
        s += "        self.treeStrides = cutoff if cutoff is not None else max(1, min(n, int(sqrt(n / max(1.0, log2(n + 1)))) // 4))\n"
        s += '        if not 0 <= self.treeStrides <= n:\n            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")\n'
    s += "        strides = max(self.blockStrides, self.treeStrides)\n"
    s += "        # offsets[step][residue]: where that residue class starts in that stride's list\n"
    s += "        self.offsets = [None] * (strides + 1)\n"
    s += "        lists = [None] * (strides + 1)\n"
    s += "        for step in range(1, strides + 1):\n            used, starts, parts = 0, [0] * step, []\n            for residue in range(step):\n"
    s += "                starts[residue] = used\n                parts.extend(A[residue::step])\n                if residue < n:\n                    used += (n - residue + step - 1) // step\n"
    s += "            self.offsets[step] = starts\n            lists[step] = parts\n"
    for f in blocks:
        fold = "sum({s})" if f == "sum" else "reduce(xor, {s})"
        s += f"        self.{f}Blocks = [None] + [[{fold.format(s='lists[step][k:k + blockSize]')} for k in range(0, n, blockSize)] + [0] for step in range(1, self.blockStrides + 1)]\n"
    if trees:
        s += "        self.trees = trees = {}\n"
    for f in trees:
        s += f"""        trees["{f}"] = [None] * (self.treeStrides + 1)
        for step in range(1, self.treeStrides + 1):
            tree = [0] * n + lists[step]
            high = n
            while high > 1:  # (level by level: map is much faster than a loop over the nodes)
                low = (high + 1) // 2
                tree[low:high] = list(map({PY_FN[f]}, tree[2 * low:2 * high:2], tree[2 * low + 1:2 * high:2]))
                high = low
            trees["{f}"][step] = tree
"""
    if trees:
        for f in trees:
            s += f'        self.{f}Tree = trees["{f}"]\n'
    s += "\n    # O(n) -- the whole array\n    def getAll(self):\n        return list(self.A)\n\n"
    s += '    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError\n    def pointGet(self, i):\n        if i < 0 or i >= self.n:\n            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")\n        return self.A[i]\n\n'
    for op, doc, value in (("pointAssign", "a[i] = v (overwrite)", "v"), ("pointAdd", "a[i] += v", "self.A[i] + v"),
                           ("pointChmax", "a[i] = max(a[i], v)", "max(self.A[i], v)"), ("pointChmin", "a[i] = min(a[i], v)", "min(self.A[i], v)")):
        s += f'    # {doc}; needs 0 <= i < n, else raises IndexError\n    def {op}(self, i, v):\n        if i < 0 or i >= self.n:\n            raise IndexError(f"{op}: needs 0 <= i < n, got i={{i}}, n={{self.n}}")\n        self._write(i, {value})\n\n'
    for f in fams:
        op = OP[f]
        walk = PY_WALK[f].format(s="self.A[l:last + 1:step]")
        s += f"    # {WHAT[f]}, up to at most r; {RANGE_RULE}, else raises IndexError\n    def {op}(self, l, r, step):\n        {check_py(op)}\n        last = l + (r - l) // step * step\n"
        if f in BLOCK:
            piece = "sum({})" if f == "sum" else "reduce(xor, {}, 0)"
            join = "+" if f == "sum" else "^"
            s += f"""        if step > self.blockStrides:
            return {walk}
        blockSize, A = self.blockSize, self.A
        starts = self.offsets[step]
        first = starts[l % step] + l // step
        final = starts[last % step] + last // step
        firstBlock, lastBlock = first // blockSize, final // blockSize
        if firstBlock == lastBlock:
            return {walk}
        leftEnd = l + ((firstBlock + 1) * blockSize - first) * step
        rightStart = last - (final - lastBlock * blockSize) * step
        middle = self.{f}Blocks[step][firstBlock + 1:lastBlock]
        return {piece.format('A[l:leftEnd:step]')} {join} {piece.format('middle')} {join} {piece.format('A[rightStart:last + 1:step]')}

"""
        else:
            s += f"""        if step > self.treeStrides:
            return {walk}
        starts, tree = self.offsets[step], self.{f}Tree[step]
        n = self.n
        low = n + starts[l % step] + l // step
        high = n + starts[last % step] + last // step + 1
        res = self.A[l]  # (every aggregate here keeps a value it has already seen)
        while low < high:
            if low & 1:
                v = tree[low]
                res = {PY_INLINE[f].format(a='res', b='v')}
                low += 1
            if high & 1:
                high -= 1
                v = tree[high]
                res = {PY_INLINE[f].format(a='res', b='v')}
            low >>= 1
            high >>= 1
        return res

"""
    s += "    # ---- internals ----\n\n    def _write(self, i, v):\n"
    s += "        A, n, offsets = self.A, self.n, self.offsets\n"
    if "sum" in blocks:
        s += "        sumDelta = v - A[i]\n"
    if "xor" in blocks:
        s += "        xorDelta = A[i] ^ v\n"
    s += "        A[i] = v\n"
    if blocks:
        s += "        blockSize = self.blockSize\n        for step in range(1, self.blockStrides + 1):\n            block = (offsets[step][i % step] + i // step) // blockSize\n"
        for f in blocks:
            s += f"            self.{f}Blocks[step][block] {'+' if f == 'sum' else '^'}= {f}Delta\n"
    if trees:
        s += "        for step in range(1, self.treeStrides + 1):\n            leaf = n + offsets[step][i % step] + i // step\n"
        for f in trees:
            s += f"""            tree = self.{f}Tree[step]
            tree[leaf] = v
            node = leaf >> 1
            while node:
                a, b = tree[2 * node], tree[2 * node + 1]
                merged = {PY_INLINE[f].format(a='a', b='b')}
                if merged == tree[node]:
                    break  # (nothing above can change either)
                tree[node] = merged
                node >>= 1
"""
    return s.rstrip() + "\n"


def updates(fams):
    blocks = [f for f in fams if f in BLOCK]
    trees = [f for f in fams if f not in BLOCK]
    folder = "sqrt-strided-updates-" + "-".join(fams)
    ops = POINT + ["getAll"] + [OP[f] for f in fams]
    costs = {"pointGet": "1", "getAll": "N"}
    for f in fams:
        costs[OP[f]] = "sqrt(N)" if f in BLOCK else "sqrt(NlogN)+log(U) ?" if f == "gcd" else "sqrt(NlogN)"
    terms, build = [], []
    if blocks:
        terms.append(f"{len(blocks)}*sqrt(N)")
        build.append(f"{len(blocks)}*N*sqrt(N)")
    if trees:
        terms.append(f"{len(trees)}*sqrt(NlogN)")
        build.append(f"{2 * len(trees)}*N*sqrt(N/logN)")
    if "gcd" in trees:
        terms.append("sqrt(N/logN)*log(U)")
        build.append("N*sqrt(N/logN)*log(U)")
    update = "+".join(terms) + (" ?" if "gcd" in trees else "")
    for op in POINT[:-1]:
        costs[op] = update
    costs["build"] = "+".join(build) + (" ?" if "gcd" in trees else "")
    node = [f"{f}Blocks[1*N]" for f in blocks] + [f"{f}Tree[2*N*sqrt(N/logN)]" for f in trees]
    memory = {"node": " ".join(node), "tags": "none", "other": "A[1*N] offsets[1*N]"}
    shared = "one list per stride, in which a strided query is a contiguous range"
    py_note = f"{shared}. Kept strides are lower than the costs suggest (an eighth for block sums, a quarter for seg trees), since slices walk the big steps fast"
    cpp_note = f"{shared}. Steps above the cutoff walk their positions"
    about = ["Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r",
             "(the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query",
             "is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few",
             "positions, so it walks them. All indices 0-based, ranges inclusive.",
             "T: int, long long, ...; sums are kept in S (long long for small T)."]
    write(folder, updates_py(fams), updates_cpp(fams), ops, costs, memory, {"py": py_note, "cpp": cpp_note}, about)


# ------------------------------------------------------------------------------------------------ static, one cached table

def static_cpp(fams):
    s = "template <typename T>\nstruct StridedQueries {\n    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n    int n, levels = 1;\n    vector<T> A;\n"
    for f in fams:
        if f in BLOCK:
            s += f"    vector<{'S' if f == 'sum' else 'T'}> {f}Pre;\n    int {f}Step = 0;  // the step {f}Pre was built for\n"
        else:
            s += f"    vector<T> {f}Table;\n    int {f}Step = 0;  // the step {f}Table was built for\n"
    s += "\n    // O(build) -- arr: the initial array\n    explicit StridedQueries(const vector<T>& arr) {\n        n = (int)arr.size();\n        A = arr;\n        while ((1 << levels) <= n) levels++;\n"
    for f in fams:
        if f in BLOCK:
            s += f"        {f}Pre.assign(n, 0);\n"
        else:
            s += f"        {f}Table.assign((size_t)levels * n, T(0));\n        copy(A.begin(), A.end(), {f}Table.begin());\n"
    s += "    }\n\n"
    for f in fams:
        op, typ = OP[f], "S" if f == "sum" else "T"
        s += f"    // {WHAT[f]}, up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by\n"
        s += f"    // step; {RANGE_RULE}, else throws out_of_range\n"
        s += f"    {typ} {op}(int l, int r, int step) {{\n        {check_cpp(op)}\n        int last = l + (r - l) / step * step, count = (r - l) / step + 1;\n"
        s += f"        if (step != {f}Step && (count <= {WALK['cpp']} || (long long)step * step > n)) {{\n            {cpp_walk(f).replace(chr(10) + '        ', chr(10) + '            ')}\n            return res;\n        }}\n"
        s += f"        if (step != {f}Step) rebuild{f.capitalize()}(step);\n"
        if f in BLOCK:
            sub = "-" if f == "sum" else "^"
            s += f"        return {f}Pre[last] {sub} (l >= step ? {f}Pre[l - step] : {typ}(0));\n    }}\n\n"
        else:
            s += "        int level = 31 - __builtin_clz(count);\n        size_t base = (size_t)level * n;\n"
            s += f"        return {CPP_OP[f].format(a=f'{f}Table[base + l]', b=f'{f}Table[base + last - ((1 << level) - 1) * step]')};\n    }}\n\n"
    s += "    // ---- internals ----\n\n"
    for f in fams:
        typ = "S" if f == "sum" else "T"
        s += f"    void rebuild{f.capitalize()}(int step) {{\n        {f}Step = step;\n"
        if f in BLOCK:
            s += f"        for (int i = 0; i < n; i++) {f}Pre[i] = (i >= step ? {f}Pre[i - step] : {typ}(0)) {'+' if f == 'sum' else '^'} A[i];\n    }}\n\n"
        else:
            merged = CPP_OP[f].format(a="previous[i]", b="previous[i + jump]")
            s += f"""        for (int level = 1; level < levels; level++) {{
            long long jump = (long long)step << (level - 1);
            if (jump >= n) break;
            const T* previous = {f}Table.data() + (size_t)(level - 1) * n;
            T* current = {f}Table.data() + (size_t)level * n;
            for (int i = 0; i < n; i++) current[i] = i + jump < n ? {merged} : previous[i];
        }}
    }}

"""
    return s.rstrip() + "\n};\n"


def static_py(fams):
    extra = {"accumulate"} if BLOCK & set(fams) else set()
    s = imports(fams, extra)
    s += "class StridedQueries:\n    # O(build) -- arr: the initial array\n    def __init__(self, arr):\n        self.A = list(arr)\n        self.n = len(self.A)\n"
    for f in fams:
        s += f"        self.{f}Step = 0  # the step the {f} {'prefixes were' if f in BLOCK else 'table was'} built for\n"
        s += f"        self.{f}Pre = None\n" if f in BLOCK else f"        self.{f}Table = None\n"
    s += "\n"
    for f in fams:
        op = OP[f]
        walk = PY_WALK[f].format(s="self.A[l:last + 1:step]")
        s += f"    # {WHAT[f]}, up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by\n    # step; {RANGE_RULE}, else raises IndexError\n"
        s += f"    def {op}(self, l, r, step):\n        {check_py(op)}\n        last = l + (r - l) // step * step\n        count = (r - l) // step + 1\n"
        s += f"        if step != self.{f}Step:\n            if count <= {WALK['py']} or step * step > self.n:\n                return {walk}\n"
        if f in BLOCK:
            func = "" if f == "sum" else ", xor"
            s += f"""            self.{f}Step = step
            self.{f}Pre = pre = list(self.A)
            for residue in range(min(step, self.n)):
                pre[residue::step] = list(accumulate(pre[residue::step]{func}))
"""
            sub = "-" if f == "sum" else "^"
            s += f"        pre = self.{f}Pre\n        return pre[last] {sub} pre[l - step] if l >= step else pre[last]\n\n"
        else:
            s += f"""            self.{f}Step = step
            self.{f}Table = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map({PY_FN[f]}, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.{f}Table[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return {PY_INLINE[f].format(a='a', b='b')}

"""
    return s.rstrip() + "\n"


def static(fams):
    folder = "sqrt-strided-static-" + "-".join(fams)
    ops = [OP[f] for f in fams]
    costs = {"build": "N"}
    for f in fams:
        costs[OP[f]] = "N" if f in BLOCK else "N*log(N)+N*log(U) ?" if f == "gcd" else "N*log(N)"
    node = [f"{f}Pre[1*N]" if f in BLOCK else f"{f}Table[1*N*log(N)]" for f in fams]
    memory = {"node": " ".join(node), "tags": "none", "other": "A[1*N]"}
    note = ("the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and "
            "a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step")
    about = ["Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r",
             "(the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the",
             "step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices",
             "0-based, ranges inclusive."]
    write(folder, static_py(fams), static_cpp(fams), ops, costs, memory, {"py": note, "cpp": note}, about)


# ------------------------------------------------------------------------------------------------ static, every prefix array

def prefix_cpp(fams):
    s = "template <typename T>\nstruct StridedQueries {\n    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n    int n, strides;\n    vector<T> A;\n"
    for f in fams:
        s += f"    vector<{'S' if f == 'sum' else 'T'}> {f}Pre;\n"
    s += """
    // O(build) -- arr: the initial array. cutoff: prefix arrays are kept for steps up to it; leave it out for sqrt(n), and
    // lower it when memory is tight (each kept step costs n values)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A = arr;
        strides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt((double)n)));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
"""
    for f in fams:
        typ = "S" if f == "sum" else "T"
        s += f"        {f}Pre.assign((size_t)strides * n, 0);\n        for (int step = 1; step <= strides; step++) {{\n            {typ}* pre = {f}Pre.data() + (size_t)(step - 1) * n;\n"
        s += f"            for (int i = 0; i < n; i++) pre[i] = (i >= step ? pre[i - step] : {typ}(0)) {'+' if f == 'sum' else '^'} A[i];\n        }}\n"
    s += "    }\n\n"
    for f in fams:
        op, typ = OP[f], "S" if f == "sum" else "T"
        s += f"    // {WHAT[f]}, up to at most r. O(1) for a kept step; {RANGE_RULE}, else throws out_of_range\n"
        s += f"    {typ} {op}(int l, int r, int step) {{\n        {check_cpp(op)}\n        int last = l + (r - l) / step * step;\n"
        s += f"        if (step > strides) {{\n            {cpp_walk(f).replace(chr(10) + '        ', chr(10) + '            ')}\n            return res;\n        }}\n"
        s += f"        const {typ}* pre = {f}Pre.data() + (size_t)(step - 1) * n;\n        return pre[last] {'-' if f == 'sum' else '^'} (l >= step ? pre[l - step] : {typ}(0));\n    }}\n\n"
    return s.rstrip() + "\n};\n"


def prefix_py(fams):
    s = imports(fams, {"accumulate", "sqrt"})
    s += """class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: prefix arrays are kept for steps up to it; leave it out for sqrt(n), and
    # lower it when memory is tight (each kept step costs n values)
    def __init__(self, arr, cutoff=None):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.strides = cutoff if cutoff is not None else max(1, min(n, int(sqrt(n))))
        if not 0 <= self.strides <= n:
            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")
"""
    for f in fams:
        func = "" if f == "sum" else ", xor"
        s += f"""        self.{f}Pre = [None] * (self.strides + 1)
        for step in range(1, self.strides + 1):
            pre = list(A)
            for residue in range(step):
                pre[residue::step] = list(accumulate(pre[residue::step]{func}))
            self.{f}Pre[step] = pre
"""
    s += "\n"
    for f in fams:
        op = OP[f]
        s += f"    # {WHAT[f]}, up to at most r. O(1) for a kept step; {RANGE_RULE}, else raises IndexError\n"
        s += f"    def {op}(self, l, r, step):\n        {check_py(op)}\n        last = l + (r - l) // step * step\n"
        s += f"        if step > self.strides:\n            return {PY_WALK[f].format(s='self.A[l:last + 1:step]')}\n"
        s += f"        pre = self.{f}Pre[step]\n        return pre[last] {'-' if f == 'sum' else '^'} pre[l - step] if l >= step else pre[last]\n\n"
    return s.rstrip() + "\n"


def prefix(fams):
    folder = "sqrt-strided-prefix-" + "-".join(fams)
    ops = [OP[f] for f in fams]
    costs = {OP[f]: "sqrt(N)" for f in fams}
    costs["build"] = f"{len(fams)}*N*sqrt(N)"
    memory = {"node": " ".join(f"{f}Pre[1*N*sqrt(N)]" for f in fams), "tags": "none", "other": "A[1*N]"}
    note = ("O(1) for a step up to the cutoff, sqrt(N) only for a bigger one. The default cutoff is about 90 million values at "
            "N = 2e5, so pass a lower one when memory is tight")
    about = ["Static strided queries, every small stride's prefix array built up front: each query covers a[l], a[l + step],",
             "a[l + 2 * step], ... up to at most r (the last position used may be below r). All indices 0-based, ranges inclusive."]
    write(folder, prefix_py(fams), prefix_cpp(fams), ops, costs, memory, {"py": note, "cpp": note}, about)


# ------------------------------------------------------------------------------------------------ strided add

ADD_CPP = """template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, strides;
    vector<S> A;
    vector<int> offsets;  // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list
    vector<S> diffs;  // one Fenwick tree of differences per kept step, n + 2 slots each

    // O(build) -- arr: the initial array. cutoff: a Fenwick tree is kept for steps up to it (more memory and slower
    // reads, faster big-step adds); leave it out for sqrt(n / log n)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A.assign(arr.begin(), arr.end());
        strides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt(n / max(1.0, log2(n + 1.0)))));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
        offsets.assign((size_t)strides * (strides + 1) / 2, 0);
        for (int step = 1; step <= strides; step++) {
            int used = 0;
            for (int residue = 0; residue < step; residue++) {
                offsets[step * (step - 1) / 2 + residue] = used;
                if (residue < n) used += (n - residue + step - 1) / step;
            }
        }
        diffs.assign((size_t)strides * (n + 2), 0);
    }

    // a[l] += v, a[l + step] += v, ... up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    void stridedAdd(int l, int r, int step, T v) {
        CHECK
        int last = l + (r - l) / step * step;
        if (step > strides) {
            for (int i = l; i <= last; i += step) A[i] += v;
            return;
        }
        addDiff(step, listIndex(step, l), S(v));
        addDiff(step, listIndex(step, last) + 1, -S(v));
    }

    // the current a[i]; needs 0 <= i < n, else throws out_of_range
    S pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        S res = A[i];
        for (int step = 1; step <= strides; step++) {
            const S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
            for (int node = listIndex(step, i) + 1; node > 0; node -= node & -node) res += tree[node];
        }
        return res;
    }

    // a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        A[i] += v;
    }

    // a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        A[i] += S(v) - pointGet(i);
    }

    // a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) > current) A[i] += S(v) - current;
    }

    // a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        S current = pointGet(i);
        if (S(v) < current) A[i] += S(v) - current;
    }

    // the whole array
    vector<S> getAll() const {
        vector<S> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // ---- internals ----

    int listIndex(int step, int i) const { return offsets[step * (step - 1) / 2 + i % step] + i / step; }

    void addDiff(int step, int index, S v) {
        S* tree = diffs.data() + (size_t)(step - 1) * (n + 2);
        for (int node = index + 1; node <= n + 1; node += node & -node) tree[node] += v;
    }
};
"""

ADD_PY = """from math import log2, sqrt


class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: a Fenwick tree is kept for steps up to it (more memory and slower
    # reads, faster big-step adds); leave it out for a quarter of sqrt(n / log n)
    def __init__(self, arr, cutoff=None):
        self.A = list(arr)
        self.n = n = len(self.A)
        self.strides = cutoff if cutoff is not None else max(1, min(n, int(sqrt(n / max(1.0, log2(n + 1)))) // 4))
        if not 0 <= self.strides <= n:
            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")
        # offsets[step][residue]: where that residue class starts in that stride's list
        self.offsets = [None] * (self.strides + 1)
        for step in range(1, self.strides + 1):
            used, starts = 0, [0] * step
            for residue in range(step):
                starts[residue] = used
                if residue < n:
                    used += (n - residue + step - 1) // step
            self.offsets[step] = starts
        self.diffs = [None] + [[0] * (n + 2) for _ in range(self.strides)]  # one Fenwick tree of differences per kept step

    # a[l] += v, a[l + step] += v, ... up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedAdd(self, l, r, step, v):
        CHECK
        last = l + (r - l) // step * step
        if step > self.strides:
            A = self.A
            for i in range(l, last + 1, step):
                A[i] += v
            return
        starts = self.offsets[step]
        self._addDiff(step, starts[l % step] + l // step, v)
        self._addDiff(step, starts[last % step] + last // step + 1, -v)

    # the current a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        res = self.A[i]
        offsets, diffs = self.offsets, self.diffs
        for step in range(1, self.strides + 1):
            tree = diffs[step]
            node = offsets[step][i % step] + i // step + 1
            while node:
                res += tree[node]
                node &= node - 1
        return res

    # a[i] += v; needs 0 <= i < n, else raises IndexError
    def pointAdd(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i={i}, n={self.n}")
        self.A[i] += v

    # a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError
    def pointAssign(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={self.n}")
        self.A[i] += v - self.pointGet(i)

    # a[i] = max(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmax(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i={i}, n={self.n}")
        current = self.pointGet(i)
        if v > current:
            self.A[i] += v - current

    # a[i] = min(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmin(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i={i}, n={self.n}")
        current = self.pointGet(i)
        if v < current:
            self.A[i] += v - current

    # the whole array
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]

    # ---- internals ----

    def _addDiff(self, step, index, v):
        tree = self.diffs[step]
        node = index + 1
        limit = self.n + 1
        while node <= limit:
            tree[node] += v
            node += node & -node
"""


def add():
    ops = POINT + ["getAll", "stridedAdd"]
    costs = {"stridedAdd": "sqrt(NlogN)", "pointGet": "sqrt(NlogN)", "pointAdd": "1", "pointAssign": "sqrt(NlogN)",
             "pointChmax": "sqrt(NlogN)", "pointChmin": "sqrt(NlogN)", "getAll": "N*sqrt(NlogN)", "build": "N*sqrt(N/logN)"}
    memory = {"node": "diffs[1*N*sqrt(N/logN)]", "tags": "none", "other": "A[1*N] offsets[1*N]"}
    note = "a small step is a range add on that step's Fenwick tree of differences, a big step walks its positions, and a point read adds up every small step"
    about = ["Strided add with point reads and writes: stridedAdd(l, r, step, v) adds v to a[l], a[l + step], ... up to at most r",
             "(the last position used may be below r). A strided sum on top of this has no good bound: two different steps",
             "overlap in a pattern that depends on both. All indices 0-based, ranges inclusive."]
    write("sqrt-strided-add", ADD_PY.replace("CHECK", check_py("stridedAdd")), ADD_CPP.replace("CHECK", check_cpp("stridedAdd")),
          ops, costs, memory, {"py": note, "cpp": note}, about)


def main():
    count = 0
    for k in range(1, len(FAMS) + 1):
        for fams in itertools.combinations(FAMS, k):
            updates(list(fams))
            static(list(fams))
            count += 2
    for fams in (["sum"], ["xor"], ["sum", "xor"]):
        prefix(fams)
        count += 1
    add()
    print(f"{count + 1} strided templates in {DIR}")


if __name__ == "__main__":
    sys.exit(main())
