"""The "compressed coordinates" version of a 2D template: the template, then a wrapper class in front of it.

lib2d.write calls compressed_variant on every folder it writes: a small-grid template with updates gets a second folder,
compressed-<the rest of its name>. The wrapper takes xs and ys, every x and every y the point operations will use, and
maps each listed x / y to its row / column of a small grid; the template underneath does the work. Rectangles and
corners can be any integers (binary search finds the listed coordinates inside). An axis can be left alone (Python:
pass an int n; C++: pass upTo(n)) to mean 0..n-1. Templates with rectangle updates and rectangle (or corner, or whole)
queries get no compressed version: a rectangle update reaches every listed x with every listed y inside it, and the
query would count those pairs too.
"""
import re

POINT_OPS = {
    "pointGet": None,
    "pointAssign": "the cell (x, y) becomes v",
    "pointAdd": "adds v to the cell (x, y)",
    "pointChmax": "the cell (x, y) becomes max(itself, v)",
    "pointChmin": "the cell (x, y) becomes min(itself, v)",
}
RECT_UPDATES = {
    "rectAdd": "adds v to every cell",
    "rectAssign": "every cell becomes v, for the cells",
    "rectChmax": "every cell becomes max(itself, v), for the cells",
    "rectChmin": "every cell becomes min(itself, v), for the cells",
}
WORDS = {"Sum": "sum", "Min": "min", "Max": "max", "Gcd": "gcd", "Xor": "XOR", "And": "AND", "Or": "OR"}
CORNER = re.compile(r"^(sum|min|max)(Lte|Gte)(Lte|Gte)$")
SIGN = {"Lte": "<=", "Gte": ">="}
RULE_PY = "x must be one of the xs and y one of the ys, else IndexError"
RULE_CPP = "x must be one of the xs and y one of the ys, else throws out_of_range"
UPDATES = set(RECT_UPDATES) | {"pointAssign", "pointAdd", "pointChmax", "pointChmin"}
NO_EMPTY = ("min", "max", "and")  # (no answer for no cells: these refuse, the rest give 0)


def _kind(op):
    """the aggregate a query op asks for (sum, min, ...), or None"""
    m = CORNER.match(op)
    if m:
        return m.group(1)
    if op.startswith("rect") and op not in RECT_UPDATES:
        return op[4:].lower()
    return None


def _rule(op, shape, lang, empties=False):
    err = "IndexError" if lang == "py" else "throws out_of_range"
    if shape in ("p", "pv"):
        return RULE_PY if lang == "py" else RULE_CPP
    if shape == "rectv":
        return f"any integers, needs x1 <= x2 and y1 <= y2, else {err}; no cell inside: nothing happens"
    k = _kind(op)
    if k == "and" and empties:
        none = "-1 (every bit set) if no cell is inside"
    elif k in NO_EMPTY and empties:
        none = f"{'None' if lang == 'py' else 'NO_' + k.upper()} if no cell is inside"
    else:
        none = f"{err} if no cell is inside" if k in NO_EMPTY else "0 if no cell is inside"
    if shape == "rect":
        return f"any integers, needs x1 <= x2 and y1 <= y2, else {err}; {none}"
    if shape == "corner":
        return f"any integers; {none.replace('inside', 'there')}"
    return ""


def _cost(expr):
    """a header cost in grid sizes, in the compressed sizes: X distinct x's, Y distinct y's (N = X * Y cells)"""
    return re.sub(r"\bC\b", "Y", re.sub(r"\bR\b", "X", expr))


def _shown(expr):
    expr = _cost(expr).replace("log(X)*log(Y)", "log X * log Y").replace("log(X)", "log X").replace("log(Y)", "log Y")
    return expr.replace("X*Y", "X * Y").replace("sqrt(N)", "sqrt(N)")


