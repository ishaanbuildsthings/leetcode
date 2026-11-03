"""Up-front argument checks on every public op that takes an index, a range or a position (BOUNDS_CHECKS.md).

    add_bounds(text, lang)    # called by note_lang.write_template on every file it writes

A bad index must fail at once and say what was expected: a treap walk with i >= size() reaches node 0 (the empty tree)
and loops there, an array read past the end returns garbage. Each op named in the file's @operations gets one O(1)
check at the top, chosen by its parameters, and its doc comment says the rule:

    point ops (i)                           0 <= i < n
    (l, r, ...)                             0 <= l <= r < n
    rangesEqual(l1, r1, l2, r2)             both ranges
    insertAt / insertCopiesAt / paste (i)   0 <= i <= n
    split(k)                                0 <= k <= n

n is size() where the class has one, else its n member; a sparse class (bounds lo / hi or first / last) checks
lo <= i <= hi instead. Python raises IndexError (with the values), C++ throws out_of_range. Methods with default
arguments, and ops already checked, are left as they are (it runs again on its own output without change).
"""
import re

POINT = {"pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"}
INSERT = {"insertAt", "insertCopiesAt", "paste"}


def _ops(text):
    m = re.search(r"^(?:#|//) @operations: (.*)$", text, re.M)
    return set(m.group(1).split()) if m else set()


POINT_NAMES = ("i", "index", "pos", "idx", "p")
RANGE_NAMES = (("l", "r"), ("ql", "qr"), ("left", "right"))


def _rule(op, params):
    """(kind, the parameter names it checks) for an op with these parameter names, or None"""
    if op in POINT and params[:1] and params[0] in POINT_NAMES:
        return "point", params[:1]
    if op in INSERT and params[:1] == ["i"]:
        return "insert", ["i"]
    if op == "split" and params == ["k"]:
        return "insert", ["k"]
    if params[:4] == ["l1", "r1", "l2", "r2"]:
        return "ranges", params[:4]
    if tuple(params[:2]) in RANGE_NAMES:
        return "range", params[:2]
    return None


def _bounds(cls_text, lang, sparse):
    """how this class measures valid indices: ("dense", n expression, n's name in messages) or ("sparse", lo, hi)"""
    if lang == "py":
        for lo, hi in (("first", "last"), ("lo", "hi")):
            if sparse and re.search(rf"self\.{lo}\b", cls_text) and re.search(rf"self\.{hi}\b", cls_text):
                return ("sparse", f"self.{lo}", f"self.{hi}")
        if re.search(r"^    def size\(self\):", cls_text, re.M):
            return ("dense", "self.size()", "size()")
        if re.search(r"self\.n = ", cls_text):
            return ("dense", "self.n", "n")
        return None
    for lo, hi in (("first", "last"), ("lo", "hi")):
        if sparse and re.search(rf"^    (?:const )?(?:long long|int|T) {lo}, {hi}\b", cls_text, re.M):
            return ("sparse", lo, hi)
    if re.search(r"^    (?:int|long long) size\(\) const", cls_text, re.M):
        return ("dense", "size()", "size()")
    if re.search(r"^    (?:int|long long|size_t) n\b", cls_text, re.M):
        return ("dense", "n", "n")
    return None


