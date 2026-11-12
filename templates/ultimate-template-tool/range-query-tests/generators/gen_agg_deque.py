"""Aggregate deques (two stacks): a window that grows and shrinks at both ends, with the min / max / gcd / OR / AND of
the whole window in O(1), and the LCM and product % MOD too. One folder per non-empty subset of those seven
(agg-deque-<names>), plus agg-deque-sum-xor
with just the running sum and xor, which every folder has too (they can be undone, so no stacks are needed).

    python3 gen_agg_deque.py

Each half is a stack keeping, per aggregate, the value of its bottom..top (so a push or pop is O(1)); the whole window
is one combine of the two tops. A pop that empties a half moves half of the other over and rebuilds both (amortized
O(1), like the rolling hash deque). Then run add_cpp_prelude.py, the fast mode step below and format_long_lines.py.
"""
import itertools
import os

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")

# name -> (op, word, field suffix, python combine(a, b), python single(v), cpp combine(a, b), cpp single(v))
AGGS = {
    "min": ("minAll", "min", "mn", "a if a < b else b", "v", "a < b ? a : b", "v"),
    "max": ("maxAll", "max", "mx", "a if a > b else b", "v", "a > b ? a : b", "v"),
    "gcd": ("gcdAll", "gcd", "g", "gcd(a, b)", "abs(v)", "gcd(a, b)", "gcd(v, T(0))"),  # (each combine O(log U))
    "or": ("orAll", "OR", "orr", "a | b", "v", "a | b", "v"),
    "and": ("andAll", "AND", "an", "a & b", "v", "a & b", "v"),
    # (each combine O(log U); -1 once the LCM passes cap, see CAP_DOC)
    "lcm": ("lcmAll", "LCM", "lc", "self._lcm(a, b)", "self._lcmOne(v)", "lcmOf(a, b)", "lcmOne(v)"),
    # values kept % MOD in its stacks (not undoable: a value 0 mod MOD has no inverse)
    "prod": ("productAllMod", "product % MOD", "pr", "a * b % self.mod", "v % self.mod", "T(W(a) * b % mod)", "norm(v)"),
}
ORDER = ["min", "max", "gcd", "or", "and", "lcm", "prod"]
TOKEN = {"prod": "product-mod"}  # in folder and class names
# what the LCM templates say about their cap (the class name goes in {cls}, the call's leading args in {pre})
CAP_DOC = ("lcmAll answers -1 once the LCM passes cap, so it can't overflow. cap defaults to {dflt}; pass your own after "
           "{pre}, e.g. {example}. Removing values is safe: each half keeps the LCM (or -1) of every prefix of its stack, so "
           "once the values that pushed it past cap are popped, lcmAll is exact again.")
BASE_OPS = ["append", "appendLeft", "getAll", "pointGet", "pop", "popLeft", "size", "sumAll", "xorAll"]


def header(cm, names):
    ops = sorted(BASE_OPS + [AGGS[n][0] for n in names])
    cost = {op: "1" for op in ops}
    cost.update(getAll="N", pop="1 amortized", popLeft="1 amortized")
    euclid = [AGGS[n][0] for n in names if n in ("gcd", "lcm")]
    if euclid:  # a gcd is a Euclid run, O(log U): every push and gcdAll / lcmAll does one; a rebuild's chain telescopes
        cost.update(append="log(U)", appendLeft="log(U)", pop="log(U) amortized", popLeft="log(U) amortized")
        cost.update({op: "log(U)" for op in euclid})
    fields = " ".join(f"F{AGGS[n][2]}[1*N] B{AGGS[n][2]}[1*N]" for n in names)
    words = ", ".join(AGGS[n][1] for n in names)
    keeps = f"each half also keeps the {words} of its bottom..top, so the whole window's is one combine of the two tops; " if names else ""
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: agg-deque", f"{cm} @complexities:"]
    lines += [f"{cm}   {op}: {cost[op]}" for op in ops] + [f"{cm}   build: N"]
    lines += [f"{cm} @memory:", f"{cm}   layout: none", f"{cm}   node: front[1*N] back[1*N]{' ' + fields if fields else ''}",
              f"{cm}   tags: none", f"{cm}   other: none",
              f"{cm}   note: the front half (stored last to first) and the back half hold the window; {keeps}a pop that "
              f"empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals"]
    return "\n".join(lines) + "\n"


