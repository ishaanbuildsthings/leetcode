"""gcd and capped-LCM multisets, made from the OR / AND ones gen_sets.py writes (run it first):

    python3 gen_sets_gcd_lcm.py

For each family (AVL, treap, splay, value tree, blocks) it writes <family>-with-[sums-]gcd[-minmax] (from the same
folder with or), ...-lcm... (from and) and ...-gcd-lcm... (from or-and): counts only or with sums, and with or without
the cached min / max, so 12 folders per family; template.py, template.cpp and fast.cpp in each. The shapes line
up: gcd's identity is 0 like OR's (gcd(0, x) = x), and the LCM's is 1 where AND's is -1, so every OR / AND combine
becomes a gcd / LCM one and the rest of the structure is untouched.

The LCM is capped: lcmOf... answers -1 once the LCM passes cap (a constructor argument, the largest T by default), so it
never overflows. Inside, -1 is the "too big" marker (the LCM sets take values >= 0): combining 0 with anything gives 0
(an LCM with a 0 is 0), else a -1 gives -1, else the LCM, or -1 past cap. Each tree node / block keeps the capped LCM of
just its own values, so removing the values that pushed it past cap makes the answer exact again.

A gcd or LCM is a Euclid run (O(log U)), so every op that recombines nodes, and every aggregate query, costs a log(U)
factor more than its OR / AND twin.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SETS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "sets")
FAMILIES = ["avl", "treap", "splay", "value-tree", "blocks"]
MODES = {"gcd": "or", "lcm": "and", "gcd-lcm": "or-and"}  # new folder suffix -> source folder suffix
# ops that change the multiset (they recombine nodes / blocks, each combine now a Euclid run)
UPDATE_OPS = {"add", "addCount", "remove", "removeCount", "removeAll", "removeInValRange", "pop", "popMin", "popMax"}
CAP_NOTE = ("lcmOf... answers -1 once the LCM passes cap, so it never overflows: cap is a constructor argument, the "
            "largest {T} by default; pass your own, e.g. {example}. Removing values is safe: every node keeps the "
            "capped LCM of just its own values, so once the values that pushed it past cap are gone, lcmOf... is "
            "exact again. Values must be >= 0. An empty selection gives the identity: gcd 0, LCM 1.")


def times_log_u(cost):
    """a cost string times log(U): log(N) -> log(N)*log(U), keeping the amortized / expected / ? suffix"""
    m = re.match(r"(.*?)((?: amortized| expected)?(?: \?)?)$", cost)
    body, suffix = m.group(1), m.group(2)
    if body == "1":
        return "log(U)" + suffix
    return "+".join(t + "*log(U)" for t in body.split("+")) + suffix


def split_top(expr, sep):
    """expr split on sep at bracket depth 0"""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(expr):
        c = expr[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if depth == 0 and expr.startswith(sep, i):
            parts.append(cur)
            cur = ""
            i += len(sep)
            continue
        cur += c
        i += 1
    parts.append(cur)
    return [p.strip() for p in parts]


def fold(parts, fn):
    acc = parts[0]
    for p in parts[1:]:
        acc = f"{fn}({acc}, {p})"
    return acc


# ------------------------------------------------------------------------------------------------ Python

def py_transform(text, mode):
    gcd, lcm = mode in ("gcd", "gcd-lcm"), mode in ("lcm", "gcd-lcm")
    # names: ops, helpers, fields (O -> G, A -> M; value tree o / a -> g / m; blocks bo / ba -> bg / bm)
    text = re.sub(r"\borOf", "gcdOf", text)
    text = re.sub(r"\bandOf", "lcmOf", text)
    text = re.sub(r"\b_or(Le|Ge|In)\b", r"_gcd\1", text)
    text = re.sub(r"\b_and(Le|Ge|In)\b", r"_lcm\1", text)
    text = re.sub(r"\bself\.O\b", "self.G", text)
    text = re.sub(r"\bself\.A\b", "self.M", text)
    text = re.sub(r'"O"', '"G"', text)
    text = re.sub(r'"A"', '"M"', text)
    text = re.sub(r"(__slots__ = \([^)]*)\)", lambda m: m.group(0).replace('"o"', '"g"').replace('"a"', '"m"'), text, count=1)
    text = re.sub(r"\bself\.o\b", "self.g", text)
    text = re.sub(r"\bself\.a\b", "self.m", text)
    text = re.sub(r"\boo\b", "gg", text)
    text = re.sub(r"\baa\b", "mm", text)
    text = re.sub(r"\bbo\b", "bg", text)
    text = re.sub(r"\bba\b", "bm", text)
    text = text.replace("from operator import and_, or_", "from operator import and_, or_  # (unused here)")
    out, method = [], ""
    for line in text.split("\n"):
        m = re.match(r"    def (\w+)\(", line)
        if m:
            method = m.group(1)
        line = py_line(line, method, gcd, lcm)
        out.append(line)
    text = "\n".join(out)
    text = text.replace("from operator import and_, or_  # (unused here)\n", "")
    if lcm:
        text = py_cap(text)
    return py_imports(text, lcm)


GCD_FIELDS = r"(self\.G\b|self\.g\b|\bgg\b|self\.bg\b)"
LCM_FIELDS = r"(self\.M\b|self\.m\b|\bmm\b|self\.bm\b)"


def py_line(line, method, gcd, lcm):
    if line.lstrip().startswith("#"):
        return line
    code, sep, comment = line.partition("  #")
    in_gcd = "gcd" in method.lower() or re.search(GCD_FIELDS, code)
    in_lcm = "lcm" in method.lower() or re.search(LCM_FIELDS, code)
    if in_gcd and gcd and "|" in code:
        code = py_combine(code, "|", "gcd")
    if in_lcm and lcm:
        code = code.replace("reduce(and_, ", "reduce(self._lc, ")
        code = re.sub(r"^(\s*)res = (K\[\w+\])$", r"\1res = self._lc(1, \2)", code)
        code = re.sub(r"(?<![\w\])])-1\b", "1", code)  # AND's identity (every bit) -> the LCM's (1)
        code = re.sub(r"\b(\w+) if (old \+ c > 0) else 1\b", r"self._lc(1, \1) if \2 else 1", code)
        code = re.sub(r"self\.bm\.append\((\w+)\)", r"self.bm.append(self._lc(1, \1))", code)
        if "&" in code and not re.search(r">> \w+ & 1|& -i|&= k - 1|& \(", code):
            code = py_combine(code, "&", "self._lc")
    if gcd:
        code = re.sub(r"reduce\(or_, ", "reduce(gcd, ", code)
    if gcd and in_gcd and not (lcm and in_lcm and "lcm" in method.lower()):
        code = re.sub(r"^(\s*)res = (K\[\w+\])$", r"\1res = gcd(0, \2)", code)  # (a range walk's first value: |v|)
    return code + sep + comment


def py_combine(code, op, fn):
    """an OR / AND line with op made into fn calls: X = a op b op c, res op= e, return a op b"""
    m = re.match(rf"^(\s*)(.+?) {re.escape(op)}= (.+)$", code)
    if m:
        ind, lhs, rhs = m.groups()
        return f"{ind}{lhs} = {fn}({lhs}, {fold(split_top(rhs, f' {op} '), fn)})"
    m = re.match(r"^(\s*)(return |.+? = )(.+)$", code)
    if m and f" {op} " in m.group(3):
        ind, head, rhs = m.groups()
        return f"{ind}{head}{fold(split_top(rhs, f' {op} '), fn)}"
    return code


def py_imports(text, lcm):
    if "gcd(" in text and "from math import gcd" not in text:
        # after the attribution / header comments, before the first import or class
        lines = text.split("\n")
        k = next(i for i, l in enumerate(lines) if l.startswith(("from ", "import ", "class ")))
        lines.insert(k, "from math import gcd")
        text = "\n".join(lines)
    return text


def py_cap(text):
    """the LCM's cap: a constructor argument, a slot, and the capped combine"""
    text = re.sub(r'__slots__ = \(([^)]*)\)', lambda m: f'__slots__ = ({m.group(1)}, "cap")', text, count=1)
    def ctor(m):
        args = m.group(1)
        return f"def __init__(self{', ' + args if args else ''}, cap=2**63 - 1):\n        self.cap = cap"
    text = re.sub(r"def __init__\(self(?:, )?([^)]*)\):", ctor, text, count=1)
    helper = '''
    def _lc(self, a, b):  # capped LCM: 0 if either is 0, else -1 if either is -1 (too big), else the LCM or -1 past cap
        if a == 0 or b == 0:
            return 0
        if a < 0 or b < 0:
            return -1
        r = a // gcd(a, b) * b
        return r if r <= self.cap else -1
'''
    k = text.rfind("\n    # ---- internals")
    if k == -1:
        k = len(text.rstrip("\n"))
        return text[:k] + "\n" + helper.rstrip("\n") + "\n" + text[k:]
    return text[:k] + "\n" + helper.rstrip("\n") + text[k:]