def _conds(kind, names, b, lang):
    """(the failing condition, the rule in words), in the method's own parameter names"""
    py = lang == "py"
    if b[0] == "sparse":
        lo, hi = b[1], b[2]
        if kind == "point":
            i = names[0]
            return (f"not {lo} <= {i} <= {hi}" if py else f"{i} < {lo} || {i} > {hi}"), f"lo <= {i} <= hi"
        if kind == "range":
            l, r = names
            return (f"not {lo} <= {l} <= {r} <= {hi}" if py else f"{l} < {lo} || {l} > {r} || {r} > {hi}"), f"lo <= {l} <= {r} <= hi"
        if kind == "ranges":
            l1, r1, l2, r2 = names
            return ((f"not ({lo} <= {l1} <= {r1} <= {hi} and {lo} <= {l2} <= {r2} <= {hi})" if py else
                     f"{l1} < {lo} || {l1} > {r1} || {r1} > {hi} || {l2} < {lo} || {l2} > {r2} || {r2} > {hi}"),
                    f"lo <= {l1} <= {r1} <= hi and lo <= {l2} <= {r2} <= hi")
        return None
    n, word = b[1], b[2]
    if kind == "point":
        i = names[0]
        return (f"not 0 <= {i} < {n}" if py else f"{i} < 0 || {i} >= {n}"), f"0 <= {i} < {word}"
    if kind == "insert":
        v = names[0]
        return (f"not 0 <= {v} <= {n}" if py else f"{v} < 0 || {v} > {n}"), f"0 <= {v} <= {word}"
    if kind == "range":
        l, r = names
        return (f"not 0 <= {l} <= {r} < {n}" if py else f"{l} < 0 || {l} > {r} || {r} >= {n}"), f"0 <= {l} <= {r} < {word}"
    l1, r1, l2, r2 = names
    return ((f"not (0 <= {l1} <= {r1} < {n} and 0 <= {l2} <= {r2} < {n})" if py else
             f"{l1} < 0 || {l1} > {r1} || {r1} >= {n} || {l2} < 0 || {l2} > {r2} || {r2} >= {n}"),
            f"0 <= {l1} <= {r1} < {word} and 0 <= {l2} <= {r2} < {word}")


def _doc(lines, rule, lang, width=120):
    """the doc comment lines with '; needs <rule>, else <error>' appended (re-wrapped at width)"""
    cm = lines[0][:len(lines[0]) - len(lines[0].lstrip())] + ("#" if lang == "py" else "//")
    words = " ".join(ln.strip()[len(cm.strip()):].strip() for ln in lines)
    err = "IndexError" if lang == "py" else "throws out_of_range"
    keep = rule.replace(" ", "\u00a0")  # (the rule stays on one line)
    if rule in words:  # (the doc states it already: say what happens outside it)
        words = words.replace(rule, f"needs {keep}, else {err}", 1)
    elif f", else {err}" in words and "needs " in words:  # (a rule on other arguments already: one "needs" for both)
        k = words.rindex("needs ", 0, words.index(f", else {err}"))
        words = words[:k] + f"needs {keep} and " + words[k + len("needs "):]
    else:
        words += f"; needs {keep}, else {err}"
    out, cur = [], cm
    for w in words.split(" "):
        if len(cur) + 1 + len(w) > width - 2 and cur != cm:
            out.append(cur)
            cur = cm
        cur += " " + w
    return [x.replace("\u00a0", " ") for x in out + [cur]]


def _classes(text, lang):
    """(start, end) of each top-level class / struct"""
    pat = r"^class \w+" if lang == "py" else r"^(?:template <[^>]*>\n)?struct \w+"
    starts = [m.start() for m in re.finditer(pat, text, re.M)]
    return [(s, starts[k + 1] if k + 1 < len(starts) else len(text)) for k, s in enumerate(starts)]


def add_bounds(text, lang):
    ops = _ops(text)
    if not ops:
        return text
    sparse = bool(re.search(r"^(?:#|//)   layout: sparse$", text, re.M))  # (a dynamic tree over [lo, hi])
    out, last = [], 0
    for s, e in _classes(text, lang):
        cls = text[s:e]
        b = _bounds(cls, lang, sparse)
        if b is None:
            continue
        cls = (_py_class if lang == "py" else _cpp_class)(cls, ops, b)
        out.append(text[last:s] + cls)
        last = e
    return "".join(out) + text[last:]


