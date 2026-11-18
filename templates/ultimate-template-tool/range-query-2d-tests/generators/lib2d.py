"""Shared by every 2D / 3D range query generator: the aggregates, the header writer and the file writer.

A generator builds one folder per template under templates/ultimate-template-tool/range-queries-2d, each holding
template.py and template.cpp with the same tagged header the 1D range query templates use, plus

    @input: grid | points | online | batch | grid-3d     what the constructor is given (the picker's switch)
    @empty-cells: yes                                    (optional) cells can be empty: see SPEC.md, section 2

Costs use R, C (a grid's rows and columns), N (how many points were given, or how many ops a batch holds), U (the
size of a coordinate range) and X, Y, Z (a 3D grid's sides).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "range-queries-2d")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d"

INPUTS = ("grid", "points", "online", "batch", "grid-3d")

# ---- C++ is fast by default: sanitizers are skipped inside every template (the range query tab's "fast mode", here
# with no slower twin). The marker and HotVector are the range query generators' own, so the text stays the same.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "range-query-tests"))
from gen_fast import PRELUDE as HOT_VECTOR_PRELUDE  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from format_long_lines import reflow_text  # noqa: E402

# (nothing here uses the SSE header; and one accessor is past 120 columns as it comes)
HOT_VECTOR_PRELUDE = HOT_VECTOR_PRELUDE.replace("#ifdef __SSE2__\n#include <immintrin.h>\n#endif\n\n", "")
_LONG = "operator[](size_t i) const { return this->_M_impl._M_start[i]; }"
assert _LONG in HOT_VECTOR_PRELUDE, "the range query generators' HotVector changed: update this"
HOT_VECTOR_PRELUDE = HOT_VECTOR_PRELUDE.replace(_LONG, "operator[](size_t i) const {\n        return this->_M_impl._M_start[i];\n    }")

FAST_NOTE = """// Sanitizers are skipped inside this template (its methods start with LEETCODE_NO_SANITIZE): where they run, like on
// LeetCode, that is most of its speed. The drawback: a bad memory access inside the template goes unreported. Arguments
// are still checked and still throw. Constructors are left alone. It needs GCC or Clang and C++17.
"""
HOT_HELPERS = {
    "hotMin(": """template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }
""",
    "hotMax(": """template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMax(A a, A b) { return a < b ? b : a; }
