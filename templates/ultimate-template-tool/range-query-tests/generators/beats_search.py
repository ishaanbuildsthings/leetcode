"""Give every beats tree that keeps a node max / min the leftmost / rightmost Gt / Gte / Lt / Lte searches it prunes.

    python3 beats_search.py      (after gen_beats.py / gen_bitbeats.py / gen_shrink_nosum.py, before sparse_beats.py)

A node's mx (mn) is current once its ancestors are pushed, so "the first i in [l, r] with a[i] >= x" is the usual
pruned walk: skip a node outside [l, r] or whose max fails, stop at a leaf, else push and try the left child first.
It costs nothing until called (no arrays). Each search is its own blank-line block, as are the two walks, so
drop_searches() can take them back out for the sparse versions (which keep the dense ops minus these). Adds the ops
to both headers and renames the folder to the new op list (replacing a stale folder of that name). Idempotent.
"""
import os
import re
import shutil

from note_lang import folder_name, write_template, strip_attribution

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SEARCH = {f"{side}{cmp}X": (side, cmp) for side in ("leftmost", "rightmost") for cmp in ("Gt", "Gte", "Lt", "Lte")}
CMP = {"Gt": ">", "Gte": ">=", "Lt": "<", "Lte": "<="}


def drop_searches(text):
    """text without the searches this adds (header lines and their blocks), for a sparse version made from it"""
    names = "|".join(SEARCH)
    text = strip_attribution(text)  # (the file's link names the folder, which names the searches)
    text = re.sub(rf"^((?:#|//) @operations:.*)$", lambda m: re.sub(rf" ({names})\b", "", m.group(1)), text, flags=re.M)
    text = re.sub(rf"^(?:#|//)   (?:{names}): .*\n", "", text, flags=re.M)
    out = []
    for b in text.split("\n\n"):
        if not re.search(rf"\b({names}|_?firstPass|_?lastPass)\b", b):
            out.append(b)
        elif "\n};" in "\n" + b:  # (the struct's closing brace right after the last walk stays)
            out[-1] += "\n" + "\n".join(ln for ln in b.split("\n") if ln == "};")
    return "\n\n".join(out)


def fields(text):
    node = re.search(r"^#   node: (.*)$", text, re.M).group(1)
    return {m for m in re.findall(r"(\w+)\[", node)}


def searches_for(fl):
    return [op for op, (_, c) in SEARCH.items() if ("mx" if c.startswith("G") else "mn") in fl]


def py_block(ops, has_push):
    out = []
    for op in ops:
        side, cmp = SEARCH[op]
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        walk = "_firstPass" if side == "leftmost" else "_lastPass"
        out.append(f'''    # O(logN) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        F = self.{f}
        return self.{walk}(1, 0, self.n - 1, l, r, lambda i: F[i] {o} x) if l <= r and self.n else -1
''')
    push = "        self._push(i, tl, tr)\n" if has_push else ""
    for walk, a, b in (("_firstPass", "2 * i", "2 * i + 1"), ("_lastPass", "2 * i + 1", "2 * i")):
        if not any((SEARCH[op][0] == "leftmost") == (walk == "_firstPass") for op in ops):
            continue
        first = walk == "_firstPass"
        ra, rb = ("tl, tm", "tm + 1, tr") if first else ("tm + 1, tr", "tl, tm")
        out.append(f'''    # the {"first" if first else "last"} index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def {walk}(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
{push}        tm = (tl + tr) // 2
        res = self.{walk}({a}, {ra}, l, r, ok)
        return res if res != -1 else self.{walk}({b}, {rb}, l, r, ok)
''')
    return out


def cpp_block(ops, has_push, node):
    out = []
    for op in ops:
        side, cmp = SEARCH[op]
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        walk = "firstPass" if side == "leftmost" else "lastPass"
        out.append(f'''    // O(logN) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    int {op}(int l, int r, T x) {{
        return l > r || !n ? -1 : {walk}(1, 0, n - 1, l, r, [&](int i) {{ return {"t[i]." + f if node else f + "[i]"} {o} x; }});
    }}
''')
    push = "        push(i, tl, tr);\n" if has_push else ""
    for walk, a, b in (("firstPass", "2 * i", "2 * i + 1"), ("lastPass", "2 * i + 1", "2 * i")):
        if not any((SEARCH[op][0] == "leftmost") == (walk == "firstPass") for op in ops):
            continue
        first = walk == "firstPass"
        ra, rb = ("tl, tm", "tm + 1, tr") if first else ("tm + 1, tr", "tl, tm")
        out.append(f'''    // the {"first" if first else "last"} index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    int {walk}(int i, int tl, int tr, int l, int r, const F& ok) {{
        if (r < tl || tr < l || !ok(i)) return -1;
        if (tl == tr) return tl;
{push}        int tm = (tl + tr) / 2, res = {walk}({a}, {ra}, l, r, ok);
        return res != -1 ? res : {walk}({b}, {rb}, l, r, ok);
    }}
''')
    return out


