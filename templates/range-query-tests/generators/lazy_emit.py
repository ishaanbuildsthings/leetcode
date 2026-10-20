from lazy_common import *
from note_lang import write_template

CMP = {"min": "<", "max": ">"}
IDENT_PY = {"min": "INF", "max": "NEG"}


def comps(tags):
    return "A" in tags, "B" in tags, "C" in tags


def clamp_params(tags):
    A, B, C = comps(tags)
    return [p for p, on in (("hi", A), ("lo", B), ("c", C)) if on]


# ------------------------------------------------------------------ Python, clamp-tag variants
def py_eval(var, tags, src, ind):
    """lines applying the clamp to var; src(name) gives the expression for tag part name ("hi", "lo", "c")"""
    A, B, C = comps(tags)
    out = []
    if C: out.append(f"{ind}{var} += {src('c')}")
    if B: out.append(f"{ind}if {var} < {src('lo')}:\n{ind}    {var} = {src('lo')}")
    if A: out.append(f"{ind}if {var} > {src('hi')}:\n{ind}    {var} = {src('hi')}")
    return "\n".join(out)


def py_compose(tags, ind):
    A, B, C = comps(tags)
    out = []
    if A:
        base = "self.hi[x] + c" if C else "self.hi[x]"
        out.append(f"{ind}nhi = {base}")
        if B: out.append(f"{ind}if nhi < lo:\n{ind}    nhi = lo")
        out.append(f"{ind}self.hi[x] = nhi if nhi < hi else hi")
    if B:
        base = "self.lo[x] + c" if C else "self.lo[x]"
        out.append(f"{ind}nlo = {base}")
        out.append(f"{ind}if nlo < lo:\n{ind}    nlo = lo")
        if A: out.append(f"{ind}if nlo > self.hi[x]:\n{ind}    nlo = self.hi[x]")
        out.append(f"{ind}self.lo[x] = nlo")
    if C: out.append(f"{ind}self.add[x] += c")
    return "\n".join(out)


