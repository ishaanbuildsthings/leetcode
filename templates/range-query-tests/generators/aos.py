"""C++ treaps: per-field node arrays -> one struct per node (array of structs), applied to generated text.

A treap step reads a node's priority, children, size and tags together, and nodes are visited in effectively random
order, so separate arrays cost one cache miss per field per node; a struct brings them in together. Python keeps
per-field lists (faster there).

    aosify(text)                  every `static inline vector<X> a{init}, ...;` member (with an initial value) becomes a
                                  field of `struct Node`, held in `static inline vector<Node> nd`
    aosify(text, groups)          several node kinds (sorted runs: value-tree nodes and run nodes): groups is a list of
                                  (struct name, vector name, field names)

Accesses `a[e]` become `nd[e].a` (nested brackets too), `a.size()` becomes `nd.size()`, and a creation step made of
`a.push_back(e)` calls becomes one Node built field by field and pushed. Members without an initial value (free lists)
stay vectors.
"""
import re

SIZE_ORDER = ["unsigned long long", "U64", "S", "long long", "T", "int", "char", "bool"]


def _decls(text):
    """(line, type, [(name, init or None)], comment) for each static vector member line (None: no initial value, e.g.
    a free list, which never becomes a node field)"""
    out = []
    for m in re.finditer(r"^    static inline vector<(.+?)> (.+?);([ \t]*//[^\n]*)?\n", text, re.M):
        items = [x.strip() for x in _split_top(m.group(2))]
        out.append((m.group(0), m.group(1), [(x[:x.index("{")], x[x.index("{") + 1:-1]) if "{" in x else (x, None) for x in items],
                    m.group(3) or ""))
    return out


def _split_top(s, sep=","):
    """s split at top-level sep (outside (), [], {})"""
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def _rewrite(text, field_vec):
    """a[e] -> vec[e].a for every node field a (field_vec: field -> its node vector), inner brackets first; // comments
    (the header's memory line names the arrays) are left as they are"""
    out = []
    for ln in text.split("\n"):
        k = ln.find("//")
        out.append(_rewrite_code(ln, field_vec) if k < 0 else _rewrite_code(ln[:k], field_vec) + ln[k:])
    return "\n".join(out)


def _rewrite_code(text, field_vec):
    names = sorted(field_vec, key=len, reverse=True)
    pat = re.compile(r"(?<![A-Za-z0-9_.>])(" + "|".join(map(re.escape, names)) + r")\[")
    out, i = [], 0
    while True:
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        j, depth = m.end(), 1
        while depth:
            depth += {"[": 1, "]": -1}.get(text[j], 0)
            j += 1
        inner = _rewrite_code(text[m.end():j - 1], field_vec)
        out.append(f"{field_vec[m.group(1)]}[{inner}].{m.group(1)}")
        i = j
    return "".join(out)


def _creations(text, field_vec, structs):
    """statements made of push_back calls on node fields -> one Node per vector, built and pushed"""
    fields = "|".join(sorted(map(re.escape, field_vec), key=len, reverse=True))
    stmt = re.compile(rf"^([ \t]+)((?:(?:{fields})\.push_back\(.*?\)|[^;\n]*?)(?:, (?:(?:{fields})\.push_back\(.*?\)|[^;\n]*?))*);[ \t]*\n", re.M)
    lines = []
    for ln in text.split("\n"):  # (a creation statement wrapped over lines, each ending in ",", becomes one line)
        if lines and ".push_back(" in lines[-1] and lines[-1].rstrip().endswith(","):
            lines[-1] = lines[-1].rstrip() + " " + ln.strip()
        else:
            lines.append(ln)
    out, k = [], 0
    while k < len(lines):
        ln = lines[k]
        m = re.match(rf"^([ \t]+)(.*\b(?:{fields})\.push_back\(.*);\s*$", ln)
        if not m:
            out.append(ln)
            k += 1
            continue
        ind = m.group(1)
        block, pre = [], []  # consecutive push_back statements (they make one node); local declarations between them
        while k < len(lines):  # go first (e.g. int w = ...; a value the fields after it use)
            if re.match(rf"^{ind}(.*\b(?:{fields})\.push_back\(.*);\s*$", lines[k]):
                block.append(re.match(rf"^{ind}(.*);\s*$", lines[k]).group(1))
            elif (block and k + 1 < len(lines) and re.match(rf"^{ind}(?:int|long long|T|S|auto) \w+ = [^;]*;\s*$", lines[k])
                  and re.search(rf"\b(?:{fields})\.push_back\(", lines[k + 1])):
                pre.append(lines[k])
            else:
                break
            k += 1
        out += pre
        sets, rest = {}, []
        for st in block:
            for part in _split_top(st):
                part = part.strip()
                pm = re.match(rf"^({fields})\.push_back\((.*)\)$", part)
                if pm:
                    sets.setdefault(field_vec[pm.group(1)], []).append((pm.group(1), pm.group(2)))
                else:
                    rest.append(part)
        for vec, assigns in sets.items():
            node = structs[vec]
            out.append(f"{ind}{node} n;")
            body = ", ".join(f"n.{f} = {_rewrite_code(e, field_vec)}" for f, e in assigns)
            out += _wrap(body, ind)
            out.append(f"{ind}{vec}.push_back(n);")
        for r in rest:
            out.append(f"{ind}{r};")
    return "\n".join(out)


