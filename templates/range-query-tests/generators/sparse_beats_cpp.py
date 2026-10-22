"""C++ half of sparse_beats.py: turns a dense beats struct into a sparse one over [lo, hi] (see sparse_beats.py)."""
import re

# A block of k zeros, per dense struct: the Node it is (node-struct style), or each per-node array's value (flat style).
ZERO_NODE = {
    "BeatsChminChmax": "Node{0, NEG_INF, 0, POS_INF, 0, 0, 0, 0, k, k, k, S(0), false}",
    "BeatsChmax": "Node{0, INF, 0, 0, 0, k, k, S(0), false}",
    "BeatsChmin": "Node{0, INF, 0, 0, 0, k, k, S(0), false}",
    "BeatsGcd": "Node{0, NEG_INF, 0, POS_INF, 0, 0, k, k, S(0)}",
    "BeatsChminChmaxNoAdd": "Node{0, NEG_INF, 0, POS_INF, k, k, S(0)}",
    "ChmaxSumBeats": "Node{0, SENT, k, S(0)}",
    "ChminSumBeats": "Node{0, SENT, k, S(0)}",
}
ZERO_FLAT = {
    "BitBeats": {"mx": "0", "mn": "0", "andAll": "0", "orAll": "0", "tagAnd": "FULL", "tagXor": "0", "tot": "0"},
    "ShrinkSeg": {"mx": "0", "mn": "0", "tot": "0"},
    "ShrinkTree": {"mx": "0", "tot": "0"},
}
INDEX_PARAMS = r"tl|tr|ql|qr|l|r|pos|p|sz|len|length|k"


def matching_brace(text, start):
    """Index just past the } matching the first { at or after start."""
    depth, k = 0, text.index("{", start)
    while True:
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1