def intro(cm, names, cls=""):
    what = ", ".join(AGGS[n][1] for n in names)
    lead = (f"Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the "
            f"{what + ', ' if what else ''}sum and xor of the whole window in O(1). ")
    rest = ("Each half is a stack that keeps the aggregates of its bottom..top, so a push or pop is O(1) and the whole "
            "window is one combine of the two tops; a pop that empties its half moves half of the other over and rebuilds "
            "both, amortized O(1). The sum and xor are running totals. No point assign or range query: for those, use a seg "
            "tree or treap. All indices 0-based.")
    if {"gcd", "lcm"} & set(names):
        rest += " A gcd or LCM is a Euclid run, O(log U), so a push and gcdAll / lcmAll cost that."
    if "lcm" in names:
        pre = "arr and mod" if "prod" in names else "arr"
        mid = ", 1000000007" if "prod" in names else ""
        example = (f"{{cls}}<long long> d(arr{mid}, 1000000000LL)" if cm == "//" else f"{{cls}}(arr{mid}, cap=10**9)")
        rest += " " + CAP_DOC.format(dflt="the largest T (2^63 - 1 for long long)" if cm == "//" else "2**63 - 1", pre=pre,
                                     example=example)
    if "prod" in names:
        rest += " The product is kept % MOD (pass mod to the constructor)."
    rest = rest.replace("{cls}", cls)
    import textwrap
    return "\n".join(textwrap.wrap(lead + rest, 117, initial_indent=f"{cm} ", subsequent_indent=f"{cm} ")) + "\n"