def _py_class(cls, ops, b):
    lines, out, k = cls.split("\n"), [], 0
    while k < len(lines):
        m = re.match(r"^    def (\w+)\(self(?:, ([^)]*))?\):( .+)?$", lines[k])
        if not m or m.group(1) not in ops or (m.group(2) and "=" in m.group(2)):
            out.append(lines[k])
            k += 1
            continue
        op, params = m.group(1), [p.strip() for p in (m.group(2) or "").split(",") if p.strip()]
        r = _rule(op, params)
        doc_start = len(out)
        while doc_start > 0 and out[doc_start - 1].startswith("    # "):
            doc_start -= 1
        body = "\n".join(lines[k + 1:k + 5])
        cond = _conds(*r, b, "py") if r else None
        if not cond or not out[doc_start:] or f'IndexError(f"{op}: needs {cond[1]},' in body:
            out.append(lines[k])
            k += 1
            continue
        fail, rule = cond
        one = m.group(3)  # (a one-line def: its statement goes on a line of its own)
        out[doc_start:] = _doc(out[doc_start:], rule, "py")
        got = ", ".join(f"{v} = {{{v}}}" for v in r[1]) + (f", n = {{{b[1]}}}" if b[0] == "dense" else "")
        head = lines[k][:len(lines[k]) - len(one)] if one else lines[k]
        out += [head, f"        if {fail}:"] + raise_lines(op, rule, got) + (["        " + one.strip()] if one else [])
        k += 1
    return "\n".join(out)


def raise_lines(op, rule, got, width=120):
    """the Python raise, its message split after "got" when the line would pass width"""
    one = f'            raise IndexError(f"{op}: needs {rule}, got {got}")'
    if len(one) <= width:
        return [one]
    return [f'            raise IndexError(f"{op}: needs {rule}, got "', f'                             f"{got}")']


def _cpp_class(cls, ops, b):
    lines, out, k = cls.split("\n"), [], 0
    sig = re.compile(r"^    (?:[\w:<>, *&]+?\s+)?(\w+)\(([^)]*)\)( const)? \{(.*)$")
    while k < len(lines):
        first = []  # (a signature wrapped over two lines: its first line)
        m = sig.match(lines[k])
        if not m and lines[k].startswith("    ") and lines[k].endswith(",") and k + 1 < len(lines):
            m2 = sig.match(lines[k] + " " + lines[k + 1].strip())
            if m2 and m2.group(1) in ops:
                first = [lines[k]]
                k += 1
                m = sig.match("    " + lines[k].strip())
        # (skipped: defaults, and int& out-parameters, which mark an internal helper of the same name)
        if not m or m.group(1) not in ops or "=" in m.group(2) or re.search(r"\bint ?&", m.group(2)):
            out += first + [lines[k]]
            k += 1
            continue
        op = m.group(1)
        params = [p.strip().split()[-1] for p in m.group(2).split(",") if p.strip()]
        r = _rule(op, params)
        doc_start = len(out)
        while doc_start > 0 and out[doc_start - 1].startswith("    // "):
            doc_start -= 1
        rest = m.group(4).strip()
        nxt = "\n".join(lines[k + 1:k + 4])
        cond = _conds(*r, b, "cpp") if r else None
        if not cond or not out[doc_start:] or f'throw out_of_range("{op}: needs {cond[1]}")' in (rest + nxt):
            out += first + [lines[k]]
            k += 1
            continue
        fail, rule = cond
        out[doc_start:] = _doc(out[doc_start:], rule, "cpp")
        check = f'        if ({fail}) throw out_of_range("{op}: needs {rule}");'
        if len(check) > 120:
            check = f"        if ({fail})\n            throw out_of_range(\"{op}: needs {rule}\");"
        head = lines[k][:len(lines[k]) - len(m.group(4))].rstrip()  # (through the "{")
        out += first
        if rest:  # a one-line body: "{ stmt; }" -> its own lines
            assert rest.endswith("}"), lines[k]
            out += [head, check, "        " + rest[:-1].strip(), "    }"]
        else:
            out += [head, check]
        k += 1
    return "\n".join(out)
