"""Fast mode for the C++ generic seg trees: writes Generic<Name>[.level][.norev].fast.cpp beside each file. The logic is
unchanged: sanitizers are skipped in the tree and in the functions you fill in, its vectors become HotVector (whose []
and size() still inline with sanitizers off), and the tree's min / max become plain comparisons, which do too. Public
signatures keep plain vector. Run this after gen_generic_examples.py and add_cpp_prelude.py.

    python3 gen_generic_fast.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TEMPLATES, "set-tests", "generators"))
from gen_sets import FAST_POOL_NOTE, FAST_VECTOR_PRELUDE, check_finished, must_replace  # noqa: E402

DIR = os.environ.get("GENERIC_DIR") or os.path.join(TEMPLATES, "segment-trees", "generic")
TREES = ("LazyDynamicSeg", "DynamicSeg", "LazySeg", "Seg", "PersistentLazyTreap", "PersistentTreap", "LazyTreap", "Treap")

MACRO, HOT = FAST_VECTOR_PRELUDE.split("// A vector whose")
MACRO = must_replace(MACRO, "#ifdef __SSE2__\n#include <immintrin.h>\n#endif\n\n", "")
MACRO = must_replace(MACRO, "// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.\n", "")
HOT = must_replace("// A vector whose" + HOT, "    using vector<U>::vector;\n", """    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
""")
FILL_IN_NOTE = """// LEETCODE_NO_SANITIZE stays on every function you fill in below. It does not carry into what a function calls, so
// anything they call needs it too:
//   LEETCODE_NO_SANITIZE long long addMod(long long a, long long b) { ... }  // a helper of yours
//   LEETCODE_NO_SANITIZE Node() { ... }                                      // a Node or Tag constructor
"""
FIELD = re.compile(r"^    (static inline |mutable )?vector<([^()\n]*)> ([\w, ]+)(;|\{)", re.M)
METHOD = re.compile(r"^    ((?:(?!//|using |struct |template )(?:[\w:]+(?:<[^;(){}]*>)?[&*]* )+)\w+\([^;{}]*\)(?: const)? \{)", re.M)
FILL_IN = re.compile(r"^((?:Node|Tag) (?:leaf|combine|reverse|apply|compose|blank)\()", re.M)
CONSTRUCTOR = re.compile(r"^(    // )((?:Node|Tag)\(\) \{)", re.M)


def plain_compare(line):
    """min(a, b) and max(a, b) as plain comparisons (a template's are side-effect free), which inline here."""
    start = 0
    while True:
        m = re.compile(r"(?<![\w.:])(min|max)\(").search(line, start)
        if not m:
            return line
        depth, comma, k = 0, None, m.end()
        while True:
            c = line[k]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                assert comma is None, line
                comma = k
            k += 1
        a, b = line[m.end():comma].strip(), line[comma + 1:k].strip()
        a, b = plain_compare(a), plain_compare(b)
        text = f"{a} {'<' if m[1] == 'min' else '>'} {b} ? {a} : {b}"
        before, after = line[:m.start()], line[k + 1:]
        if not (re.search(r"(= |return )$", before) and re.match(r"[;,]", after)):
            text = f"({text})"
        line = before + text + after
        start = m.start() + len(text)


def plain_compares(text):
    out = []
    for line in text.split("\n"):
        code, note = line, ""
        if not line.lstrip().startswith("//") and " // " in line:  # (a trailing note stays as written)
            code, note = line.split(" // ", 1)[0], " // " + line.split(" // ", 1)[1]
        elif line.lstrip().startswith("//") and "  // " in line.lstrip()[3:]:
            code, note = line[:line.rindex("  // ")], line[line.rindex("  // "):]
        out.append(plain_compare(code) + note)
    return "\n".join(out)


def fast_cpp(text, source, target):
    t = must_replace(text, source, target)
    stem = next((n for n in TREES if re.search(rf"^struct {n} \{{", t, re.M)), None)
    assert stem, f"{target}: no tree"
    start = re.search(rf"^(// Every op copies.*\n(?://.*\n)*)?struct {stem} \{{", t, re.M).start()
    head, tail = t[:start], t[start:]
    top = "using ll = long long;\n\n"
    assert top in head, f"{target}: no prelude"
    note = FAST_POOL_NOTE.replace("template.cpp", source).replace("inside this template", "in this template and in what you fill in")
    first = head.index(top) + len(top)
    fill, stubs = FILL_IN.subn(r"LEETCODE_NO_SANITIZE \1", head[first:])
    fill = CONSTRUCTOR.sub(r"\1LEETCODE_NO_SANITIZE \2", fill)
    tail, fields = FIELD.subn(r"    \1HotVector<\2> \3\4", tail)  # members only: signatures keep plain vector
    tail, methods = METHOD.subn(r"    LEETCODE_NO_SANITIZE \1", tail)
    tail, built = re.subn(rf"^    ({stem}\()", r"    LEETCODE_NO_SANITIZE \1", tail, flags=re.M)
    assert stubs >= 2 and fields and methods >= 3 and built, f"{target}: {stubs} stubs, {fields} fields, {methods} methods"
    return head[:first] + note + "\n" + MACRO + FILL_IN_NOTE + "\n" + fill + HOT + "\n" + plain_compares(tail)


def main():
    written = 0
    sources = sorted(f for f in os.listdir(DIR) if f.endswith(".cpp") and not f.endswith((".fast.cpp", ".debug.cpp")))
    for source in sources:
        target = source[:-4] + ".fast.cpp"
        out = check_finished(fast_cpp(open(os.path.join(DIR, source)).read(), source, target), target)
        path = os.path.join(DIR, target)
        if not os.path.exists(path) or open(path).read() != out:
            open(path, "w").write(out)
            written += 1
    print(f"{len(sources)} generics have fast mode, {written} files written")


if __name__ == "__main__":
    main()