def _wrap(body, ind):
    parts, lines, cur = _split_top(body), [], ""
    for p in parts:
        p = p.strip()
        if cur and len(ind) + len(cur) + len(p) + 3 > 119:
            lines.append(cur + ",")
            cur = ""
        cur += (", " if cur and not cur.endswith(",") else "") + p
    lines.append(cur + ";")
    return [ind + x for x in lines]


def aosify(text, groups=None):
    decls = _decls(text)
    allf = [(n, t, i, cm) for _, t, items, cm in decls for n, i in items if i is not None]
    if not allf:
        return text
    if groups is None:
        groups = [("Node", "nd", [n for n, *_ in allf])]
    field_vec, structs = {}, {}
    for sname, vec, names in groups:
        structs[vec] = sname
        for n in names:
            field_vec[n] = vec
    blocks = []  # (the structs go where the first node array was)
    for sname, vec, names in groups:
        fl = [x for x in allf if x[0] in names]
        fl.sort(key=lambda x: SIZE_ORDER.index(x[1]) if x[1] in SIZE_ORDER else 3)
        body = "".join(f"        {t} {n} = {i or t + '()'};\n" for n, t, i, _ in fl)
        blocks.append(f"    struct {sname} {{  // a node's fields side by side: a walk reads them together (faster than one array per field)\n{body}    }};\n"
                      f"    static inline vector<{sname}> {vec}{{{sname}{{}}}};  // node 0 = the empty tree\n")
    mark = "\x00STRUCTS\x00"
    for line, typ, items, cm in decls:  # (each line keeps the members that are not node fields)
        keep = [(n, i) for n, i in items if n not in field_vec]
        if len(keep) == len(items):
            continue
        new = f"    static inline vector<{typ}> {', '.join(n + ('{' + i + '}' if i is not None else '') for n, i in keep)};{cm}\n" if keep else ""
        text = text.replace(line, ("" if mark in text else mark) + new, 1)
    text = text.replace(mark, "".join(blocks))
    text = _creations(text, field_vec, structs)
    for n, vec in field_vec.items():
        text = re.sub(rf"(?<![A-Za-z0-9_.>]){re.escape(n)}\.size\(\)", f"{vec}.size()", text)
    return _fit(_rewrite(text, field_vec))


def _fit(text, width=120):
    """code lines the longer field accesses pushed past width: a trailing comment moves above the line, then the line
    breaks at its last top-level ", " that fits (the rest indented 4 more)"""
    out = []
    for ln in text.split("\n"):
        if len(ln) <= width or ln.lstrip().startswith(("//", "#")):
            out.append(ln)
            continue
        ind = ln[:len(ln) - len(ln.lstrip())]
        k = ln.find("  // ")
        if k > 0:
            out.append(ind + ln[k + 2:])
            ln = ln[:k]
        while len(ln) > width:
            depth, cut = 0, -1
            for i, ch in enumerate(ln):
                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif ch == "," and depth == 0 and i + 1 < width:
                    cut = i
            if cut < 0:
                break
            out.append(ln[:cut + 1])
            ln = ind + "    " + ln[cut + 1:].lstrip()
        out.append(ln)
    return "\n".join(out)


VALUE_NODE = ("Lc", "Rc", "cnt", "sm", "xr", "ov", "av", "fh", "bh")  # (sorted runs: a value-tree node)
NOT_NODE = ("pw", "gs")  # (sorted runs: B^k and 1 + B + ... + B^(k-1), indexed by length)


def aosify_runs(text):
    """sorted runs (sequence variants): value-tree nodes -> struct VNode in vn, run (treap) nodes -> struct Run in rn"""
    names = [n for _, _, items, _ in _decls(text) for n, i in items if i is not None]
    val = [n for n in names if n in VALUE_NODE]
    run = [n for n in names if n not in VALUE_NODE and n not in NOT_NODE]
    text = aosify(text, [("VNode", "vn", val), ("Run", "rn", run)])
    text = re.sub(r"(static inline vector<int> freeList;)  //.*", r"\1  // value nodes freed by merges, reused first", text)
    return re.sub(r"(static inline vector<unsigned long long> pw\{1\}, gs\{0\};)  //.*", r"\1  // B^k; 1 + B + ... + B^(k-1)", text)
