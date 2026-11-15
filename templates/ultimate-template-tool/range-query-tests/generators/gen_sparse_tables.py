"""Sparse tables with more than one aggregate: a static array with O(1) range min / max / AND / OR (and a range gcd in
one Euclid run), any two or more of them in one class. One folder per subset of two or more of the five
(sparse-table-<names>); the one-aggregate tables are the hand-written pointGet-rangeMin, pointGet-rangeMax,
pointGet-rangeGcd, pointGet-rangeAndQuery and pointGet-rangeOrQuery.

    python3 gen_sparse_tables.py

Each aggregate has its own table: level k holds that aggregate of every window of 2^k values, and a range is the
combine of the two windows of the largest power of two that fit, one starting at l and one ending at r (they overlap,
which is fine: every one of these gives the same answer when a value is counted twice). Then run gen_fast.py and
format_long_lines.py.
"""
import itertools
import os
import textwrap

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")

# name -> (op, word, table name, python combine(a, b), cpp combine(a, b), what the range op returns)
AGGS = {
    "min": ("rangeMin", "min", "mn", "a if a < b else b", "a < b ? a : b", "min of a[l..r]"),
    "max": ("rangeMax", "max", "mx", "a if a > b else b", "a > b ? a : b", "max of a[l..r]"),
    "gcd": ("rangeGcd", "gcd", "g", "gcd(a, b)", "std::gcd(a, b)", "gcd of |a[l]|, ..., |a[r]| (0 only if all are 0)"),
    "and": ("rangeAndQuery", "AND", "an", "a & b", "a & b", "a[l] & ... & a[r]"),
    "or": ("rangeOrQuery", "OR", "orr", "a | b", "a | b", "a[l] | ... | a[r]"),
}
ORDER = ["min", "max", "gcd", "and", "or"]
EUCLID = "log(U) ?"  # a gcd is one Euclid run
PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n"  # (so add_cpp_prelude.py is not needed)


def folder_of(names):
    return "sparse-table-" + "-".join(names)


def class_of(names):
    return "Sparse" + "".join(AGGS[n][1].capitalize() for n in names)


def header(cm, names):
    ops = sorted(["pointGet"] + [AGGS[n][0] for n in names])
    cost = {op: "1" for op in ops}
    if "gcd" in names:
        cost["rangeGcd"] = EUCLID
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: sparse-table"]
    if set(names) <= {"min", "max"}:  # (comparisons only, so it takes characters as it is)
        lines.append(f"{cm} @letters: same")
    lines.append(f"{cm} @complexities:")
    lines += [f"{cm}   {op}: {cost[op]}" for op in ops]
    lines.append(f"{cm}   build: {'N*log(N)*log(U) ?' if 'gcd' in names else 'N*log(N)'}")
    tables = " ".join(f"{AGGS[n][2]}[1*N*log(N)]" for n in names)
    lines += [f"{cm} @memory:", f"{cm}   layout: none", f"{cm}   node: {tables}", f"{cm}   tags: none", f"{cm}   other: none",
              f"{cm}   note: one table per aggregate ({', '.join(AGGS[n][1] for n in names)}), each log(N) levels of up to N "
              f"values; level 0 is the array itself"]
    return "\n".join(lines) + "\n"


def intro(cm, names):
    words = [AGGS[n][1] for n in names]
    what = ", ".join(words[:-1]) + " and " + words[-1]
    text = (f"Static range {what} in one class: one sparse table per aggregate. Level k of a table holds that aggregate "
            f"of every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, "
            f"one starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when "
            f"a value is counted twice). No updates. All indices 0-based, ranges inclusive.")
    if "gcd" in names:
        text += " A gcd is a Euclid run, O(log U), so rangeGcd costs one of those and the build N log N of them."
    return "\n".join(textwrap.wrap(text, 117, initial_indent=f"{cm} ", subsequent_indent=f"{cm} ")) + "\n"