def py_clamp(fields, tags):
    A, B, C = comps(tags)
    name = class_name("clamp", fields, tags)
    arrs = [FIELD_ARR[f] for f in fields]
    tarr = tag_arrays("clamp", tags)
    params = ", ".join(clamp_params(tags))
    tag_ident = {"hi": "INF", "lo": "NEG", "add": "0"}
    own = lambda p: {"hi": "self.hi[p]", "lo": "self.lo[p]", "c": "self.add[p]"}[p]  # noqa: E731
    arg = lambda p: p  # noqa: E731
    apply_fields = "\n".join(f"        v = self.{a}[x]\n{py_eval('v', tags, arg, '        ')}\n        self.{a}[x] = v" for a in arrs)
    rebuild_fields = "\n".join(
        f"            a, b = self.{a}[2 * p], self.{a}[2 * p + 1]\n            v = a if a {CMP[f]} b else b\n"
        f"{py_eval('v', tags, own, '            ')}\n            self.{a}[p] = v" for f, a in zip(fields, arrs))
    cond = " or ".join(f"self.{t}[x] != {tag_ident[t]}" for t in tarr)
    tagvals = ", ".join(f"self.{t}[x]" for t in tarr)
    reset = "\n".join(f"                self.{t}[x] = {tag_ident[t]}" for t in tarr)
    call = {"C": None}
    def args(hi, lo, c):
        return ", ".join(v for v, on in ((hi, A), (lo, B), (c, C)) if on)
    upd = []
    if C: upd.append(("rangeAdd", "a[i] += v", args("INF", "NEG", "v")))
    if A: upd.append(("rangeChmin", "a[i] = min(a[i], v)", args("v", "NEG", "0")))
    if B: upd.append(("rangeChmax", "a[i] = max(a[i], v)", args("INF", "v", "0")))
    if A and B: upd.append(("rangeAssign", "a[i] = v", args("v", "v", "0")))
    upd_text = "".join(f'''
    # O(logN) -- {d} for i in [l, r]
    def {m}(self, l, r, v):
        self._update(l, r, {a})
''' for m, d, a in upd)
    queries = "".join(f'''
    # O(logN) -- {f} of a[l..r]
    def {FIELD_OP[f]}(self, l, r):
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        arr = self.{FIELD_ARR[f]}
        res = {IDENT_PY[f]}
        r += 1
        while l < r:
            if l & 1:
                if arr[l] {CMP[f]} res:
                    res = arr[l]
                l += 1
            if r & 1:
                r -= 1
                if arr[r] {CMP[f]} res:
                    res = arr[r]
            l >>= 1
            r >>= 1
        return res
''' for f in fields)
    tagdesc = {"C": "x + add", "A": "min(hi, x)", "B": "max(lo, x)", "AB": "min(hi, max(lo, x))", "AC": "min(hi, x + add)",
               "BC": "max(lo, x + add)", "ABC": "min(hi, max(lo, x + add))"}[tags]
    extra = ""
    if A and B:
        extra = "\n# Assign v is the clamp with hi = lo = v."
    return f'''
INF = float("inf")
NEG = float("-inf")

# {describe("clamp", fields, tags)[0].upper() + describe("clamp", fields, tags)[1:]}. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
# to my children". The tag is the map x -> {tagdesc}; these maps compose into the same form, and each is
# monotone, so it sends a node's min / max straight to the new min / max.{extra}
# An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.


class {name}:
    __slots__ = ({", ".join(f'"{x}"' for x in ["n", "h"] + arrs + tarr)})

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
{chr(10).join(f"        self.{a} = [{IDENT_PY[f]}] * n + list(arr)" for f, a in zip(fields, arrs))}
        for x in range(n - 1, 0, -1):
{chr(10).join(f"            a, b = self.{a}[2 * x], self.{a}[2 * x + 1]{chr(10)}            self.{a}[x] = a if a {CMP[f]} b else b" for f, a in zip(fields, arrs))}
{chr(10).join(f"        self.{t} = [{tag_ident[t]}] * n" for t in tarr)}

    # apply the map to node x: to its values now, and (if internal) on top of its pending tag
    def _apply(self, x, {params}):
{apply_fields}
        if x < self.n:
{py_compose(tags, "            ")}

    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            if {cond}:
                {params} = {tagvals}
                self._apply(2 * x, {params})
                self._apply(2 * x + 1, {params})
{reset}

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        while p > 1:
            p >>= 1
{rebuild_fields}

    def _update(self, l, r, {params}):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j = l0, r0 + 1
        while i < j:
            if i & 1:
                self._apply(i, {params})
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, {params})
            i >>= 1
            j >>= 1
        self._rebuild(l0)
        self._rebuild(r0)
{upd_text}{queries}
    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return self.{arrs[0]}[p]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        {" = ".join(f"self.{a}[p]" for a in arrs)} = val
        self._rebuild(p)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''


# ------------------------------------------------------------------ Python, sum variants (tags: add and / or assign)
def py_sum(fields, tags):
    ADD, ASG = "add" in tags, "assign" in tags
    name = class_name("sum", fields, tags)
    arrs = [FIELD_ARR[f] for f in fields]
    tarr = tag_arrays("sum", tags)
    other = [f for f in fields if f != "sum"]
    lines_add = ["        self.sm[x] += c * k"] + [f"        self.{FIELD_ARR[f]}[x] += c" for f in other]
    if ASG:
        lines_add += ["        if x < self.n:", "            if self.hasAsg[x]:", "                self.asg[x] += c  # still an assign, of a shifted value", "            else:", "                self.add[x] += c"] if ADD else []
    else:
        lines_add += ["        if x < self.n:", "            self.add[x] += c"]
    lines_asg = ["        self.sm[x] = v * k"] + ([" = ".join(f"        self.{FIELD_ARR[f]}[x]" if i == 0 else f"self.{FIELD_ARR[f]}[x]" for i, f in enumerate(other)) + " = v"] if other else [])
    lines_asg += ["        if x < self.n:", "            self.hasAsg[x] = True", "            self.asg[x] = v"] + (["            self.add[x] = 0"] if ADD else [])
    apply_add = ("\n    # add c to every slot of node x, which covers k slots\n    def _applyAdd(self, x, k, c):\n" + "\n".join(lines_add) + "\n") if ADD else ""
    apply_asg = ("\n    # set every slot of node x (k slots) to v\n    def _applyAssign(self, x, k, v):\n" + "\n".join(lines_asg) + "\n") if ASG else ""
    push_body = []
    if ASG:
        push_body += ["            if self.hasAsg[x]:", "                self._applyAssign(2 * x, k, self.asg[x])", "                self._applyAssign(2 * x + 1, k, self.asg[x])", "                self.hasAsg[x] = False"]
    if ADD:
        kw = "elif" if ASG else "if"
        push_body += [f"            {kw} self.add[x]:", "                self._applyAdd(2 * x, k, self.add[x])", "                self._applyAdd(2 * x + 1, k, self.add[x])", "                self.add[x] = 0"]
    combine = {"sum": "self.sm[2 * p] + self.sm[2 * p + 1]", "min": "min(self.mn[2 * p], self.mn[2 * p + 1])", "max": "max(self.mx[2 * p], self.mx[2 * p + 1])"}
    rb = []
    if ASG:
        rb += ["            if self.hasAsg[p]:", "                v = self.asg[p]", "                self.sm[p] = v * k"] + ([("                " + " = ".join(f"self.{FIELD_ARR[f]}[p]" for f in other) + " = v")] if other else []) + ["                continue"]
    for f in fields:
        a = FIELD_ARR[f]
        tail = (" + self.add[p] * k" if f == "sum" else " + self.add[p]") if ADD else ""
        rb.append(f"            self.{a}[p] = {combine[f]}{tail}")
    upd = []
    loop = lambda fn, a: f'''        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        lo, hi, k = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self.{fn}(lo, k, {a})
                lo += 1
            if hi & 1:
                hi -= 1
                self.{fn}(hi, k, {a})
            lo >>= 1
            hi >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)'''
    if ADD: upd.append(f"\n    # O(logN) -- a[i] += v for i in [l, r]\n    def rangeAdd(self, l, r, v):\n{loop('_applyAdd', 'v')}\n")
    if ASG: upd.append(f"\n    # O(logN) -- a[i] = v for i in [l, r]\n    def rangeAssign(self, l, r, v):\n{loop('_applyAssign', 'v')}\n")
    queries = []
    for f in fields:
        a = FIELD_ARR[f]
        if f == "sum":
            step = ("                res += arr[l]\n", "                res += arr[r]\n")
            init = "0"
        else:
            c = CMP[f]
            step = (f"                if arr[l] {c} res:\n                    res = arr[l]\n", f"                if arr[r] {c} res:\n                    res = arr[r]\n")
            init = IDENT_PY[f]
        queries.append(f'''
    # O(logN) -- {"a[l] + ... + a[r]" if f == "sum" else f + " of a[l..r]"}
    def {FIELD_OP[f]}(self, l, r):
        if l > r:
            return {"0" if f == "sum" else init}
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        arr = self.{a}
        res = {init}
        r += 1
        while l < r:
            if l & 1:
{step[0]}                l += 1
            if r & 1:
                r -= 1
{step[1]}            l >>= 1
            r >>= 1
        return res