# ------------------------------------------------------------------------------------------------ C++

def cpp_transform(text, mode):
    gcd, lcm = mode in ("gcd", "gcd-lcm"), mode in ("lcm", "gcd-lcm")
    text = re.sub(r"\borOf", "gcdOf", text)
    text = re.sub(r"\bandOf", "lcmOf", text)
    text = re.sub(r"\bor(Le|Ge|In|Walk)\b", r"gcd\1", text)
    text = re.sub(r"\band(Le|Ge|In|Walk)\b", r"lcm\1", text)
    text = re.sub(r"\borv\b", "gcdv", text)
    text = re.sub(r"\bandv\b", "lcmv", text)
    text = re.sub(r"\bbo\b", "bg", text)
    text = re.sub(r"\bba\b", "bm", text)
    out, fn_name = [], ""
    for line in text.split("\n"):
        m = re.match(r"    (?:LEETCODE_NO_SANITIZE )?(?:[\w:<>,]+[&*]? )+(\w+)\(", line)
        if m and line.split("  //")[0].rstrip().endswith("{"):
            fn_name = m.group(1)
        out.append(cpp_line(line, fn_name, gcd, lcm))
    text = "\n".join(out)
    if lcm:
        text = cpp_cap(text)
    return text


C_GCD = r"(\.gcdv\b|\bbg\b)"
C_LCM = r"(\.lcmv\b|\bbm\b)"