def py_file(names, cls):
    fs = [AGGS[n][2] for n in names]
    prod = "prod" in names
    lcm = "lcm" in names
    slots = ", ".join(f'"{x}"' for x in ["front", "back", "sm", "xr"] + (["mod"] if prod else []) + (["cap"] if lcm else [])
                      + [p + f for f in fs for p in ("F", "B")])
    out = [header("#", names), intro("#", names, cls)]
    imports = ["gcd"] if {"gcd", "lcm"} & set(names) else []
    if imports:
        out.append(f"from math import {', '.join(imports)}\n")
    out.append(f'''

class {cls}:
    __slots__ = ({slots})

    # O(N) -- arr: the initial array (a list), or left out to start empty{"; mod: for the product" if prod else ""}{"; cap: lcmAll is -1 past it" if lcm else ""}
    def __init__(self, arr=(){", mod=10**9 + 7" if prod else ""}{", cap=2**63 - 1" if lcm else ""}):
        self.front, self.back = [], []  # front: the first values, stored last to first
        self.sm = self.xr = 0
''')
    if prod:
        out.append("        self.mod = mod\n")
    if lcm:
        out.append("        self.cap = cap\n")
    for f in fs:
        out.append(f"        self.F{f}, self.B{f} = [], []  # F{f}[j]: over front[0..j]; B{f}[k]: over back[0..k]\n")
    out.append('''        for v in arr:
            self.append(v)

    # O(1) -- the current length of the window
    def size(self):
        return len(self.front) + len(self.back)

    # O(N) -- the whole window as a list
    def getAll(self):
        return self.front[::-1] + self.back

    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        f = len(self.front)
        return self.front[f - 1 - i] if i < f else self.back[i - f]

    # O(1) -- append v at the right end
    def append(self, v):
        self.sm += v
        self.xr ^= v
''')
    for n in names:
        f, comb, single = AGGS[n][2], AGGS[n][3], AGGS[n][4]
        out.append(f"        S = self.B{f}\n        if S:\n            a, b = S[-1], {single}\n            S.append({comb})\n"
                   f"        else:\n            S.append({single})\n")
    out.append('''        self.back.append(v)

    # O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        self.sm += v
        self.xr ^= v
''')
    for n in names:
        f, comb, single = AGGS[n][2], AGGS[n][3], AGGS[n][4]
        out.append(f"        S = self.F{f}\n        if S:\n            a, b = S[-1], {single}\n            S.append({comb})\n"
                   f"        else:\n            S.append({single})\n")
    pops_b = "".join(f"        self.B{f}.pop()\n" for f in fs)
    pops_f = "".join(f"        self.F{f}.pop()\n" for f in fs)
    out.append(f'''        self.front.append(v)

    # O(1) amortized -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        if not self.back:
            self._moveToBack()
{pops_b}        v = self.back.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(1) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises
    # IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
{pops_f}        v = self.front.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.sm

    # O(1) -- xor of the whole window; needs n >= 1, else raises IndexError
    def xorAll(self):
        if self.size() < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.xr
''')
    for n in names:
        op, word, f, comb = AGGS[n][0], AGGS[n][1], AGGS[n][2], AGGS[n][3]
        out.append(f'''
{query_doc(n, '#')}    def {op}(self):
        if self.size() < 1:
            raise IndexError("{op}: needs n >= 1")
        F, B = self.F{f}, self.B{f}
        if not F:
            return B[-1]
        if not B:
            return F[-1]
        a, b = F[-1], B[-1]
        return {comb}
''')
    out.append('''
    # ---- internals ----

    def _moveToFront(self):  # the back half's first half becomes the front (the front is empty)
        k = (len(self.back) + 1) // 2
        self.front = self.back[:k][::-1]
        self.back = self.back[k:]
        self._rebuild()

    def _moveToBack(self):  # the front half's values nearest the middle (stored first) become the back
        k = (len(self.front) + 1) // 2
        self.back = self.front[:k][::-1]
        self.front = self.front[k:]
        self._rebuild()

    def _rebuild(self):  # every half's aggregates, O(size())
''')
    lcm_py = """
    def _lcmOne(self, v):  # |v|, or -1 past cap
        v = abs(v)
        return v if v <= self.cap else -1

    def _lcm(self, a, b):  # 0 if either is 0 (an LCM with a 0 is 0); else -1 if either is past cap or the LCM is
        if a == 0 or b == 0:
            return 0
        if a < 0 or b < 0:
            return -1
        r = a // gcd(a, b) * b
        return r if r <= self.cap else -1
""" if lcm else ""
    if not names:
        out.append("        pass\n")
    for n in names:
        f, comb, single = AGGS[n][2], AGGS[n][3], AGGS[n][4]
        for side, src in (("F", "front"), ("B", "back")):
            out.append(f"        S = []\n        for v in self.{src}:\n            if S:\n                a, b = S[-1], {single}\n"
                       f"                S.append({comb})\n            else:\n                S.append({single})\n"
                       f"        self.{side}{f} = S\n")
    out.append(lcm_py)
    return "".join(out)


