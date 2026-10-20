"""Sparse (dynamic) versions of the segment tree beats templates: sparse.py + sparse.cpp per folder.

    python3 sparse_beats.py

A beats tree's logic is kept exactly; only where nodes live changes. Every position of [lo, hi] starts at 0, and
the root is one block of zeros. Children are created on demand, as blocks of zeros of the right length (a block of
k zeros: max = min = 0, no second max / min, every count = k, sum 0, no tags), right before anything descends past
a node or pushes its tags. Queries push like the dense trees do, so they may create nodes too.
  Python: the dense class's per-field lists grow by one entry per node; L / R hold the children, ln the lengths.
  C++:    the same, with every per-node array static and shared by all trees of the type (resetPool() between
          test cases).
The heap arithmetic (2 * i, 2 * i + 1) becomes L[i] / R[i]; indices, lengths and counts become 64-bit.
"""
import os

from note_lang import strip_attribution, write_template
import re

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
HEADER_LINE = re.compile(r"^(#|//) (@|  )")


def split_header(text):
    lines = strip_attribution(text).split("\n")
    k = 0
    while k < len(lines) and HEADER_LINE.match(lines[k]):
        k += 1
    return lines[:k], "\n".join(lines[k:])


def sparse_header(header_lines, cm):
    """The dense header with N -> U costs (U = index-range size) and per-update memory."""
    out = []
    block = None
    for line in header_lines:
        m = re.match(rf"^{re.escape(cm)} @(\w[\w-]*):\s*(.*)$", line)
        if m:
            block = m.group(1)
            if block == "original-file-url":
                continue
            out.append(line)
            continue
        key, _, val = line[len(cm):].strip().partition(": ")
        if block == "complexities":
            val = "1" if key == "build" else val.replace("log^2(N)", "log(U)*log(U)").replace("log(N)", "log(U)")
            out.append(f"{cm}   {key}: {val}")
        elif block == "memory":
            if key == "layout":
                val = "sparse"
            elif key in ("node", "tags", "other") and val != "none":
                val = re.sub(r"\[\d+\*N\]", "[4*log(U)]", val)
            elif key == "note":
                val = ("per update, the nodes it visits (and their siblings, created as blocks of zeros); beats "
                       "recursion is amortized, so count nodes by work done. C++: one shared node pool, call "
                       "resetPool() between test cases; Python: per-node lists that grow")
            out.append(f"{cm}   {key}: {val}")
        else:
            out.append(line)
    return out


def sparse_costs(code, cm):
    """In comments, costs that counted tree levels over N elements now count them over the index range: N -> U."""
    def fix(line):
        k = line.find(cm)
        if k < 0:
            return line
        c = line[k:]
        c = c.replace("log^2 N", "log^2 U").replace("log^2(N)", "log^2(U)").replace("log² N", "log² U")
        c = re.sub(r"\blog ?N\b", lambda m: m.group(0).replace("N", "U"), c)
        c = re.sub(r"\blog n\b", "log U", c)
        return line[:k] + c
    return "\n".join(fix(line) for line in code.split("\n"))


# ================================================================================================ Python