def _doc(op, empties):
    if op == "pointGet":
        return "the value at (x, y)" + (", None if the cell is empty" if empties else "")
    if op in POINT_OPS:
        return POINT_OPS[op] + ("; an empty cell becomes v" if empties else "")
    if op in RECT_UPDATES:
        return f"{RECT_UPDATES[op]} with x1 <= x <= x2 and y1 <= y <= y2"
    if op == "getAll":
        return "the whole grid, X rows of Y values: row i is the i-th smallest x, column j the j-th smallest y"
    m = CORNER.match(op)
    if m:
        k, a, b = m.groups()
        none = " (None if there are none)" if empties and k != "sum" else ""
        return f"{k} of the cells with x {SIGN[a]} the given x and y {SIGN[b]} the given y{none}"
    if op.endswith("All"):
        k = op[:-3]
        none = " (None if there are none)" if empties and k in ("min", "max") else ""
        return f"{WORDS[k.capitalize()]} of every {'set ' if empties and k in ('min', 'max') else ''}cell{none}"
    if op.startswith("rect"):
        k = op[4:]
        none = " (None if there are none)" if empties and k in ("Min", "Max") else ""
        return f"{WORDS[k]} of the cells with x1 <= x <= x2 and y1 <= y <= y2{none}"
    raise AssertionError(f"compress2d doesn't know {op}")


def _shape(op):
    if op in POINT_OPS:
        return "pv" if op != "pointGet" else "p"
    if op in RECT_UPDATES:
        return "rectv"
    if op == "getAll" or (op.endswith("All") and not CORNER.match(op)):
        return ""
    if CORNER.match(op):
        return "corner"
    if op.startswith("rect"):
        return "rect"
    raise AssertionError(f"compress2d doesn't know {op}")


ARGS = {"p": ["x", "y"], "pv": ["x", "y", "v"], "corner": ["x", "y"], "rect": ["x1", "y1", "x2", "y2"],
        "rectv": ["x1", "y1", "x2", "y2", "v"], "": []}


def _py_body(op, shape, empties):
    if shape in ("p", "pv"):
        return [f'return self.ds.{op}(*self._cell(x, y, "{op}"){", v" if shape == "pv" else ""})']
    if shape == "rectv":
        return [f'r = self._rect(x1, y1, x2, y2, "{op}")', "if r is not None:", f"    self.ds.{op}(*r, v)"]
    if shape in ("rect", "corner"):
        if shape == "rect":
            find, where = f'r = self._rect(x1, y1, x2, y2, "{op}")', "inside the rectangle"
        else:
            m = CORNER.match(op)
            find, where = f'r = self._corner(x, y, "{m.group(2)}", "{m.group(3)}")', "there"
        k = _kind(op)
        empty = ("return 0" if k not in NO_EMPTY else "return -1" if empties and k == "and" else "return None" if empties
                 else f'raise IndexError("{op}: no cell is {where}")')
        return [find, "if r is None:", f"    {empty}", f"return self.ds.{op}(*r)"]
    return [f"return self.ds.{op}()"]


def _cpp_body(op, shape, empties):
    if shape in ("p", "pv"):
        return [f'return ds.{op}(xAt(x, "{op}"), yAt(y, "{op}"){", v" if shape == "pv" else ""});']
    if shape == "rectv":
        return [f'auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "{op}");', f"if (r1 >= 0) ds.{op}(r1, c1, r2, c2, v);"]
    if shape in ("rect", "corner"):
        if shape == "rect":
            find, call, zero, where = (f'auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "{op}");', "r1, c1, r2, c2",
                                       "0, 0, 0, 0", "inside the rectangle")
        else:
            m = CORNER.match(op)
            find, call, zero, where = (f'auto [r1, c1] = corner(x, y, {str(m.group(2) == "Lte").lower()}, '
                                       f'{str(m.group(3) == "Lte").lower()});', "r1, c1", "0, 0", "there")
        k = _kind(op)
        if k not in NO_EMPTY:
            empty = f"return decltype(ds.{op}({zero}))(0);"
        elif empties and k == "and":
            empty = f"return decltype(ds.{op}({zero}))(-1);"
        elif empties:
            empty = f"return NO_{k.upper()};"
        else:
            empty = f'throw out_of_range("{op}: no cell is {where}");'
        return [find, f"if (r1 < 0) {empty}", f"return ds.{op}({call});"]
    return [f"return ds.{op}();"]