def cpp_file(names, cls):
    fs = [AGGS[n][2] for n in names]
    out = [header("//", names), intro("//", names, cls), "// T: int, long long, ...; the sum is kept in S (long long for small T).\n"]
    stacks = ", ".join(["front", "back"] + [p + f for f in fs for p in ("F", "B")])
    prod = "prod" in names
    CAP = lambda n: "[this]" if n in ("prod", "lcm") else "[]"  # noqa: E731  (the product's read mod, the LCM's cap)
    wide = """    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
""" if prod else ""
    modm = """    T mod;
    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }
""" if prod else ""
    lcm = "lcm" in names
    params = ", T mod = 1000000007" * prod + ", T cap = numeric_limits<T>::max()" * lcm
    inits = ", ".join(["mod(mod)"] * prod + ["cap(cap)"] * lcm)
    ctor = f"    explicit {cls}(const vector<T>& arr = {{}}{params}){' : ' + inits if inits else ''} {{"
    lcm_helper = """
    T lcmOne(T v) const { T x = v < 0 ? -v : v; return x > cap ? T(-1) : x; }  // |v|, or -1 past cap

    T lcmOf(T a, T b) const {  // 0 if either is 0 (an LCM with a 0 is 0); else -1 if either is past cap or the LCM is
        if (a == 0 || b == 0) return 0;
        if (a < 0 || b < 0) return -1;
        T r;
        if (__builtin_mul_overflow(a / gcd(a, b), b, &r) || r > cap) return -1;
        return r;
    }
""" if lcm else ""
    out.append(f'''template <typename T>
struct {cls} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
{wide}    vector<T> {stacks};  // front: the first values, stored last to first; F*[j] over front[0..j], B*[k] over back[0..k]
    S sm = 0;
    T xr = 0;
{modm}{"    T cap;  // lcmAll is -1 past it" + chr(10) if lcm else ""}
    // O(N) -- arr: the initial array, or left out to start empty{"; mod: for the product" if prod else ""}{"; cap: lcmAll is -1 past it" if lcm else ""}
{ctor}
        for (const T& v : arr) append(v);
    }}

    // O(1) -- the current length of the window
    int size() const {{ return int(front.size() + back.size()); }}

    // O(N) -- the whole window
    vector<T> getAll() const {{
        vector<T> out(front.rbegin(), front.rend());
        out.insert(out.end(), back.begin(), back.end());
        return out;
    }}

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {{
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int f = int(front.size());
        return i < f ? front[f - 1 - i] : back[i - f];
    }}

    // O(1) -- append v at the right end
    void append(T v) {{
        sm += S(v);
        xr ^= v;
''')
    for n in names:
        f, comb, single = AGGS[n][2], AGGS[n][5], AGGS[n][6]
        out.append(f"        push(B{f}, v, {CAP(n)}(T a, T b) {{ return {comb}; }}, {CAP(n)}(T v) {{ return {single}; }});\n")
    out.append('''        back.push_back(v);
    }

    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    void appendLeft(T v) {
        sm += S(v);
        xr ^= v;
''')
    for n in names:
        f, comb, single = AGGS[n][2], AGGS[n][5], AGGS[n][6]
        out.append(f"        push(F{f}, v, {CAP(n)}(T a, T b) {{ return {comb}; }}, {CAP(n)}(T v) {{ return {single}; }});\n")
    pops_b = "".join(f"        B{f}.pop_back();\n" for f in fs)
    pops_f = "".join(f"        F{f}.pop_back();\n" for f in fs)
    out.append(f'''        front.push_back(v);
    }}

    // O(1) amortized -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {{
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
{pops_b}        T v = back.back();
        back.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }}

    // O(1) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    T popLeft() {{
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
{pops_f}        T v = front.back();
        front.pop_back();
        sm -= S(v);
        xr ^= v;
        return v;
    }}

    // O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else throws out_of_range
    S sumAll() const {{
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return sm;
    }}

    // O(1) -- xor of the whole window; needs n >= 1, else throws out_of_range
    T xorAll() const {{
        if (size() < 1) throw out_of_range("xorAll: needs n >= 1");
        return xr;
    }}
''')
    for n in names:
        op, word, f, comb = AGGS[n][0], AGGS[n][1], AGGS[n][2], AGGS[n][5]
        out.append(f'''
{query_doc(n, '//')}    T {op}() const {{
        if (size() < 1) throw out_of_range("{op}: needs n >= 1");
        if (F{f}.empty()) return B{f}.back();
        if (B{f}.empty()) return F{f}.back();
        T a = F{f}.back(), b = B{f}.back();
        return {comb};
    }}
''')
    rebuild = "".join(
        f"        rebuildOne(F{AGGS[n][2]}, front, {CAP(n)}(T a, T b) {{ return {AGGS[n][5]}; }}, {CAP(n)}(T v) {{ return {AGGS[n][6]}; }});\n"
        f"        rebuildOne(B{AGGS[n][2]}, back, {CAP(n)}(T a, T b) {{ return {AGGS[n][5]}; }}, {CAP(n)}(T v) {{ return {AGGS[n][6]}; }});\n"
        for n in names)
    helpers = '''
    template <typename C, typename O>
    static void push(vector<T>& st, T v, C comb, O one) {
        st.push_back(st.empty() ? one(v) : comb(st.back(), one(v)));  // (one(v): |v| for gcd / LCM, v % MOD)
    }

    template <typename C, typename O>
    static void rebuildOne(vector<T>& st, const vector<T>& src, C comb, O one) {
        st.clear();
        for (const T& v : src) push(st, v, comb, one);
    }
''' if names else ""
    out.append(f'''
    // ---- internals ----
{lcm_helper}{helpers}
    void moveToFront() {{  // the back half's first half becomes the front (the front is empty)
        size_t k = (back.size() + 1) / 2;
        front.assign(back.rend() - k, back.rend());
        back.erase(back.begin(), back.begin() + k);
        rebuild();
    }}

    void moveToBack() {{  // the front half's values nearest the middle (stored first) become the back
        size_t k = (front.size() + 1) / 2;
        back.assign(front.rend() - k, front.rend());
        front.erase(front.begin(), front.begin() + k);
        rebuild();
    }}

    void rebuild() {{  // every half's aggregates, O(size())
{rebuild}    }}
}};
''')
    return "".join(out)