def convert_cpp(folder, src):
    m = re.search(r"^template <typename T>\nstruct (\w+) \{", src, re.M)
    old = m.group(1)
    name = "Sparse" + old
    flat = old in ZERO_FLAT
    pre, body = src[:m.start()], src[m.start():]
    body = body.replace(f"struct {old} {{", f"struct {name} {{", 1)

    # storage: a shared pool, with children and lengths
    body = re.sub(r"^    int n;\n", "", body, count=1, flags=re.M)
    pool_extra = ("    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)\n"
                  "    static inline vector<long long> ln{0};   // how many positions each node covers\n"
                  "    long long lo, hi;\n    int root;\n")
    if flat:
        arrays = []

        def make_static(mm):
            typ, names = mm.group(1), [x.strip() for x in mm.group(2).split(",")]
            typ = "long long" if typ == "int" else typ
            arrays.extend(names)
            return "".join(f"    static inline vector<{typ}> {x} = vector<{typ}>(1);\n" for x in names)
        body = re.sub(r"^    vector<(\w+)> ([\w, ]+);\n", make_static, body, flags=re.M)
        # the pool's node 0 is a placeholder; the extra members go after the last array
        last = list(re.finditer(r"^    static inline vector<.*\n", body, re.M))[-1]
        body = body[:last.end()] + pool_extra + body[last.end():]
        zero = ZERO_FLAT[old]
        assert set(arrays) <= set(zero), (old, arrays)  # (gen_bitbeats.py's variants keep only some of the fields)
        push_zero = " ".join(f"{a}.push_back({zero[a]});" for a in arrays)
        resets = " ".join(f"{a}.resize(1);" for a in arrays)
        reserves = " ".join(f"{a}.reserve(nodes);" for a in arrays)
    else:
        body = re.sub(r"^    vector<Node> t;\n", "    static inline vector<Node> t{Node{}};  // node 0 is a placeholder\n" + pool_extra,
                      body, count=1, flags=re.M)
        # counts and sizes can exceed int
        node_m = re.search(r"struct Node \{.*?\};", body, re.S)
        body = body[:node_m.start()] + re.sub(r"\bint\b", "long long", node_m.group(0)) + body[node_m.end():]
        push_zero = f"t.push_back({ZERO_NODE[old]});"
        resets, reserves = "t.resize(1);", "t.reserve(nodes);"

    # constructor -> (lo, hi[, bits]); drop build
    cm = re.search(rf"^    explicit {old}\(const vector<T>& a(.*?)\)", body, re.M)
    extra = cm.group(1)
    ctor_start = body.rfind("\n", 0, cm.start()) + 1
    comment_start = ctor_start
    prev_line_start = body.rfind("\n", 0, ctor_start - 1) + 1
    if body[prev_line_start:ctor_start].strip().startswith("//"):
        comment_start = prev_line_start
    ctor_end = matching_brace(body, cm.end())
    full_init = ", FULL(T((T(1) << bits) - 1))" if "bits" in extra else ""
    new_ctor = f'''    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    {name}(long long lo, long long hi{extra}) : {"FULL(T((T(1) << bits) - 1)), " if full_init else ""}lo(lo), hi(hi) {{ root = node(hi - lo + 1); }}

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ {resets} Lc.resize(1); Rc.resize(1); ln.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ {reserves} Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }}

    // a fresh node: a block of k zeros
    int node(long long k) const {{  // const: it only touches the shared pool
        {push_zero}
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }}

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {{
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }}'''
    body = body[:comment_start] + new_ctor + body[ctor_end:]
    bm = re.search(r"^    void build\(", body, re.M)
    if bm:
        end = matching_brace(body, bm.start())
        body = body[:bm.start()] + body[end:].lstrip("\n")
        body = body.replace("    \n", "")

    # children
    body = re.sub(r"2 \* (\w+) \+ 1", r"Rc[\1]", body)
    body = re.sub(r"2 \* (\w+)", r"Lc[\1]", body)
    body = re.sub(r"(\w+) = Lc\[(\w+)\], (\w+) = \1 \+ 1", r"\1 = Lc[\2], \3 = Rc[\2]", body)

    # 64-bit positions, lengths and counts; overflow-safe midpoints
    body = body.replace("(tl + tr) / 2", "tl + (tr - tl) / 2")
    body = re.sub(r"\bint tm\b", "long long tm", body)
    out, node_var = [], None
    for line in body.split("\n"):
        fm = re.match(r"^    (?:static )?[\w<>:, ]+? (\w+)\((.*)\)( const)? \{", line)
        if fm and fm.group(1) not in ("node", "kids", name):
            fname, params = fm.group(1), fm.group(2)
            public = fname.startswith("point") or fname.startswith("range")
            if public:
                params2 = re.sub(r"\bint (\w+)", r"long long \1", params)
                node_var = None
            else:
                params2 = re.sub(rf"\bint ({INDEX_PARAMS})\b", r"long long \1", params)
                first = re.match(r"\s*int (\w+)", params)
                node_var = first.group(1) if first else None
            line = line.replace(f"({params})", f"({params2})", 1)
            if fname == "push" and node_var:
                out.append(line)
                out.append(f"        kids({node_var});")
                continue
        tm = re.match(r"^(\s+)(long long tm = |tm = )", line)
        if tm and node_var:
            out.append(f"{tm.group(1)}kids({node_var});")
        out.append(line)
    body = "\n".join(out)

    # public entry points: the whole range is [lo, hi]; there is always a root
    body = re.sub(r"\(1, 0, n - 1,", "(root, lo, hi,", body)
    body = re.sub(r" && n\b", "", body)
    body = re.sub(r" \|\| !n\b", "", body)
    body = re.sub(r"\bif \(n\) ", "", body)
    leftover = [ln for ln in body.split("\n") if re.search(r"(?<![\w.>])n\b(?!\w)", ln.split("//")[0])]
    assert not leftover, (old, leftover)
    intro = ("\n// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root\n"
             "// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)\n"
             f"// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every\n"
             f"// {name}<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with\n"
             "// children in Lc / Rc instead of at 2i / 2i + 1.\n")
    return intro + pre + body
