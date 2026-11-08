"""Ops a template gets for free from ones it already has, added to every template.* / sparse.* / letters.* file as it is
written (note_lang.write_template) and by the rewrite pass (python3 note_lang.py):

  pop(), popLeft()                       on everything with cut, pointGet and size: read the end value, cut it out
  hashAll()                              on everything with rangeHash (dense files): rangeHash of the whole array
  sumAll(), minAll(), maxAll(), gcdAll(), xorAll(), andAll(), orAll()   on everything with the range op (dense files):
                                         O(1) off the root where a treap keeps it, else the range op over everything
  longestPalCenteredAtI(i)               on everything with isPalindrome (dense files): (l, r) by a binary search on the
  longestPalCenteredAtIPlusOne(i)        radius, log N calls of isPalindrome

They are left out of folder names (note_lang.FREE_OPS), like getAll and size.
"""
import math
import re

FACTORS = {"1": 1, "N": 2e5, "log(N)": math.log2(2e5), "log^2(N)": math.log2(2e5) ** 2, "sqrt(N)": math.sqrt(2e5),
           "sqrt(NlogN)": math.sqrt(2e5 * math.log2(2e5)), "sqrt(N/logN)": math.sqrt(2e5 / math.log2(2e5)),
           "log(U)": math.log2(1e9), "log(log(U))": math.log2(math.log2(1e9)), "U": 1e9, "U/64": 1e9 / 64,
           "log64(U)": math.log2(1e9) / 6}


def _split(cost):
    m = re.match(r"(.*?)((?: amortized| expected)?(?: \?)?)$", cost)
    return m.group(1), m.group(2)


def _value(cost):
    body = _split(cost)[0]
    return sum(math.prod(FACTORS[f] if f in FACTORS else float(f) for f in term.split("*")) for term in body.split("+"))


def _max_cost(a, b):
    """the larger of two costs, with the weaker guarantee of the two (amortized / expected / ?)"""
    body = _split(a)[0] if _value(a) >= _value(b) else _split(b)[0]
    suffix = " amortized" if "amortized" in a + b else " expected" if "expected" in a + b else ""
    return body + suffix + (" ?" if "?" in a + b else "")


def _times_log(cost):
    """cost * log(N): a walk of log N steps, each costing cost"""
    body, suffix = _split(cost)
    terms = []
    for term in body.split("+"):
        fs = term.split("*")
        assert "log^2(N)" not in fs, f"can't write log^3(N): {cost}"
        if "log(N)" in fs:
            fs[fs.index("log(N)")] = "log^2(N)"
        elif fs == ["1"]:
            fs = ["log(N)"]
        else:
            fs = ["log(N)"] + fs
        terms.append("*".join(fs))
    return "+".join(terms) + suffix


def _header(text, cm):
    ops = re.search(rf"^{re.escape(cm)} @operations: (.*)$", text, re.M)
    costs = dict(re.findall(rf"^{re.escape(cm)}   (\w+): (.+?)\s*$", text, re.M))
    return ops, costs


def _classes(text, lang):
    pat = r"^class \w+" if lang == "py" else r"^(?:template <[^>]*>\n)?struct \w+"
    starts = [m.start() for m in re.finditer(pat, text, re.M)]
    return [(s, starts[k + 1] if k + 1 < len(starts) else len(text)) for k, s in enumerate(starts)]


def _has(cls, lang, name):
    return re.search(rf"^    def {name}\(self\b" if lang == "py" else rf"^    [\w:<>, *&]+ {name}\(", cls, re.M) is not None


def _length(cls, lang):
    """how the class spells its current length: size() when it has one, else its n member; None if neither"""
    if _has(cls, lang, "size"):
        return "self.size()" if lang == "py" else "size()"
    if lang == "py" and re.search(r"self\.n = ", cls):
        return "self.n"
    if lang == "cpp" and re.search(r"^    (?:int|long long) n[,;]| n = ", cls, re.M):
        return "n"
    return None