def cpp_line(line, fn, gcd, lcm):
    if line.lstrip().startswith("//"):
        return line
    code, sep, comment = line.partition("  //")
    in_gcd = "gcd" in fn.lower() or re.search(C_GCD, code)
    in_lcm = "lcm" in fn.lower() or re.search(C_LCM, code)
    if gcd:
        code = code.replace("T(0), bit_or<T>())", "T(0), [](T a, T b) { return gcd(a, b); })")
    if lcm:
        code = code.replace("~T(0), bit_and<T>())", "T(1), [this](T a, T b) { return lc(a, b); })")
        code = code.replace("T lcmv = ~T(0);", "T lcmv = 1;")
        code = code.replace("~T(0)", "T(1)")
        code = re.sub(r"pres > 0 \? x : T\(1\)", "pres > 0 ? lc(T(1), x) : T(1)", code)
        code = re.sub(r"\bbm\.push_back\((\w+)\)", r"bm.push_back(lc(T(1), \1))", code)
    if gcd and in_gcd and "|" in code:
        code = cpp_combine(code, "|", "gcd")
    if gcd and "gcd" in fn.lower():
        code = re.sub(r"T res = (pool\[\w+\]\.key);", r"T res = gcd(T(0), \1);", code)  # (a range walk's first value)
    if lcm and "lcm" in fn.lower():
        code = re.sub(r"T res = (pool\[\w+\]\.key);", r"T res = lc(T(1), \1);", code)
    if lcm and in_lcm and "&" in code and not re.search(r"& -i|&= k - 1|const \w|&\w|\w& |\(&|i & ", code):
        code = cpp_combine(code, "&", "lc")
    return code + sep + comment


def cpp_combine(code, op, fn):
    """an OR / AND statement with op made into fn calls; handles "res op= e, t = ...;" comma statements"""
    def peel(stmt):  # a leading "for (...) ", "if (...) " or "else " (balanced parentheses), and the rest
        m = re.match(r"^(\s*)(?:else |(for|if) \()", stmt)
        if not m:
            return "", stmt
        if not m.group(2):
            return stmt[:m.end()], stmt[m.end():]
        depth, i = 0, stmt.index("(", m.start(2))
        for j in range(i, len(stmt)):
            depth += stmt[j] == "("
            depth -= stmt[j] == ")"
            if depth == 0:
                return stmt[:j + 2], stmt[j + 2:]
        return "", stmt

    def comb_assign(stmt):
        pre, rest = peel(stmt)
        if pre:
            return pre + comb_assign(rest)
        m = re.match(rf"^(\s*)(.+?) {re.escape(op)}= (.+)$", stmt)
        if m:
            pre, lhs, rhs = m.groups()
            return f"{pre}{lhs} = {fn}({lhs}, {fold(split_top(rhs, f' {op} '), fn)})"
        m = re.match(r"^(\s*(?:return |.+? = ))(.+)$", stmt)
        if m and f" {op} " in m.group(2):
            return m.group(1) + fold(split_top(m.group(2), f" {op} "), fn)
        return stmt
    body = code.rstrip()
    end = ";" if body.endswith(";") else ""
    if end:
        body = body[:-1]
    parts = split_top(body, ", ")
    if len(parts) > 1 and re.search(rf"{re.escape(op)}=", parts[0]):  # "res |= a | b, t = r" (a comma statement)
        lead = re.match(r"^\s*", code).group(0)
        first = comb_assign(lead + parts[0].lstrip()) if not parts[0].startswith(lead) else comb_assign(parts[0])
        return first + ", " + ", ".join(parts[1:]) + end
    return comb_assign(body) + end