def _header(lines, folder, new_folder):
    """the header block (up to the first blank line) for the compressed folder"""
    out, i = [], 0
    in_cost = in_mem = False
    while i < len(lines) and lines[i] != "":
        line = lines[i]
        body = line.lstrip("#/ ")
        line = line.replace(f"/{folder}/", f"/{new_folder}/")
        if body.startswith("@input:"):
            line = line.replace(body, "@input: compressed")
        if body.startswith("@complexities:"):
            in_cost, in_mem = True, False
        elif body.startswith("@memory:"):
            in_cost, in_mem = False, True
        elif body.startswith("@"):
            in_cost = in_mem = False
        elif in_cost or in_mem:
            head = line[:len(line) - len(line.lstrip("#/ "))]
            key, _, rest = body.partition(": ")
            if in_cost or key in ("node", "tags", "other"):
                rest = _cost(rest)
            if in_mem and key == "other":
                extra = "xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]"
                rest = extra if rest == "none" else rest + " " + extra
            if in_mem and key == "note":
                rest = ("X = how many distinct x's, Y = distinct y's; " + rest)
            line = f"{head}{key}: {rest}"
        out.append(line)
        i += 1
    return out, i


def compressed_variant(folder, py, cpp):
    """(new folder, python lines, c++ lines) for a template that gets a compressed version, else None"""
    if not folder.startswith("grid-"):
        return None  # (a k-d tree is not one: it keeps given points, not a grid of listed x's by listed y's)
    head = "\n".join(py[:60])
    ops = re.search(r"@operations: (.*)", head).group(1).split()
    if not any(op in UPDATES for op in ops):
        return None  # (static: nothing to start from but the grid itself)
    if any(op in RECT_UPDATES for op in ops) and any(_kind(op) or op.endswith("All") and op != "getAll" for op in ops):
        # a rectangle update reaches every listed x with every listed y inside it, pairs you may never use
        # included, and a rectangle query would add those in: only rectangle updates with point reads make sense
        return None
    if any(op.startswith(("square", "window", "rectHash", "rectsEqual", "hash")) for op in ops):
        return None
    empties = "@empty-cells: yes" in head
    costs = dict(re.findall(r"^#   (\w+): (.*)$", head, re.M))
    new_folder = "compressed-" + folder.split("-", 1)[1]
    py_inner = [m.group(1) for line in py if (m := re.match(r"^class (\w+)", line))][-1]
    cpp_inner = [m.group(1) for line in cpp if (m := re.match(r"^struct (\w+) \{", line))][-1]
    sized = any(re.match(rf"^    {cpp_inner}\(int \w+, int \w+\)", line) for line in cpp)
    has_none = {name: any(f"static constexpr T {name}" in line for line in cpp) for name in ("NO_MAX", "NO_MIN")}

    doc = (f"Coordinate compression in front of {py_inner}: coordinates can be any integers (huge, negative, ...). You "
           f"list every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can "
           f"be any integers. Each listed x becomes a row and each listed y a column of a small grid, and the template "
           f"above does the work on it. X = how many distinct x's, Y = distinct y's: memory and costs are the "
           f"template's for an X by Y grid. A cell is a listed x with a listed y, and it is one point, not a block: a "
           f"rectangle covers just the cells inside it (the gaps between listed coordinates don't exist), so a sum adds "
           f"those cells' values, it is not an area. Cells you never set count as "
           f"{'empty' if empties else '0'}, a listed x with a listed y you never use together included.")
    start = "Every cell starts empty." if empties else "Every cell starts at 0."

    # ---------------- Python
    p = []
    from lib2d import indent, wrap_comment  # (lib2d imports this module)
    p += ["", ""] + (["from bisect import bisect_left, bisect_right", "", ""]
                     if any(_shape(op) in ("rect", "rectv", "corner") for op in ops) else []) + wrap_comment(doc, "#") + ["class Compressed2D:", '    __slots__ = ("xs", "ys", "xAt", "yAt", "ds")', ""]
    p += indent(wrap_comment(f"O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use "
                             f"(any order, repeats are fine), or an int n to leave x uncompressed as "
                             f"0..n-1; ys: the same for y. {start} Needs at least one x and one y, else ValueError", "#"))
    build = f"self.ds = {py_inner}([[{'None' if empties else '0'}] * len(self.ys) for _ in self.xs])"
    p += ["    def __init__(self, xs, ys):",
          "        self.xs = range(xs) if isinstance(xs, int) else sorted(set(xs))",
          "        self.ys = range(ys) if isinstance(ys, int) else sorted(set(ys))",
          '        if not self.xs or not self.ys:',
          '            raise ValueError("Compressed2D: needs at least one x and one y")',
          "        # a listed coordinate's row / column (None: that axis is 0..n-1 as it is)",
          "        self.xAt = None if isinstance(xs, int) else {x: i for i, x in enumerate(self.xs)}",
          "        self.yAt = None if isinstance(ys, int) else {y: i for i, y in enumerate(self.ys)}",
          "        " + build, ""]
    for axis in ("x", "y"):
        p += [f"    def _{axis}(self, {axis}, name):", f"        at = self.{axis}At",
              "        if at is None:", f"            if 0 <= {axis} < len(self.{axis}s):", f"                return {axis}",
              f"        elif {axis} in at:", f"            return at[{axis}]",
              f'        raise IndexError(f"{{name}}: {axis} = {{{axis}}} is not one of the {axis}s given to the constructor")', ""]
    p += ["    # the row and column of the cell (x, y)", "    def _cell(self, x, y, name):", "        return self._x(x, name), self._y(y, name)", ""]
    if any(_shape(op) in ("rect", "rectv") for op in ops):
        p += ["    # the rows and columns a rectangle covers, (r1, c1, r2, c2); None when no listed x or no listed y is inside",
              "    def _rect(self, x1, y1, x2, y2, name):",
              "        if x1 > x2 or y1 > y2:",
              '            raise IndexError(f"{name}: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")',
              "        r1, r2 = bisect_left(self.xs, x1), bisect_right(self.xs, x2) - 1",
              "        c1, c2 = bisect_left(self.ys, y1), bisect_right(self.ys, y2) - 1",
              "        if r1 > r2 or c1 > c2:", "            return None", "        return r1, c1, r2, c2", ""]
    if any(_shape(op) == "corner" for op in ops):
        p += ["    # the cell a corner query starts from: the last listed x <= x (Lte) or the first listed x >= x (Gte), the",
              "    # same for y; None when there is none",
              "    def _corner(self, x, y, xSide, ySide):",
              '        r = bisect_right(self.xs, x) - 1 if xSide == "Lte" else bisect_left(self.xs, x)',
              '        c = bisect_right(self.ys, y) - 1 if ySide == "Lte" else bisect_left(self.ys, y)',
              "        if not (0 <= r < len(self.xs) and 0 <= c < len(self.ys)):", "            return None",
              "        return r, c", ""]
    for op in ops:
        shape = _shape(op)
        cost = _shown(costs.get(op, "1"))
        rule = f"; {_rule(op, shape, 'py', empties)}" if ARGS[shape] else ""
        p += indent(wrap_comment(f"O({cost}) -- {_doc(op, empties)}{rule}", "#"))
        p += [f"    def {op}(self{''.join(', ' + a for a in ARGS[shape])}):"] + indent(_py_body(op, shape, empties), 2) + [""]
    while p[-1] == "":
        p.pop()

    # ---------------- C++
    c = [""] + wrap_comment(doc, "//") + ["template <typename T>", "struct Compressed2D {", "    using ll = long long;"]
    for name, there in has_none.items():
        if there:
            c.append(f"    static constexpr T {name} = {cpp_inner}<T>::{name};")
    c += ["    vector<ll> xs, ys;  // the listed coordinates, sorted, each once", f"    {cpp_inner}<T> ds;", "",
          "    // n coordinates 0..n-1: pass upTo(n) for an axis you don't want compressed",
          "    static vector<ll> upTo(ll n) {", "        vector<ll> v(n);", "        iota(v.begin(), v.end(), 0LL);", "        return v;", "    }", ""]
    c += indent(wrap_comment(f"O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use "
                             f"(any order, repeats are fine), or upTo(n) to leave x as 0..n-1; ys: the "
                             f"same for y. {start} Needs at least one x and one y, else throws invalid_argument", "//"))
    c += ["    Compressed2D(vector<ll> xs_, vector<ll> ys_)", "        : xs(sorted(std::move(xs_))), ys(sorted(std::move(ys_))), ds(make(xs, ys)) {}", "",
          "    static vector<ll> sorted(vector<ll> v) {", "        sort(v.begin(), v.end());", "        v.erase(unique(v.begin(), v.end()), v.end());",
          "        return v;", "    }", "",
          f"    static {cpp_inner}<T> make(const vector<ll>& xs, const vector<ll>& ys) {{",
          '        if (xs.empty() || ys.empty()) throw invalid_argument("Compressed2D: needs at least one x and one y");',
          "        int X = (int)xs.size(), Y = (int)ys.size();"]
    if sized:
        c.append(f"        return {cpp_inner}<T>(X, Y);")
    else:
        c.append(f"        return {cpp_inner}<T>(vector<vector<T>>(X, vector<T>(Y, T(0))));")
    c += ["    }", ""]
    for axis in ("x", "y"):
        c += [f"    // the row / column of a listed {axis}", f"    int {axis}At(ll {axis}, const char* name) const {{",
              f"        int lo = 0, hi = (int){axis}s.size();", "        while (lo < hi) {", "            int mid = (lo + hi) >> 1;",
              f"            if ({axis}s[mid] < {axis}) lo = mid + 1;", "            else hi = mid;", "        }",
              f"        if (lo == (int){axis}s.size() || {axis}s[lo] != {axis})",
              f'            throw out_of_range(string(name) + ": {axis} is not one of the {axis}s given to the constructor");',
              "        return lo;", "    }", ""]
    if any(_shape(op) in ("rect", "rectv") for op in ops):
        c += ["    // the rows and columns a rectangle covers, {r1, c1, r2, c2}; r1 = -1 when no listed x or no listed y is inside",
              "    array<int, 4> rect(ll x1, ll y1, ll x2, ll y2, const char* name) const {",
              '        if (x1 > x2 || y1 > y2) throw out_of_range(string(name) + ": needs x1 <= x2 and y1 <= y2");',
              "        int r1 = int(lower_bound(xs.begin(), xs.end(), x1) - xs.begin());",
              "        int r2 = int(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) - 1;",
              "        int c1 = int(lower_bound(ys.begin(), ys.end(), y1) - ys.begin());",
              "        int c2 = int(upper_bound(ys.begin(), ys.end(), y2) - ys.begin()) - 1;",
              "        if (r1 > r2 || c1 > c2) return {-1, -1, -1, -1};", "        return {r1, c1, r2, c2};", "    }", ""]
    if any(_shape(op) == "corner" for op in ops):
        c += ["    // the cell a corner query starts from: the last listed x <= x (xLte) or the first listed x >= x, the same",
              "    // for y; {-1, -1} when there is none",
              "    array<int, 2> corner(ll x, ll y, bool xLte, bool yLte) const {",
              "        int r = xLte ? int(upper_bound(xs.begin(), xs.end(), x) - xs.begin()) - 1",
              "                     : int(lower_bound(xs.begin(), xs.end(), x) - xs.begin());",
              "        int c = yLte ? int(upper_bound(ys.begin(), ys.end(), y) - ys.begin()) - 1",
              "                     : int(lower_bound(ys.begin(), ys.end(), y) - ys.begin());",
              "        if (r < 0 || r >= (int)xs.size() || c < 0 || c >= (int)ys.size()) return {-1, -1};",
              "        return {r, c};", "    }", ""]
    for op in ops:
        shape = _shape(op)
        cost = _shown(costs.get(op, "1"))
        rule = f"; {_rule(op, shape, 'cpp', empties)}" if ARGS[shape] else ""
        params = ", ".join(("T v" if a == "v" else f"ll {a}") for a in ARGS[shape])
        c += indent(wrap_comment(f"O({cost}) -- {_doc(op, empties).replace('None', 'NO_' + _kind(op).upper() if _kind(op) in ('min', 'max') else 'NO_MAX' if has_none['NO_MAX'] else 'NO_MIN')}{rule}", "//"))
        c += [f"    {'void' if shape == 'rectv' else 'auto'} {op}({params}) {{"] + indent(_cpp_body(op, shape, empties), 2) + ["    }", ""]
    while c[-1] == "":
        c.pop()
    c.append("};")

    py_head, pi = _header(py, folder, new_folder)
    cpp_head, ci = _header(cpp, folder, new_folder)
    return new_folder, py_head + py[pi:] + p, cpp_head + cpp[ci:] + c