def _insert(cls, lang, block):
    """block added to the class before its internals marker, else after its last method"""
    m = re.search(r"^    (?:#|//) ---- internals", cls, re.M)
    if m:
        return cls[:m.start()] + block + "\n" + cls[m.start():]
    if lang == "cpp":
        k = cls.rfind("\n};")
        assert k != -1, "struct without a closing };"
        return cls[:k].rstrip("\n") + "\n\n" + block + cls[k:]
    # after the class's last line of code (a method body line, not just its def line, which would split the method open)
    body = cls.rstrip("\n")
    assert re.search(r"^    \S", body, re.M), "class without methods"
    return body + "\n\n" + block.rstrip("\n") + cls[len(body):]


def _pop_block(lang, cost):
    if lang == "py":
        return f'''    # O({cost}) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        n = self.size()
        if n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(n - 1)
        self.cut(n - 1, n - 1)
        return v

    # O({cost}) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.cut(0, 0)
        return v
'''
    return f'''    // O({cost}) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {{
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }}

    // O({cost}) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    T popLeft() {{
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }}
'''


def _root_hash(cls, lang):
    """the O(1) expression for the whole array's hash when the structure keeps it at a root (treaps: the root node's
    forward hash), else None"""
    if lang == "py":
        m = re.search(r"    def rangeHash\(self, l, r\):(.*?)\n    def ", cls, re.S)
        if m and "res = self.fh[b]" in m.group(1) and re.search(r"self\.root = ", cls):
            return "self.fh[self.root]"
        return None
    m = re.search(r" rangeHash\((?:int|long long) l, (?:int|long long) r\)[^{]*\{(.*?)\n    \}", cls, re.S)
    if m and "U64 res = nd[b].fh;" in m.group(1) and re.search(r"^    int root\b", cls, re.M):
        return "nd[root].fh"
    return None


AGGREGATES = {"rangeSum": ("sumAll", "sum"), "rangeMin": ("minAll", "min"), "rangeMax": ("maxAll", "max"),
              "rangeGcd": ("gcdAll", "gcd"), "rangeXorQuery": ("xorAll", "xor"), "rangeAndQuery": ("andAll", "AND"),
              "rangeOrQuery": ("orAll", "OR")}
ROOTS_PY = {"b": "self.root", "be": "self.rE", "bo": "self.rO"}
ROOTS_CPP = {"b": "root", "be": "rE", "bo": "rO"}


def _root_aggregate(cls, lang, op):
    """the O(1) expression for op over the whole array when the structure keeps it at its root(s): the "res = ..." line
    of op's body with the range's node(s) replaced by the root(s) (treaps, treap pairs); else None"""
    if lang == "py":
        m = re.search(rf"    def {op}\(self, l, r\):(.*?)\n    def ", cls, re.S)
        if not m:
            return None
        line = re.search(r"^        res = (.+)$", m.group(1), re.M)
        if not line or not re.fullmatch(r"[\w.\[\]()+^&|\s]+", line.group(1)):
            return None
        expr, used = line.group(1), set(re.findall(r"\[(b|be|bo)\]", line.group(1)))
        if not used or set(re.findall(r"[A-Za-z_]\w*", re.sub(r"self\.\w+", "", expr))) - {"b", "be", "bo"}:
            return None  # (anything but the structure's arrays and the range's nodes: not a plain root read)
        for var in used:
            if not re.search(rf"{re.escape(ROOTS_PY[var])} = ", cls):
                return None
            expr = re.sub(rf"\[{var}\]", f"[{ROOTS_PY[var]}]", expr)
        return expr
    m = re.search(rf" {op}\((?:int|long long) l, (?:int|long long) r\)[^{{]*\{{(.*?)\n    \}}", cls, re.S)
    if not m:
        return None
    line = re.search(r"^        (?:[\w:<> ]+ )?res = (.+);$", m.group(1), re.M)
    if not line or not re.fullmatch(r"[\w.\[\]()+^&|\s]+", line.group(1)):
        return None
    expr, used = line.group(1), set(re.findall(r"nd\[(b|be|bo)\]", line.group(1)))
    if not used or set(re.findall(r"[A-Za-z_]\w*", re.sub(r"\.\w+", "", expr))) - {"nd", "b", "be", "bo"}:
        return None  # (anything but the node arrays and the range's nodes: not a plain root read)
    for var in used:
        if not re.search(rf"^    int (?:\w+(?: = \d+)?, )*{ROOTS_CPP[var]}\b", cls, re.M):
            return None
        expr = expr.replace(f"nd[{var}]", f"nd[{ROOTS_CPP[var]}]")
    return expr