def cpp_cap(text):
    """the LCM's cap: a member, a constructor argument and the capped combine"""
    name = re.findall(r"^template <typename T>\nstruct (\w+) \{", text, re.M)[-1]  # (fast.cpp has helper structs first)
    def ctor(mm):
        lead, args, init, body = mm.group(1) or "", mm.group(2), mm.group(3) or "", mm.group(4)
        args = (args + ", " if args else "") + "T cap = numeric_limits<T>::max()"
        init = (init + ", " if init else " : ") + "cap(cap)"
        return f"    {lead or ('explicit ' if ',' not in args else '')}{name}({args}){init} {{{body}}}"
    text, k = re.subn(rf"^    (explicit )?{name}\(([^)]*)\)((?: : [^{{]*?)?) \{{(.*)\}}$", ctor, text, count=1, flags=re.M)
    assert k == 1, f"{name}: constructor not found"
    helper = """
    T cap;  // lcmOf... is -1 past it
    T lc(T a, T b) const {  // capped LCM: 0 if either is 0, else -1 if either is -1 (too big), else the LCM or -1 past cap
        if (a == 0 || b == 0) return 0;
        if (a < 0 || b < 0) return -1;
        T r;
        if (__builtin_mul_overflow(a / gcd(a, b), b, &r) || r > cap) return -1;
        return r;
    }
"""
    k = text.find("\n", text.find(f"struct {name} {{")) + 1
    return text[:k] + helper.lstrip("\n") + text[k:]


# ------------------------------------------------------------------------------------------------ headers and docs

def header_and_docs(text, mode, cm, folder, src_folder, cls):
    text = text.replace(src_folder + "/", folder + "/")
    lines = text.split("\n")
    out = []
    for line in lines:
        m = re.match(rf"^{re.escape(cm)} @operations: (.*)$", line)
        if m:
            ops = sorted(re.sub(r"^orOf", "gcdOf", re.sub(r"^andOf", "lcmOf", o)) for o in m.group(1).split())
            line = f"{cm} @operations: {' '.join(ops)}"
        m = re.match(rf"^({re.escape(cm)}   )(\w+): (.+)$", line)
        if m and m.group(2) != "build" and not line.startswith(f"{cm}   node") and m.group(2) not in ("layout", "tags", "other", "note"):
            op = m.group(2)
            cost = m.group(3)
            if op in UPDATE_OPS or op.startswith(("gcdOf", "lcmOf")):
                if not (op.endswith("OfAll") and cost == "1"):
                    cost = times_log_u(cost)
            line = f"{m.group(1)}{op}: {cost}"
        out.append(line)
    text = "\n".join(out)
    # memory field names
    text = re.sub(rf"^({re.escape(cm)}   (?:node|other): .*)$",
                  lambda mm: mm.group(1).replace("or[", "gcd[").replace("and[", "lcm[").replace(" o[", " g[")
                  .replace(" a[", " m[").replace("bo[", "bg[").replace("ba[", "bm["), text, flags=re.M)
    # words
    reps = [("bitwise OR", "gcd"), ("bitwise AND", "LCM"), ("-1 (every bit set)", "1"), ("(returns -1, every bit set)", "(returns 1)"),
            ("returns -1, every bit\n", "returns 1,\n"), ("OR of the values", "gcd of the values"),
            ("AND of the values below (the empty tree's: every bit)", "capped LCM of the values below (the empty tree's: 1)"),
            ("AND of the values", "capped LCM of the values"), ("the OR / AND up its path", "the gcd / LCM up its path"),
            ("OR / AND", "gcd / LCM"), ("per block: OR of its values", "per block: gcd of its values"),
            ("per block: AND of its values", "per block: capped LCM of its values"),
            ("per block OR of its values", "per block gcd of its values"), ("per block AND of its values", "per block capped LCM of its values"),
            ("copies, OR, AND below", "copies, gcd, LCM below")]
    for a, b in reps:
        text = text.replace(a, b)
    # "(returns -1, every bit set)" wrapped across two comment lines
    text = re.sub(r"\(returns -1,(\n\s*(?:#|//) )every bit set\), ", r"(returns 1),\1", text)
    # the remaining OR / AND words, in comments only
    def words(seg):
        return re.sub(r"\bAND\b", "LCM", re.sub(r"\bOR\b", "gcd", seg))
    out = []
    for line in text.split("\n"):
        st = line.lstrip()
        if st.startswith(cm):
            line = words(line)
        elif f"  {cm} " in line:
            code, _, com = line.partition(f"  {cm} ")
            line = f"{code}  {cm} {words(com)}"
        out.append(line)
    text = "\n".join(out)
    if "lcm" in mode:
        T = "T (2^63 - 1 for long long)" if cm == "//" else "value (2**63 - 1)"
        args = {"value-tree": ("lo, hi, ", "")}.get(folder.split("-with-")[0], ("", ""))
        example = (f"{cls}<long long> s({args[0]}1000000000LL)" if cm == "//" else f"{cls}({args[0]}cap=10**9)")
        note = CAP_NOTE.format(T=T, example=example)
        import textwrap
        block = "\n".join(textwrap.wrap(note, 117, initial_indent=f"{cm} ", subsequent_indent=f"{cm} "))
        # after the @ header block (the first line that isn't an @ / indented tag line)
        ls = text.split("\n")
        k = next(i for i, l in enumerate(ls) if l.startswith(f"{cm} @operations"))
        while k < len(ls) and re.match(rf"^{re.escape(cm)} ( |@)", ls[k]):
            k += 1
        ls.insert(k, block)
        text = "\n".join(ls)
    return method_costs(text, cm)