''')
    init_fields = "\n".join(f"        self.{FIELD_ARR[f]} = [{'0' if f == 'sum' else IDENT_PY[f]}] * n + list(arr)" for f in fields)
    build = "\n".join(f"            self.{FIELD_ARR[f]}[x] = {combine[f].replace('p]', 'x]').replace('* p', '* x')}" for f in fields)
    tag_init = "\n".join(f"        self.{t} = [{ {'add': '0', 'asg': '0', 'hasAsg': 'False'}[t] }] * n" for t in tarr)
    tagword = {"add": "a pending add", "assign": "a pending assign", "add+assign": "a pending assign or add"}[tags]
    need_inf = any(f in ("min", "max") for f in fields)
    return f'''{"" if not need_inf else chr(10) + 'INF = float("inf")' + chr(10) + 'NEG = float("-inf")' + chr(10)}
# {describe("sum", fields, tags)[0].upper() + describe("sum", fields, tags)[1:]}. All indices 0-based, ranges inclusive [l, r].
# Iterative 2N lazy tree: values on the leaves, and on each internal node {tagword}, meaning "applied here, not
# yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
# rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.


class {name}:
    __slots__ = ({", ".join(f'"{x}"' for x in ["n", "h"] + arrs + tarr)})

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
{init_fields}
        for x in range(n - 1, 0, -1):
{build}
{tag_init}
{apply_add}{apply_asg}
    # push every tag on the root-to-leaf path of leaf p down one level
    def _push(self, p):
        for s in range(self.h, 0, -1):
            x = p >> s
            k = 1 << (s - 1)
{chr(10).join(push_body)}

    # recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
{chr(10).join(rb)}
{"".join(upd)}{"".join(queries)}
    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._push(p)
        return self.sm[p]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        {" = ".join(f"self.{a}[p]" for a in arrs)} = val
        self._rebuild(p)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''


def write_py_all():
    for kind, fields, tags in variants():
        folder = "-".join(ops_of(kind, fields, tags))
        body = py_clamp(fields, tags) if kind == "clamp" else py_sum(fields, tags)
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), header("#", kind, fields, tags) + body)
    print(len(variants()), "python templates written")