def _aggregate_block(lang, op, name, word, cost, length, root=None):
    where = "read off the root" if root else f"{op}(0, n - 1)"
    body = root if root else (f"self.{op}(0, {length} - 1)" if lang == "py" else f"{op}(0, {length} - 1)")
    if lang == "py":
        return f'''    # O({cost}) -- {word} of the whole array a[0..n-1] ({where}); needs n >= 1, else raises IndexError
    def {name}(self):
        if {length} < 1:
            raise IndexError("{name}: needs n >= 1")
        return {body}
'''
    return f'''    // O({cost}) -- {word} of the whole array a[0..n-1] ({where}); needs n >= 1, else throws out_of_range
    auto {name}() {{
        if ({length} < 1) throw out_of_range("{name}: needs n >= 1");
        return {body};
    }}
'''


def _hash_all_block(lang, cost, length, root=None):
    if root:
        if lang == "py":
            return f'''    # O(1) -- hash of the whole array a[0..n-1], read off the root: the same base and mod as rangeHash (shared by every
    # structure this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if {length} < 1:
            raise IndexError("hashAll: needs n >= 1")
        return {root}
'''
        return f'''    // O(1) -- hash of the whole array a[0..n-1], read off the root: the same base and mod as rangeHash (shared by every
    // structure this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {{
        if ({length} < 1) throw out_of_range("hashAll: needs n >= 1");
        return {root};
    }}
'''
    if lang == "py":
        return f'''    # O({cost}) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    # this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if {length} < 1:
            raise IndexError("hashAll: needs n >= 1")
        return self.rangeHash(0, {length} - 1)
'''
    return f'''    // O({cost}) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    // this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {{
        if ({length} < 1) throw out_of_range("hashAll: needs n >= 1");
        return rangeHash(0, {length} - 1);
    }}
'''


def _pal_block(lang, cost, length):
    if lang == "py":
        return f'''    # O({cost}) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    # its radius, log N calls of isPalindrome; needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtI(self, i):
        n = {length}
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {{i}}, n = {{n}}")
        lo, hi = 0, min(i, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo, i + lo

    # O({cost}) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
    # range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    # needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        n = {length}
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {{i}}, n = {{n}}")
        lo, hi = 0, min(i + 1, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid + 1, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo + 1, i + lo
'''
    return f'''    // O({cost}) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    // its radius, log N calls of isPalindrome; needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtI(long long i) {{
        long long len = {length};
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        long long lo = 0, hi = min(i, len - 1 - i);
        while (lo < hi) {{
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid, i + mid)) lo = mid;
            else hi = mid - 1;
        }}
        return {{i - lo, i + lo}};
    }}

    // O({cost}) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
    // range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    // needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtIPlusOne(long long i) {{
        long long len = {length};
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        long long lo = 0, hi = min(i + 1, len - 1 - i);
        while (lo < hi) {{
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid + 1, i + mid)) lo = mid;
            else hi = mid - 1;
        }}
        return {{i - lo + 1, i + lo}};
    }}
'''