def py_sparse_block(ops):
    """the same searches for sparse_beats.py's trees: node 1 over [lo, hi], children L / R made by _kids, and lo - 1 when
    nothing qualifies (any index can be negative there, so the walks say "none" with None)"""
    out = []
    for op in ops:
        side, cmp = SEARCH[op]
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        walk = "_firstPass" if side == "leftmost" else "_lastPass"
        out.append(f'''    # O(logU) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or lo - 1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        F = self.{f}
        res = self.{walk}(1, self.lo, self.hi, l, r, lambda i: F[i] {o} x) if l <= r else None
        return self.lo - 1 if res is None else res
''')
    for walk, a, b in (("_firstPass", "self.L[i]", "self.R[i]"), ("_lastPass", "self.R[i]", "self.L[i]")):
        if not any((SEARCH[op][0] == "leftmost") == (walk == "_firstPass") for op in ops):
            continue
        first = walk == "_firstPass"
        ra, rb = ("tl, tm", "tm + 1, tr") if first else ("tm + 1, tr", "tl, tm")
        out.append(f'''    # the {"first" if first else "last"} index in [l, r] under node i whose value passes ok(node), or None: O(logU), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def {walk}(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return None
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        res = self.{walk}({a}, {ra}, l, r, ok)
        return res if res is not None else self.{walk}({b}, {rb}, l, r, ok)
''')
    return out


def cpp_sparse_block(ops, node):
    out = []
    for op in ops:
        side, cmp = SEARCH[op]
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        walk = "firstPass" if side == "leftmost" else "lastPass"
        out.append(f'''    // O(logU) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or lo - 1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    long long {op}(long long l, long long r, T x) {{
        long long res = l > r ? NONE : {walk}(root, lo, hi, l, r, [&](int i) {{ return {"t[i]." + f if node else f + "[i]"} {o} x; }});
        return res == NONE ? lo - 1 : res;
    }}
''')
    out.append("    static constexpr long long NONE = LLONG_MIN;  // (\"no index\": any long long can be an index here)\n")
    for walk, a, b in (("firstPass", "Lc[i]", "Rc[i]"), ("lastPass", "Rc[i]", "Lc[i]")):
        if not any((SEARCH[op][0] == "leftmost") == (walk == "firstPass") for op in ops):
            continue
        first = walk == "firstPass"
        ra, rb = ("tl, tm", "tm + 1, tr") if first else ("tm + 1, tr", "tl, tm")
        out.append(f'''    // the {"first" if first else "last"} index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long {walk}(int i, long long tl, long long tr, long long l, long long r, const F& ok) {{
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = {walk}({a}, {ra}, l, r, ok);
        return res != NONE ? res : {walk}({b}, {rb}, l, r, ok);
    }}
''')
    return out


def add_ops(text, ops, cm, cost="log(N)"):
    m = re.search(rf"^{re.escape(cm)} @operations: (.*)$", text, re.M)
    allops = sorted(set(m.group(1).split()) | set(ops))
    text = text[:m.start()] + f"{cm} @operations: {' '.join(allops)}" + text[m.end():]
    a = text.index(f"{cm} @complexities:\n") + len(f"{cm} @complexities:\n")
    b = text.index(f"{cm}   build:", a)
    lines = [ln for ln in text[a:b].split("\n") if ln] + [f"{cm}   {op}: {cost}" for op in ops]
    lines.sort(key=lambda ln: ln.split(":")[0].split()[-1])
    return text[:a] + "\n".join(lines) + "\n" + text[b:], allops


def inject(folder):
    py_path, cpp_path = os.path.join(DIR, folder, "template.py"), os.path.join(DIR, folder, "template.cpp")
    py = strip_attribution(open(py_path).read())
    cpp = strip_attribution(open(cpp_path).read())
    have = re.search(r"^# @operations: (.*)$", py, re.M).group(1).split()
    ops = [op for op in searches_for(fields(py)) if op not in have]
    if not ops:
        return folder
    has_push = "def _push(self, i, tl, tr)" in py
    assert ("void push(int i, int tl, int tr)" in cpp) == has_push, folder
    py, allops = add_ops(py, ops, "#")
    py = py.rstrip("\n") + "\n\n" + "\n".join(py_block(ops, has_push))
    cpp, _ = add_ops(cpp, ops, "//")
    end = cpp.rindex("};")
    cpp = cpp[:end].rstrip("\n") + "\n\n" + "\n".join(cpp_block(ops, has_push, "vector<Node> t;" in cpp)) + cpp[end:]
    new = folder_name(allops)
    if new != folder:
        target = os.path.join(DIR, new)
        if os.path.exists(target):
            shutil.rmtree(target)
        os.rename(os.path.join(DIR, folder), target)
    write_template(os.path.join(DIR, new, "template.py"), py)
    write_template(os.path.join(DIR, new, "template.cpp"), cpp)
    return new


def main():
    done = 0
    for folder in sorted(os.listdir(DIR)):
        path = os.path.join(DIR, folder, "template.py")
        if not os.path.exists(path):
            continue
        text = open(path).read()
        if "@data-structure-type: beats" not in text or not searches_for(fields(text)):
            continue
        new = inject(folder)
        if new != folder:
            done += 1
            print(folder, "->", new)
    print("added searches to", done, "beats trees")


if __name__ == "__main__":
    main()