def method_costs(text, cm):
    """each method comment's O(...) to match the header: a log U more on the ops that recombine or aggregate"""
    lines = text.split("\n")
    last = None
    for i, l in enumerate(lines):
        if l.startswith(f"    {cm} O("):
            last = i
        m = re.match(r"    (?:def |(?:LEETCODE_NO_SANITIZE )?(?:[\w:<>,]+[&*]? )+)(\w+)\(", l)
        if m and last is not None and not l.lstrip().startswith(cm):
            name = m.group(1)
            if name in UPDATE_OPS or name.startswith(("gcdOf", "lcmOf")):
                c = re.match(rf"    {re.escape(cm)} O\((.*?)\) -- ", lines[last])
                if c and not (name.endswith("OfAll") and c.group(1) == "1"):
                    cost = c.group(1)
                    new = "logU" if cost == "1" else re.sub(r"^(\S+)", r"\1 * logU", cost)
                    lines[last] = lines[last].replace(f"O({cost}) -- ", f"O({new}) -- ", 1)
            if name.startswith("lcmOf"):
                lines[last] = lines[last].replace("-- LCM of", "-- LCM (-1 once it passes cap) of", 1)
            last = None
    return "\n".join(lines)


def main():
    made = 0
    variants = [(fam, mode, src, sums, mm) for fam in FAMILIES for mode, src in MODES.items() for sums in ("", "sums-")
                for mm in ("", "-minmax")]
    for fam, mode, src, sums, mm in variants:
            sfolder, folder = f"{fam}-with-{sums}{src}{mm}", f"{fam}-with-{sums}{mode}{mm}"
            spath, path = os.path.join(SETS, sfolder), os.path.join(SETS, folder)
            if not os.path.isdir(spath):
                print("missing", sfolder)
                continue
            os.makedirs(path, exist_ok=True)
            for name in ("template.py", "template.cpp", "fast.cpp"):
                src_file = os.path.join(spath, name)
                if not os.path.exists(src_file):
                    continue
                text = open(src_file).read()
                py = name.endswith(".py")
                cls = re.search(r"^class (\w+)" if py else r"^struct (\w+) \{", text, re.M).group(1)
                text = py_transform(text, mode) if py else cpp_transform(text, mode)
                text = header_and_docs(text, mode, "#" if py else "//", folder, sfolder, cls)
                open(os.path.join(path, name), "w").write(text)
            made += 1
    print(made, "folders written")


if __name__ == "__main__":
    main()