def add_derived_ops(text, lang):
    cm = "#" if lang == "py" else "//"
    m, costs = _header(text, cm)
    if not m:
        return text
    ops = set(m.group(1).split())
    sparse = bool(re.search(rf"^{re.escape(cm)}   layout: sparse$", text, re.M))
    wanted = []  # (op names, cost, block maker needing (lang, cost, length), needs)
    if {"cut", "pointGet", "size"} <= ops and "pop" not in ops:
        wanted.append((("pop", "popLeft"), _max_cost(costs["cut"], costs["pointGet"]), "pop", ("cut", "pointGet", "size")))
    if "rangeHash" in ops and "hashAll" not in ops and not sparse:
        wanted.append((("hashAll",), costs["rangeHash"], "hash", ("rangeHash",)))
    for op, (name, word) in AGGREGATES.items():
        if op in ops and name not in ops and not sparse:
            wanted.append(((name,), costs[op], ("agg", op, word), (op,)))
    if "isPalindrome" in ops and "longestPalCenteredAtI" not in ops and not sparse:
        wanted.append((("longestPalCenteredAtI", "longestPalCenteredAtIPlusOne"), _times_log(costs["isPalindrome"]), "pal", ("isPalindrome",)))
    if not wanted:
        return text
    added = set()
    final_cost = {}
    out, last = [], 0
    for s, e in _classes(text, lang):
        cls = text[s:e]
        for names, cost, kind, needs in wanted:
            if not all(_has(cls, lang, x) for x in needs):
                continue
            length = _length(cls, lang)
            if kind == "pop":
                block = _pop_block(lang, cost)
            elif length is None:
                continue
            elif kind == "hash":
                root = _root_hash(cls, lang)
                if root:
                    cost = "1"
                block = _hash_all_block(lang, cost, length, root)
            elif isinstance(kind, tuple):  # ("agg", the range op, its word)
                root = _root_aggregate(cls, lang, kind[1])
                if root:
                    cost = "1"
                block = _aggregate_block(lang, kind[1], names[0], kind[2], cost, length, root)
            else:
                block = _pal_block(lang, cost, length)
            cls = _insert(cls, lang, block)
            added.update(names)
            final_cost[names] = cost
        out.append(text[last:s])
        out.append(cls)
        last = e
    out.append(text[last:])
    text = "".join(out)
    if not added:
        return text
    text = text.replace(m.group(0), f"{cm} @operations: {' '.join(sorted(ops | added))}", 1)
    lines = "".join(f"{cm}   {op}: {final_cost.get(names, cost)}\n" for names, cost, _, _ in wanted for op in names if op in added)
    return re.sub(rf"^({re.escape(cm)}   build: )", lambda mm: lines + mm.group(1), text, count=1, flags=re.M)


OLD_PAL = ("longestPalCenteredAt", "longestPalCenteredBetween")


def remove_old_pal(text, lang):
    """text without the first-version longest-palindrome methods (length-returning, old names) and their header lines"""
    cm = "#" if lang == "py" else "//"
    m, _ = _header(text, cm)
    if not m or "longestPalCenteredAt " not in m.group(1) + " ":
        return text
    ops = [o for o in m.group(1).split() if o not in OLD_PAL]
    text = text.replace(m.group(0), f"{cm} @operations: {' '.join(ops)}", 1)
    text = re.sub(rf"^{re.escape(cm)}   (?:longestPalCenteredAt|longestPalCenteredBetween): .*\n", "", text, flags=re.M)
    if lang == "py":
        pat = r"    # O\([^\n]*\) -- length of the longest odd palindrome.*?def longestPalCenteredBetween.*?        return 2 \* lo\n\n?"
    else:
        pat = r"    // O\([^\n]*\) -- length of the longest odd palindrome.*?longestPalCenteredBetween\(long long i\).*?        return 2 \* lo;\n    \}\n\n?"
    text, k = re.subn(pat, "", text, flags=re.S)
    assert k >= 1, "old longest-palindrome block not found"
    return text


def remove_old_hash_all(text, lang):
    """text without the first-version hashAll (the rangeHash wrapper) and its header lines, so it can be re-added"""
    cm = "#" if lang == "py" else "//"
    m, _ = _header(text, cm)
    if not m or " hashAll " not in " " + m.group(1) + " ":
        return text
    if lang == "py":
        pat = r"    # O\([^\n]*\) -- hash of the whole array a\[0\.\.n-1\]: the same base and mod as rangeHash.*?        return self\.rangeHash\(0, [^\n]*\)\n\n?"
    else:
        pat = r"    // O\([^\n]*\) -- hash of the whole array a\[0\.\.n-1\]: the same base and mod as rangeHash.*?        return rangeHash\(0, [^\n]*\);\n    \}\n\n?"
    text, k = re.subn(pat, "", text, flags=re.S)
    if not k:
        return text  # (not the wrapper version: nothing to replace)
    ops = [o for o in m.group(1).split() if o != "hashAll"]
    text = text.replace(m.group(0), f"{cm} @operations: {' '.join(ops)}", 1)
    return re.sub(rf"^{re.escape(cm)}   hashAll: .*\n", "", text, flags=re.M)