def convert_py(src, name):
    """The dense beats class -> a sparse one over [lo, hi]."""
    m = re.search(r"^class (\w+)", src, re.M)
    old_name = m.group(1)
    pre, cls = src[:m.start()], src[m.start():]
    cls = cls.replace(f"class {old_name}", f"class {name}", 1)

    # fields from the dense __init__: self.f = [default] * size
    fields = re.findall(r"^\s+self\.(\w+) = \[(.+?)\] \* size", cls, re.M)
    init_m = re.search(r"^    def __init__\(self, arr(.*?)\):\n(.*?)(?=^    (def |#|@))", cls, re.M | re.S)
    extra_args = init_m.group(1)
    init_body = init_m.group(2)
    keep = [ln for ln in init_body.split("\n") if re.match(r"\s+self\.FULL", ln)]
    counts = [f for f, _ in fields if f.startswith("cnt") or f == "sz"]

    node_defaults = [(f, re.sub(r"(?<!self\.)\bFULL\b", "self.FULL", d)) for f, d in fields]
    zero_sets = "".join(f"\n        self.{f}[i] = k" for f in counts) + (
        "\n        self.andAll[i] = 0" if any(f == "andAll" for f, _ in fields) else "")
    new_init = f'''    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi{extra_args}):
        self.lo, self.hi = lo, hi
{chr(10).join(keep) + chr(10) if keep else ""}        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
{"".join(f"        self.{f} = [{d}] * 2{chr(10)}" for f, d in fields)}        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k{zero_sets}

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
{"".join(f"        self.{f}.append({d}){chr(10)}" for f, d in node_defaults)}        self._zero(j, k)
        return j

    # create node i's children (blocks of zeros: the left one gets the extra slot) if it has none yet
    def _kids(self, i):
        if not self.L[i] and self.ln[i] > 1:
            k = self.ln[i]
            self.L[i] = self._node((k + 1) // 2)
            self.R[i] = self._node(k // 2)

'''
    cls = cls[:init_m.start()] + new_init + cls[init_m.end():]
    # drop the build
    cls = re.sub(r"^    def _build\(.*?(?=^    (def |#|@))", "", cls, flags=re.M | re.S)
    # __slots__ (if any) gets the new fields
    cls = re.sub(r'__slots__ = \((.*?)\)', lambda mm: '__slots__ = ("lo", "hi", "L", "R", "ln", ' + ", ".join(
        f'"{f}"' for f, _ in fields) + (', "FULL"' if keep else "") + ")", cls, count=1)

    # children
    cls = re.sub(r"2 \* (\w+) \+ 1", r"self.R[\1]", cls)
    cls = re.sub(r"2 \* (\w+)", r"self.L[\1]", cls)
    cls = re.sub(r"(\w+) = self\.L\[(\w+)\]; (\w+) = \1 \+ 1", r"\1 = self.L[\2]; \3 = self.R[\2]", cls)

    # create children before every descent and at the start of every push
    out = []
    node = None
    for line in cls.split("\n"):
        dm = re.match(r"^    def (\w+)\(self, (\w+)", line)
        if dm:
            node = dm.group(2)
        tm = re.match(r"^(\s+)tm = \(tl \+ tr\) // 2", line)
        if tm and node:
            out.append(f"{tm.group(1)}self._kids({node})")
        out.append(line)
        if dm and dm.group(1) == "_push":
            out.append(f"        self._kids({node})")
    cls = "\n".join(out)

    # public entry points: the whole range is [lo, hi]; there is always a root
    cls = re.sub(r"\(1, 0, self\.n ?- ?1,", "(1, self.lo, self.hi,", cls)
    cls = re.sub(r" and self\.n\b(?! ==)", "", cls)
    cls = re.sub(r" or not self\.n\b", "", cls)
    cls = re.sub(r" or self\.n == 0", "", cls)
    cls = re.sub(r"if self\.n:\s*(\S)", r"\1", cls)
    assert "self.n" not in cls, [ln for ln in cls.split("\n") if "self.n" in ln]
    return pre + cls


# ================================================================================================ main

def main():
    import sys
    only_py = "--py" in sys.argv
    for folder in sorted(os.listdir(DIR)):
        path = os.path.join(DIR, folder, "template.py")
        if not os.path.exists(path) or "@data-structure-type: beats" not in open(path).read():
            continue
        head, body = split_header(open(path).read())
        m = re.search(r"^class (\w+)", body, re.M)
        name = "Sparse" + m.group(1).replace("_PERFORMANT", "")
        intro = ("\n# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root\n"
                 "# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)\n"
                 "# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the\n"
                 "# dense tree's, with children in L / R instead of at 2i / 2i + 1.\n")
        py = "\n".join(sparse_header(head, "#")) + "\n" + intro + sparse_costs(convert_py(body, name), "#")
        write_template(os.path.join(DIR, folder, "sparse.py"), py)
        if not only_py:
            from sparse_beats_cpp import convert_cpp  # noqa: E402
            chead, cbody = split_header(open(os.path.join(DIR, folder, "template.cpp")).read())
            cpp = "\n".join(sparse_header(chead, "//")) + "\n" + sparse_costs(convert_cpp(folder, cbody), "//")
            write_template(os.path.join(DIR, folder, "sparse.cpp"), cpp)
        print("wrote", folder)


if __name__ == "__main__":
    main()
