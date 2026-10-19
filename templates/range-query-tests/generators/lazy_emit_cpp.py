from lazy_common import *

CMP = {"min": "<", "max": ">"}
IDENT = {"min": "INF", "max": "NEG"}
FN = {"min": "min", "max": "max"}


def comps(tags):
    return "A" in tags, "B" in tags, "C" in tags


def cpp_clamp(fields, tags):
    A, B, C = comps(tags)
    name = class_name("clamp", fields, tags)
    arrs = [FIELD_ARR[f] for f in fields]
    tarr = tag_arrays("clamp", tags)
    ps = [p for p, on in (("hi", A), ("lo", B), ("c", C)) if on]
    sig = ", ".join(f"T {p}" for p in ps)
    params = ", ".join(ps)
    tag_ident = {"hi": "INF", "lo": "NEG", "add": "0"}

    def ev(var, src):
        out = []
        if C: out.append(f"{var} += {src('c')};")
        if B: out.append(f"{var} = max({var}, {src('lo')});")
        if A: out.append(f"{var} = min({var}, {src('hi')});")
        return " ".join(out)

    arg = lambda p: p  # noqa: E731
    own = lambda p: {"hi": "hi[p]", "lo": "lo[p]", "c": "add[p]"}[p]  # noqa: E731
    compose = []
    if A:
        compose.append(f"T nhi = {'hi[x] == INF ? INF : hi[x] + c' if C else 'hi[x]'};")
        if B: compose.append("nhi = std::max(nhi, loArg);")
        compose.append("hi[x] = std::min(nhi, hi);".replace("std::min(nhi, hi)", "std::min(nhi, hiArg)"))
    if B:
        compose.append(f"T nlo = {'lo[x] == NEG ? NEG : lo[x] + c' if C else 'lo[x]'};")
        compose.append("nlo = std::max(nlo, loArg);")
        if A: compose.append("nlo = std::min(nlo, hi[x]);")
        compose.append("lo[x] = nlo;")
    if C: compose.append("add[x] += c;")
    # member arrays are named hi / lo, so the apply parameters are hiArg / loArg
    sig = ", ".join({"hi": "T hiArg", "lo": "T loArg", "c": "T c"}[p] for p in ps)
    argname = lambda p: {"hi": "hiArg", "lo": "loArg", "c": "c"}[p]  # noqa: E731
    apply_fields = "\n".join(f"        {a}[x] = clampValue({a}[x], {', '.join(argname(p) for p in ps)});" for a in arrs)
    evsig = ", ".join({"hi": "T h", "lo": "T l", "c": "T c"}[p] for p in ps)
    evbody = ev("v", lambda p: {"hi": "h", "lo": "l", "c": "c"}[p])
    rebuild = "\n".join(f"            {a}[p] = clampValue(std::{FN[f]}({a}[2 * p], {a}[2 * p + 1]), {', '.join(own(p) for p in ps)});" for f, a in zip(fields, arrs))
    cond = " || ".join(f"{t}[x] != {tag_ident[t]}" for t in tarr)
    tagvals = ", ".join(f"{t}[x]" for t in tarr)
    reset = ", ".join(f"{t}[x] = {tag_ident[t]}" for t in tarr)

    def args(h, l, c):
        return ", ".join(v for v, on in ((h, A), (l, B), (c, C)) if on)
    upd = []
    if C: upd.append(("rangeAdd", "a[i] += v", args("INF", "NEG", "v")))
    if A: upd.append(("rangeChmin", "a[i] = min(a[i], v)", args("v", "NEG", "0")))
    if B: upd.append(("rangeChmax", "a[i] = max(a[i], v)", args("INF", "v", "0")))
    if A and B: upd.append(("rangeAssign", "a[i] = v", args("v", "v", "0")))
    upd_text = "".join(f"\n    // O(logN) -- {d} for i in [l, r]\n    void {m}(int l, int r, T v) {{ update(l, r, {a}); }}\n" for m, d, a in upd)
    queries = "".join(f'''
    // O(logN) -- {f} of a[l..r]
    T {FIELD_OP[f]}(int l, int r) {{
        l += n, r += n;
        push(l), push(r);
        T res = {IDENT[f]};
        for (r++; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) res = std::{FN[f]}(res, {FIELD_ARR[f]}[l++]);
            if (r & 1) res = std::{FN[f]}(res, {FIELD_ARR[f]}[--r]);
        }}
        return res;
    }}
''' for f in fields)
    tagdesc = {"C": "x + add", "A": "min(hi, x)", "B": "max(lo, x)", "AB": "min(hi, max(lo, x))", "AC": "min(hi, x + add)",
               "BC": "max(lo, x + add)", "ABC": "min(hi, max(lo, x + add))"}[tags]
    extra = "\n// Assign v is the clamp with hi = lo = v." if A and B else ""
    d = describe("clamp", fields, tags)
    return f'''
// {d[0].upper() + d[1:]}. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
// to my children". The tag is the map x -> {tagdesc}; these maps compose into the same form, and each is
// monotone, so it sends a node's min / max straight to the new min / max.{extra}
// An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.
// T: int, long long, ...; the INF / NEG sentinels in the tags are never shifted.
template <typename T>
struct {name} {{
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<T> {", ".join(arrs)};  // 2N: leaves are tree[n..2n)
    vector<T> {", ".join(tarr)};  // N: tags on internal nodes

    // O(N)
    explicit {name}(const vector<T>& a) : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {{
{chr(10).join(f"        {a}.assign(2 * n, {IDENT[f]});" for f, a in zip(fields, arrs))}
        for (int i = 0; i < n; i++) {" = ".join(f"{a}[n + i]" for a in arrs)} = a[i];
        for (int x = n - 1; x > 0; x--) {", ".join(f"{a}[x] = std::{FN[f]}({a}[2 * x], {a}[2 * x + 1])" for f, a in zip(fields, arrs))};
{chr(10).join(f"        {t}.assign(n, {tag_ident[t]});" for t in tarr)}
    }}

    static T clampValue(T v, {evsig}) {{ {evbody} return v; }}

    // apply the map to node x: to its values now, and (if internal) on top of its pending tag
    void apply(int x, {sig}) {{
{apply_fields}
        if (x < n) {{
{chr(10).join("            " + c for c in compose)}
        }}
    }}

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {{
        for (int s = h; s > 0; s--) {{
            int x = p >> s;
            if ({cond}) {{
                apply(2 * x, {tagvals}), apply(2 * x + 1, {tagvals});
                {reset};
            }}
        }}
    }}

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {{
        while (p > 1) {{
            p >>= 1;
{rebuild}
        }}
    }}

    void update(int l, int r, {", ".join(f"T {p}" for p in ps)}) {{
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {{
            if (i & 1) apply(i++, {params});
            if (j & 1) apply(--j, {params});
        }}
        rebuild(l0), rebuild(r0);
    }}
{upd_text}{queries}
    // O(logN) -- a[i]
    T pointGet(int i) {{
        push(i + n);
        return {arrs[0]}[i + n];
    }}

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {{
        int p = i + n;
        push(p);
        {" = ".join(f"{a}[p]" for a in arrs)} = v;
        rebuild(p);
    }}

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {{ pointAssign(i, pointGet(i) + delta); }}

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {{ if (v > pointGet(i)) pointAssign(i, v); }}

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {{ if (v < pointGet(i)) pointAssign(i, v); }}
}};
'''