def py_file(names):
    cls = class_of(names)
    out = [header("#", names), "\n", intro("#", names)]
    if "gcd" in names:
        out.append("from math import gcd\n")
    out.append(f'''

class {cls}:
    # O(N log N) -- arr: the array (a list)
    def __init__(self, arr):
        self.n = n = len(arr)
''')
    for n in names:
        _, word, tab, comb, _, _ = AGGS[n]
        out.append(f'''        # {tab}[k][i]: the {word} of arr[i .. i + 2^k - 1]
        self.{tab} = t = [list(arr)]
        half = 1
        while 2 * half <= n:
            prev = t[-1]
            t.append([{comb} for a, b in zip(prev, prev[half:])])
            half *= 2
''')
    out.append('''
    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.''' + AGGS[names[0]][2] + '''[0][i]
''')
    for n in names:
        op, _, tab, comb, _, returns = AGGS[n]
        cost = "O(log U)" if n == "gcd" else "O(1)"
        out.append(f'''
    # {cost} -- {returns}; needs 0 <= l <= r < n, else IndexError
    def {op}(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"{op}: needs 0 <= l <= r < n, got l = {{l}}, r = {{r}}, n = {{self.n}}")
        k = (r - l + 1).bit_length() - 1
        row = self.{tab}[k]
        a, b = row[l], row[r - (1 << k) + 1]
        return {comb}
''')
    return "".join(out)


def cpp_file(names):
    cls = class_of(names)
    tabs = [AGGS[n][2] for n in names]
    out = [PRELUDE, header("//", names), "\n", intro("//", names), "// T is any integral type (int, long long, ...).\n"]
    out.append(f'''template <typename T>
struct {cls} {{
    int n;
    // one table per aggregate: tab[k][i] = that aggregate of a[i .. i + 2^k - 1]
    vector<vector<T>> {", ".join(tabs)};

''')
    for n in names:
        _, word, tab, _, comb, _ = AGGS[n]
        out.append(f"    static T {tab}Of(T a, T b) {{ return {comb}; }}\n")
    build = "O(N log N log U) -- N log N gcds, each up to O(log U)" if "gcd" in names else "O(N log N)"
    out.append(f'''
    // {build}
    explicit {cls}(const vector<T>& a) : n((int)a.size()) {{
        int levels = n ? 32 - __builtin_clz(n) : 1;
''')
    for tab in tabs:
        out.append(f"        {tab}.assign(levels, vector<T>());\n        {tab}[0] = a;\n")
    out.append('''        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
''')
    for tab in tabs:
        out.append(f'''            {tab}[k].resize(len);
            for (int i = 0; i < len; i++) {tab}[k][i] = {tab}Of({tab}[k - 1][i], {tab}[k - 1][i + half]);
''')
    out.append(f'''        }}
    }}

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {{
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return {tabs[0]}[0][i];
    }}
''')
    for n in names:
        op, _, tab, _, _, returns = AGGS[n]
        cost = "O(log U)" if n == "gcd" else "O(1)"
        out.append(f'''
    // {cost} -- {returns}; needs 0 <= l <= r < n, else throws out_of_range
    T {op}(int l, int r) const {{
        if (l < 0 || l > r || r >= n) throw out_of_range("{op}: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return {tab}Of({tab}[k][l], {tab}[k][r - (1 << k) + 1]);
    }}
''')
    out.append("};\n")
    return "".join(out)


def main():
    made = 0
    for size in range(2, len(ORDER) + 1):
        for names in itertools.combinations(ORDER, size):
            path = os.path.join(DIR, folder_of(names))
            os.makedirs(path, exist_ok=True)
            write_template(os.path.join(path, "template.py"), py_file(names))
            write_template(os.path.join(path, "template.cpp"), cpp_file(names))
            made += 1
    print(made, "sparse table folders written")


if __name__ == "__main__":
    main()