""",
    "hotLowerBound(": """// how many of the n sorted values at `first` are < x (std::lower_bound as a count, inlined with sanitizers skipped)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE int hotLowerBound(const A* first, int n, A x) {
    int lo = 0;
    while (n > 0) {
        int half = n >> 1;
        if (first[lo + half] < x) lo += half + 1, n -= half + 1;
        else n = half;
    }
    return lo;
}
""",
    "hotUpperBound(": """// how many of the n sorted values at `first` are <= x (std::upper_bound as a count)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE int hotUpperBound(const A* first, int n, A x) {
    int lo = 0;
    while (n > 0) {
        int half = n >> 1;
        if (!(x < first[lo + half])) lo += half + 1, n -= half + 1;
        else n = half;
    }
    return lo;
}
""",
}
# methods that keep sanitizers: they run once, on plain vectors (constructors are never marked either)
UNMARKED = {"build", "getAll"}
_NOT_A_METHOD = ("//", "using ", "struct ", "template ", "explicit ", "return ", "if ", "for ", "while ", "else", "throw ", "static constexpr ",
                 "typedef ", "LEETCODE_")


def make_fast(lines):
    """A finished C++ template with sanitizers skipped: vector members become HotVector, every method but the
    constructors starts with LEETCODE_NO_SANITIZE, min / max become the helpers that still inline."""
    cut = lines.index("") + 1  # (the tagged header ends at its first blank line)
    head, body = lines[:cut], lines[cut:]
    out, nested, fields, methods = [], False, 0, 0
    for line in body:
        if re.match(r"^    struct \w+ \{\s*(//.*)?$", line):
            nested = True
        elif line == "    };":
            nested = False
        pad = "        " if nested else "    "
        rest = line[len(pad):] if line.startswith(pad) and not line.startswith(pad + " ") else None
        if rest is not None and not rest.startswith(_NOT_A_METHOD):
            m = re.match(r"^(static inline |mutable )?vector<([^()\n]*)> ([\w, ]+)(;|\{)", rest)
            if m:
                line = pad + f"{m.group(1) or ''}HotVector<{m.group(2)}> {m.group(3)}{m.group(4)}" + rest[m.end():]
                fields += 1
            else:
                m = re.match(r"^((?:static )?[\w:<>,&* ]+? )(\w+)\(([^;{}]*)\)( const)? \{", rest)
                if m and m.group(2) not in UNMARKED:
                    line = pad + "LEETCODE_NO_SANITIZE " + rest
                    methods += 1
        if not line.lstrip().startswith("//"):
            line = re.sub(r"(?<![\w:.>])(max|min)\(", lambda g: "hotMax(" if g.group(1) == "max" else "hotMin(", line)
        out.append(line)
    assert methods, "no method was marked"
    text = "\n".join(out)
    helpers = "".join(code for name, code in HOT_HELPERS.items() if name in text)
    if "hotMin(" in text or "hotMax(" in text:
        helpers = "// min / max that still inline with sanitizers skipped (std::min and std::max do not)\n" + helpers
    prelude = FAST_NOTE + "\n" + HOT_VECTOR_PRELUDE + helpers
    return head + prelude.rstrip("\n").split("\n") + [""] + out

WRITTEN = set()  # folders written by this run
CHECK = "--check" in sys.argv  # write nothing: list in STALE every file that differs from what the generators make now
STALE = []


class Agg:
    """One aggregate a tree can keep: its array name, its ops, what it is over nothing, and how two combine."""

    def __init__(self, key, arr, word, py_id, cpp_id, cpp_type, none_py, none_cpp, none_words_py, none_words_cpp):
        self.key = key  # "sum"
        self.arr = arr  # "sm": the array's name in the code
        self.word = word  # "sum": how comments call it
        self.cap = key[0].upper() + key[1:]  # "Sum"
        self.rect = f"rect{self.cap}"
        self.all = f"{key}All"
        self.py_id, self.cpp_id, self.cpp_type = py_id, cpp_id, cpp_type
        # what a query over no set cell hands back, as code and as the words a comment uses
        self.none_py, self.none_cpp = none_py, none_cpp
        self.none_words_py, self.none_words_cpp = none_words_py, none_words_cpp

    # ---- Python
    def py_merge(self, dst, a, b):
        """Lines setting dst to the combine of expressions a and b (array reads)."""
        if self.key == "max":
            return [f"lhs = {a}", f"rhs = {b}", f"{dst} = lhs if lhs > rhs else rhs"]
        if self.key == "min":
            return [f"lhs = {a}", f"rhs = {b}", f"{dst} = lhs if lhs < rhs else rhs"]
        if self.key == "gcd":
            return [f"{dst} = gcd({a}, {b})"]
        return [f"{dst} = {a} {PY_SYM[self.key]} {b}"]

    def py_take(self, res, a):
        """Lines folding expression a into the running result res."""
        if self.key == "max":
            return [f"cand = {a}", f"if cand > {res}:", f"    {res} = cand"]
        if self.key == "min":
            return [f"cand = {a}", f"if cand < {res}:", f"    {res} = cand"]
        if self.key == "gcd":
            return [f"{res} = gcd({res}, {a})"]
        return [f"{res} {PY_SYM[self.key]}= {a}"]

    def py_result(self, res):
        """The expression a query returns for running result res."""
        if self.key == "max":
            return f"None if {res} == NEG else {res}"
        if self.key == "min":
            return f"None if {res} == POS else {res}"
        return res

    # ---- C++
    def cpp_comb(self, a, b):
        if self.key in ("max", "min"):
            return f"{self.key}({a}, {b})"
        if self.key == "gcd":
            return f"gcdOf({a}, {b})"
        return f"{a} {PY_SYM[self.key]} {b}"

    def cpp_take(self, res, a):
        if self.key in ("max", "min"):
            return f"{res} = {self.key}({res}, {a});"
        if self.key == "gcd":
            return f"{res} = gcdOf({res}, {a});"
        return f"{res} {PY_SYM[self.key]}= {a};"


PY_SYM = {"sum": "+", "xor": "^", "and": "&", "or": "|"}

AGGS = {
    a.key: a
    for a in [
        Agg("sum", "sm", "sum", "0", "S(0)", "S", "0", "0", "0", "0"),
        Agg("min", "mn", "min", "POS", "NO_MIN", "T", "None", "NO_MIN", "None", "NO_MIN"),
        Agg("max", "mx", "max", "NEG", "NO_MAX", "T", "None", "NO_MAX", "None", "NO_MAX"),
        Agg("gcd", "gc", "gcd", "0", "T(0)", "T", "0", "0", "0", "0"),
        Agg("xor", "xr", "xor", "0", "T(0)", "T", "0", "0", "0", "0"),
        Agg("and", "an", "AND", "-1", "T(-1)", "T", "-1", "-1", "-1 (every bit set)", "-1 (every bit set)"),
        Agg("or", "orr", "OR", "0", "T(0)", "T", "0", "0", "0", "0"),
    ]
}
AGG_ORDER = ["sum", "min", "max", "gcd", "xor", "and", "or"]
# which aggregate a cell's own value is read from (and what an empty cell reads as), first one present
READ_ORDER = ["max", "min", "sum", "xor", "or", "gcd", "and"]


def subsets(keys):
    """Every non-empty subset of keys, in order."""
    out = []
    for mask in range(1, 1 << len(keys)):
        out.append([k for i, k in enumerate(keys) if mask >> i & 1])
    return out


def read_agg(aggs):
    return next(AGGS[k] for k in READ_ORDER if k in aggs)


def cost_note(aggs):
    """" ?" when a cost pays for gcd work (the 1D templates mark those bounds as unsure the same way)."""
    return " ?" if "gcd" in aggs else ""


def indent(lines, n=1):
    return [("    " * n + line) if line else "" for line in lines]


def header(folder, lang, ops, dstype, costs, build, memory, input_kind, extra_tags=()):
    """The tagged header. costs: {op: cost}; memory: dict(layout, node, tags, other, note)."""
    cm = "#" if lang == "py" else "//"
    assert input_kind in INPUTS, input_kind
    ops = sorted(ops)
    missing = [op for op in ops if op not in costs]
    assert not missing, f"{folder}: no cost for {missing}"
    lines = [
        f"{cm} Template by https://github.com/ishaanbuildsthings",
        f"{cm} {URL}/{folder}/template.{lang}",
    ]
    if lang == "cpp":
        lines += ["#include <bits/stdc++.h>", "using namespace std;"]
    lines += [
        f"{cm} @operations: {' '.join(ops)}",
        f"{cm} @data-structure-type: {dstype}",
        f"{cm} @input: {input_kind}",
    ]
    lines += [f"{cm} @{tag}: {value}" for tag, value in extra_tags]
    lines.append(f"{cm} @complexities:")
    lines += [f"{cm}   {op}: {costs[op]}" for op in ops]
    lines.append(f"{cm}   build: {build}")
    lines.append(f"{cm} @memory:")
    lines.append(f"{cm}   layout: {memory['layout']}")
    for group in ("node", "tags", "other"):
        lines.append(f"{cm}   {group}: {memory.get(group, 'none')}")
    if memory.get("note"):
        lines.append(f"{cm}   note: {memory['note']}")
    lines.append("")
    return lines


def wrap_comment(text, cm, width=118):
    """A paragraph as comment lines within the width."""
    out, cur = [], cm
    for word in text.split():
        if len(cur) + 1 + len(word) > width and cur != cm:
            out.append(cur)
            cur = cm
        cur += " " + word
    if cur != cm:
        out.append(cur)
    return out


def _wrap_long_comments(lines, cm):
    """Comment-only lines past 120 columns are rewrapped at their own indentation (header tag lines are left alone)."""
    out, in_header = [], True
    for line in lines:
        body = line.lstrip()
        if in_header and line == "":
            in_header = False
        if not in_header and len(line) > 120 and cm == "//":
            m = re.match(r"^(\s*)((?:if|while|for) \(.*\)) ([^{}]*;)$", line)  # a one-line if / loop: body on its own line
            if m:
                out += [m.group(1) + m.group(2), m.group(1) + "    " + m.group(3)]
                continue
        if not in_header and len(line) > 120 and body.startswith("__slots__ = ("):  # a long tuple of names: two lines
            pad = line[: len(line) - len(body)]
            names = body[len("__slots__ = ("):-1].split(", ")
            half = (len(names) + 1) // 2
            out += [pad + "__slots__ = (" + ", ".join(names[:half]) + ",", pad + " " * len("__slots__ = (") + ", ".join(names[half:]) + ")"]
            continue
        if not in_header and len(line) > 120 and not body.startswith(cm) and f"  {cm} " in line and '"' not in line:
            code, note = line.split(f"  {cm} ", 1)  # a trailing comment moves to its own line above
            pad = line[: len(line) - len(body)]
            out += [f"{pad}{cm} {note}", code.rstrip()]
            continue
        if in_header or len(line) <= 120 or not body.startswith(cm + " "):
            out.append(line)
            continue
        pad = line[: len(line) - len(body)]
        out += [pad + piece for piece in wrap_comment(body[len(cm):], cm, 118 - len(pad))]
    return out


def write(folder, py_lines, cpp_lines):
    """Writes range-queries-2d/<folder>/template.{py,cpp} (only when changed, so timestamps stay put)."""
    assert folder not in WRITTEN, f"{folder} written twice"
    WRITTEN.add(folder)
    d = os.path.join(OUT, folder)
    texts = {}
    for name, lines in (("template.py", py_lines), ("template.cpp", cpp_lines)):
        if lines is None:
            continue
        if name.endswith(".cpp"):
            lines = make_fast(lines)
        text = "\n".join(_wrap_long_comments(lines, "#" if name.endswith(".py") else "//")).rstrip("\n") + "\n"
        # (what format_long_lines.py would do to it, so running the formatter over the repo changes nothing here)
        text = reflow_text(text, name.endswith(".py"))
        long = [line for line in text.split("\n") if len(line) > 120 and "http" not in line and " @" not in line[:6]
                and not line.lstrip("#/ ").startswith(("node:", "tags:", "other:", "note:"))]
        assert not long, f"{folder}/{name}: lines over 120 columns:\n" + "\n".join(long)
        texts[name] = text
    if not CHECK:
        os.makedirs(d, exist_ok=True)
    for name, text in texts.items():
        path = os.path.join(d, name)
        if not os.path.exists(path) or open(path).read() != text:
            if CHECK:
                STALE.append(f"{folder}/{name}")
            else:
                open(path, "w").write(text)


def unwritten():
    """After every generator ran: the folders on disk that none of them writes any more (never deleted here)."""
    if not os.path.isdir(OUT):
        return []
    return sorted(f for f in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, f)) and f not in WRITTEN)


def py_raise(exc, msg, depth):
    """`raise exc(f"msg")` as lines (not indented): the f-string is split at a ", " when the line, indented `depth`
    levels, would pass 120 columns."""
    room = 118 - 4 * depth
    one = f'raise {exc}(f"{msg}")'
    if len(one) <= room:
        return [one]
    pad = " " * len(f"raise {exc}(")
    pieces, cur = [], ""
    for part in msg.split(", "):
        nxt = part if not cur else cur + ", " + part
        if cur and len(pad) + len(nxt) + 6 > room:
            pieces.append(cur + ", ")
            cur = part
        else:
            cur = nxt
    pieces.append(cur)
    lines = [f'raise {exc}(f"{pieces[0]}"'] + [f'{pad}f"{p}"' for p in pieces[1:]]
    lines[-1] += ")"
    return lines


def cpp_throw(cond, exc, msg, depth):
    """`if (cond) throw exc("msg");` as one line, or two when too long."""
    one = f'if ({cond}) throw {exc}("{msg}");'
    if len(one) <= 118 - 4 * depth:
        return [one]
    return [f"if ({cond})", f'    throw {exc}("{msg}");']