def cpp_sum(fields, tags):
    ADD, ASG = "add" in tags, "assign" in tags
    name = class_name("sum", fields, tags)
    other = [f for f in fields if f != "sum"]
    oa = [FIELD_ARR[f] for f in other]
    tarr = tag_arrays("sum", tags)
    apply_add = ""
    if ADD:
        tagline = "if (x < n) (hasAsg[x] ? asg[x] : add[x]) += c;  // an add on an assign shifts the assigned value" if ASG else "if (x < n) add[x] += c;"
        apply_add = f'''
    // add c to every slot of node x, which covers k slots
    void applyAdd(int x, int k, T c) {{
        sm[x] += S(c) * k;
{"".join(f"        {a}[x] += c;{chr(10)}" for a in oa)}        {tagline}
    }}
'''
    apply_asg = ""
    if ASG:
        apply_asg = f'''
    // set every slot of node x (k slots) to v
    void applyAssign(int x, int k, T v) {{
        sm[x] = S(v) * k;
{"".join(f"        {a}[x] = v;{chr(10)}" for a in oa)}        if (x < n) hasAsg[x] = 1, asg[x] = v{", add[x] = 0" if ADD else ""};
    }}
'''
    push_lines = []
    if ASG:
        push_lines.append("            if (hasAsg[x]) applyAssign(2 * x, k, asg[x]), applyAssign(2 * x + 1, k, asg[x]), hasAsg[x] = 0;")
    if ADD:
        push_lines.append(f"            {'else if' if ASG else 'if'} (add[x]) applyAdd(2 * x, k, add[x]), applyAdd(2 * x + 1, k, add[x]), add[x] = 0;")
    rb = []
    if ASG:
        rb.append(f"            if (hasAsg[p]) {{\n                sm[p] = S(asg[p]) * k;\n{''.join(f'                {a}[p] = asg[p];{chr(10)}' for a in oa)}                continue;\n            }}")
    rb.append(f"            sm[p] = sm[2 * p] + sm[2 * p + 1]{' + S(add[p]) * k' if ADD else ''};")
    for f in other:
        a = FIELD_ARR[f]
        rb.append(f"            {a}[p] = std::{FN[f]}({a}[2 * p], {a}[2 * p + 1]){' + add[p]' if ADD else ''};")

    def loop(fn):
        return f'''        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {{
            if (i & 1) {fn}(i++, k, v);
            if (j & 1) {fn}(--j, k, v);
        }}
        rebuild(l0), rebuild(r0);'''
    upd = ""
    if ADD: upd += f"\n    // O(logN) -- a[i] += v for i in [l, r]\n    void rangeAdd(int l, int r, T v) {{\n{loop('applyAdd')}\n    }}\n"
    if ASG: upd += f"\n    // O(logN) -- a[i] = v for i in [l, r]\n    void rangeAssign(int l, int r, T v) {{\n{loop('applyAssign')}\n    }}\n"
    q = f'''
    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {{
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        S res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) res += sm[l++];
            if (r & 1) res += sm[--r];
        }}
        return res;
    }}
'''
    for f in other:
        a = FIELD_ARR[f]
        q += f'''
    // O(logN) -- {f} of a[l..r]
    T {FIELD_OP[f]}(int l, int r) {{
        l += n, r += n;
        push(l), push(r);
        T res = {IDENT[f]};
        for (r++; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) res = std::{FN[f]}(res, {a}[l++]);
            if (r & 1) res = std::{FN[f]}(res, {a}[--r]);
        }}
        return res;
    }}
'''
    tag_decl = []
    if ADD: tag_decl.append("add")
    if ASG: tag_decl.append("asg")
    tag_init = []
    if ADD: tag_init.append("add.assign(n, 0)")
    if ASG: tag_init += ["asg.assign(n, 0)", "hasAsg.assign(n, 0)"]
    tagword = {"add": "a pending add", "assign": "a pending assign", "add+assign": "a pending assign or add"}[tags]
    d = describe("sum", fields, tags)
    return f'''
// {d[0].upper() + d[1:]}. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, and on each internal node {tagword}, meaning "applied here, not
// yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
// rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
{"    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();" + chr(10) if other else ""}    int n, h;
    vector<S> sm;  // 2N: leaves are sm[n..2n)
{f"    vector<T> {', '.join(oa)};{chr(10)}" if oa else ""}    vector<T> {", ".join(tag_decl)};  // N: tags on internal nodes
{"    vector<char> hasAsg;" + chr(10) if ASG else ""}
    // O(N)
    explicit {name}(const vector<T>& a) : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {{
        sm.assign(2 * n, 0);
{"".join(f"        {FIELD_ARR[f]}.assign(2 * n, {IDENT[f]});{chr(10)}" for f in other)}        for (int i = 0; i < n; i++) {{
            sm[n + i] = a[i];
{"".join(f"            {a}[n + i] = a[i];{chr(10)}" for a in oa)}        }}
        for (int x = n - 1; x > 0; x--) {{
            sm[x] = sm[2 * x] + sm[2 * x + 1];
{"".join(f"            {FIELD_ARR[f]}[x] = std::{FN[f]}({FIELD_ARR[f]}[2 * x], {FIELD_ARR[f]}[2 * x + 1]);{chr(10)}" for f in other)}        }}
        {", ".join(tag_init)};
    }}
{apply_add}{apply_asg}
    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {{
        for (int s = h; s > 0; s--) {{
            int x = p >> s, k = 1 << (s - 1);
{chr(10).join(push_lines)}
        }}
    }}

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {{
        for (int k = 2; p > 1; k <<= 1) {{
            p >>= 1;
{chr(10).join(rb)}
        }}
    }}
{upd}{q}
    // O(logN) -- a[i]
    T pointGet(int i) {{
        push(i + n);
        return T(sm[i + n]);
    }}

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {{
        int p = i + n;
        push(p);
        sm[p] = v;
{"".join(f"        {a}[p] = v;{chr(10)}" for a in oa)}        rebuild(p);
    }}

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {{ pointAssign(i, pointGet(i) + delta); }}

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {{ if (v > pointGet(i)) pointAssign(i, v); }}

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {{ if (v < pointGet(i)) pointAssign(i, v); }}
}};
'''


def write_cpp_all():
    for kind, fields, tags in variants():
        folder = "-".join(ops_of(kind, fields, tags))
        body = cpp_clamp(fields, tags) if kind == "clamp" else cpp_sum(fields, tags)
        open(os.path.join(DIR, folder, "template.cpp"), "w").write(header("//", kind, fields, tags) + body)
    print(len(variants()), "cpp templates written")