def query_doc(n, cm):
    """the comment over an aggregate's whole-window query, wrapped to 120 columns"""
    import textwrap
    cost = "log U" if n in ("gcd", "lcm") else "1"
    cap = " or -1 once it passes cap" if n == "lcm" else ""
    err = "raises IndexError" if cm == "#" else "throws out_of_range"
    text = f"O({cost}) -- {AGGS[n][1]} of the whole window (one combine of the two halves' tops){cap}; needs n >= 1, else {err}"
    return textwrap.fill(text, 120, initial_indent=f"    {cm} ", subsequent_indent=f"    {cm} ") + "\n"


def euclid_costs(text, names):
    """the push / pop comments of a deque with a gcd or LCM: those combines are Euclid runs, O(log U)"""
    if not {"gcd", "lcm"} & set(names):
        return text
    for cm in ("#", "//"):
        text = text.replace(f"    {cm} O(1) -- append v", f"    {cm} O(log U) -- append v")
        text = text.replace(f"    {cm} O(1) -- insert v at the left end", f"    {cm} O(log U) -- insert v at the left end")
        text = text.replace(f"    {cm} O(1) amortized -- remove", f"    {cm} O(log U) amortized -- remove")
    return text


def main():
    made = []
    subsets = [()] + [c for k in range(1, len(ORDER) + 1) for c in itertools.combinations(ORDER, k)]
    for names in subsets:
        tokens = [TOKEN.get(n, n) for n in names]
        folder = "agg-deque-" + ("-".join(tokens) if names else "sum-xor")
        cls = "AggDeque" + "".join(t.replace("-", " ").title().replace(" ", "") for t in tokens)
        path = os.path.join(DIR, folder)
        os.makedirs(path, exist_ok=True)
        write_template(os.path.join(path, "template.py"), euclid_costs(py_file(list(names), cls), names))
        write_template(os.path.join(path, "template.cpp"), euclid_costs(cpp_file(list(names), cls), names))
        made.append(folder)
    print(len(made), "folders written")


if __name__ == "__main__":
    main()
