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
    """(line, type, [(name, init)], comment) for each node-array member line"""
    out = []
    for m in re.finditer(r"^    static inline vector<(.+?)> (.+?);([ \t]*//[^\n]*)?\n", text, re.M):
        items = [x.strip() for x in _split_top(m.group(2))]
        if not all("{" in x for x in items):
            continue  # (a free list: no initial value)
        out.append((m.group(0), m.group(1), [(x[:x.index("{")], x[x.index("{") + 1:-1]) for x in items], m.group(3) or ""))
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
    """a[e] -> vec[e].a for every node field a (field_vec: field -> its node vector), inner brackets first"""
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
        inner = _rewrite(text[m.end():j - 1], field_vec)
        out.append(f"{field_vec[m.group(1)]}[{inner}].{m.group(1)}")
        i = j
    return "".join(out)


def _creations(text, field_vec, structs):
    """statements made of push_back calls on node fields -> one Node per vector, built and pushed"""
    fields = "|".join(sorted(map(re.escape, field_vec), key=len, reverse=True))
    stmt = re.compile(rf"^([ \t]+)((?:(?:{fields})\.push_back\(.*?\)|[^;\n]*?)(?:, (?:(?:{fields})\.push_back\(.*?\)|[^;\n]*?))*);[ \t]*\n", re.M)
    lines = text.split("\n")
    out, k = [], 0
    while k < len(lines):
        ln = lines[k]
        m = re.match(rf"^([ \t]+)(.*\b(?:{fields})\.push_back\(.*);\s*$", ln)
        if not m:
            out.append(ln)
            k += 1
            continue
        ind = m.group(1)
        block = []  # consecutive push_back statements (they make one node)
        while k < len(lines) and re.match(rf"^{ind}(.*\b(?:{fields})\.push_back\(.*);\s*$", lines[k]):
            block.append(re.match(rf"^{ind}(.*);\s*$", lines[k]).group(1))
            k += 1
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
            body = ", ".join(f"n.{f} = {e}" for f, e in assigns)
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
    if not decls:
        return text
    allf = [(n, t, i, cm) for _, t, items, cm in decls for n, i in items]
    if groups is None:
        groups = [("Node", "nd", [n for n, *_ in allf])]
    field_vec, structs = {}, {}
    for sname, vec, names in groups:
        structs[vec] = sname
        for n in names:
            field_vec[n] = vec
    # the structs, placed where the first node array was
    blocks = []
    for sname, vec, names in groups:
        fl = [x for x in allf if x[0] in names]
        fl.sort(key=lambda x: SIZE_ORDER.index(x[1]) if x[1] in SIZE_ORDER else 3)
        body = "".join(f"        {t} {n} = {i or t + '()'};\n" for n, t, i, _ in fl)
        blocks.append(f"    struct {sname} {{  // one node's fields together: a walk reads them at once (one cache line)\n{body}    }};\n"
                      f"    static inline vector<{sname}> {vec}{{{sname}{{}}}};  // node 0 = the empty tree\n")
    first = text.index(decls[0][0])
    for line, *_ in decls:
        text = text.replace(line, "", 1)
    text = text[:first] + "".join(blocks) + text[first:]
    text = _creations(text, field_vec, structs)
    for n, vec in field_vec.items():
        text = re.sub(rf"(?<![A-Za-z0-9_.>]){re.escape(n)}\.size\(\)", f"{vec}.size()", text)
    head, sep, rest = text.partition("struct Node {") if groups[0][0] == "Node" else ("", "", text)
    return _rewrite(text, field_vec)
