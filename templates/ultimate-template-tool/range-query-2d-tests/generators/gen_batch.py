"""Whole input known: every update and query is recorded first, then solve() answers them all at once.

    python3 gen_batch.py           # writes range-queries-2d/batch-sum/template.{py,cpp}

Only usable when no call depends on an earlier answer. In exchange it is the one option with linear memory for point
adds and rectangle sums over any coordinates: divide and conquer over time, with one 1D Fenwick tree.
"""
from lib2d import cpp_throw, header, indent, py_raise, wrap_comment, write


def batch_sum():
    cls = "OfflineRectSum"
    ops = ["pointAdd", "rectSum"]
    costs = {"pointAdd": "log^2(N) amortized", "rectSum": "log^2(N) amortized"}
    memory = {"layout": "none", "node": "bit[1*N]", "other": "events[5*N] ys[1*N] answers[1*N]",
              "note": "N = how many calls were recorded; a rectSum is stored as its four corners"}
    doc = ("Point add and rectangle sum over any coordinates, answered all at once: linear memory, O(N log^2 N) in total. Call "
           "pointAdd and rectSum in the order they happen (they are only recorded: rectSum returns which query it is, 0, 1, "
           "2, ...), then solve() returns every answer, answers[i] for query i. Use it only when no call depends on an "
           "earlier answer. A rectangle sum is four corner sums (how much was added at x <= X and y <= Y before this "
           "moment). The calls are split in half by time, again and again: the adds of an earlier half count for the "
           "corners of the later half, and with both halves sorted by x that is one sweep with a Fenwick tree over y. "
           "Rectangles are inclusive, x1..x2 by y1..y2; coordinates are any integers.")
    py = ["from bisect import bisect_right", "from operator import itemgetter", "", ""] + wrap_comment(doc, "#")
    py += [f"class {cls}:", '    __slots__ = ("events", "queries")', "", "    # O(1) -- nothing recorded yet", "    def __init__(self):",
           "        self.events = []  # in call order: (x, y, v) for an add, (x1, y1, x2, y2, query number) for a sum", "        self.queries = 0", "",
           "    # O(1) now (O(log^2 N) amortized in solve) -- records: add v at (x, y)", "    def pointAdd(self, x, y, v):", "        self.events.append((x, y, v))", ""]
    py += indent(wrap_comment("O(1) now (O(log^2 N) amortized in solve) -- records: sum of everything added so far at x1 <= x <= x2 and y1 <= y <= y2. Returns "
                              "this query's number: its answer is solve()[that number]; needs x1 <= x2 and y1 <= y2, else IndexError", "#"))
    py += ["    def rectSum(self, x1, y1, x2, y2):", "        if x1 > x2 or y1 > y2:"]
    py += indent(py_raise("IndexError", "rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}", 3), 3)
    py += ["        self.events.append((x1, y1, x2, y2, self.queries))", "        self.queries += 1", "        return self.queries - 1", "",
           "    # O(N log^2 N) -- every rectSum's answer, in the order they were asked (can be called again after more calls)", "    def solve(self):"]
    py += indent([
        "ys = sorted({e[1] for e in self.events if len(e) == 3})",
        "# one item per add, four per sum (its corners): (x, y as a count of distinct add-y's <= it, amount or sign, query number or -1)",
        "items = []",
        "for e in self.events:",
        "    if len(e) == 3:",
        "        items.append((e[0], bisect_right(ys, e[1]), e[2], -1))",
        "    else:",
        "        x1, y1, x2, y2, q = e",
        "        top = bisect_right(ys, y2)",
        "        bot = bisect_right(ys, y1 - 1)",
        "        items += [(x2, top, 1, q), (x1 - 1, top, -1, q), (x2, bot, -1, q), (x1 - 1, bot, 1, q)]",
        "answers = [0] * self.queries",
        "m = len(ys)",
        "bit = [0] * (m + 1)",
        "byX = itemgetter(0)",
        "n = len(items)",
        "width = 1",
        "while width < n:  # blocks of `width` items, each already sorted by x; neighbors are an earlier and a later stretch of time",
        "    for l in range(0, n - width, 2 * width):",
        "        mid = l + width",
        "        r = min(mid + width, n)",
        "        i = l",
        "        for j in range(mid, r):",
        "            x, y, sign, q = items[j]",
        "            if q < 0:",
        "                continue",
        "            while i < mid and items[i][0] <= x:  # the earlier adds at or left of this corner go into the tree",
        "                if items[i][3] < 0:",
        "                    k = items[i][1]",
        "                    amount = items[i][2]",
        "                    while k <= m:",
        "                        bit[k] += amount",
        "                        k += k & -k",
        "                i += 1",
        "            total = 0",
        "            while y > 0:",
        "                total += bit[y]",
        "                y &= y - 1",
        "            answers[q] += sign * total",
        "        for k2 in range(l, i):  # take them back out",
        "            if items[k2][3] < 0:",
        "                k = items[k2][1]",
        "                amount = items[k2][2]",
        "                while k <= m:",
        "                    bit[k] -= amount",
        "                    k += k & -k",
        "        items[l:r] = sorted(items[l:r], key=byX)  # (stable, and both halves are sorted: a merge)",
        "    width *= 2",
        "return answers",
    ], 2)

    cpp = wrap_comment(doc, "//") + ["// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long long.",
                                      "template <typename T>", f"struct {cls} {{", "    using ll = long long;",
                                      "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;",
                                      "    struct Event {  // in call order: an add (query = -1) at (x1, y1), or a sum over x1..x2, y1..y2", "        ll x1, y1, x2, y2;",
                                      "        T v;", "        int query;", "    };", "    vector<Event> events;", "    int queries = 0;", "",
                                      "    // O(1) -- nothing recorded yet", f"    {cls}() {{}}", "",
                                      "    // O(1) now (O(log^2 N) amortized in solve) -- records: add v at (x, y)", "    void pointAdd(ll x, ll y, T v) {",
                                      "        events.push_back({x, y, 0, 0, v, -1});", "    }", ""]
    cpp += indent(wrap_comment("O(1) now (O(log^2 N) amortized in solve) -- records: sum of everything added so far at x1 <= x <= x2 and y1 <= y <= y2. Returns "
                               "this query's number: its answer is solve()[that number]; needs x1 <= x2 and y1 <= y2, else throws out_of_range", "//"))
    cpp += ["    int rectSum(ll x1, ll y1, ll x2, ll y2) {"] + indent(cpp_throw("x1 > x2 || y1 > y2", "out_of_range", "rectSum: needs x1 <= x2 and y1 <= y2", 2), 2)
    cpp += ["        events.push_back({x1, y1, x2, y2, T(0), queries});", "        return queries++;", "    }", "",
            "    // O(N log^2 N) -- every rectSum's answer, in the order they were asked (can be called again after more calls)", "    vector<S> solve() const {"]
    cpp += indent([
        "vector<ll> ys;",
        "for (auto& e : events)",
        "    if (e.query < 0) ys.push_back(e.y1);",
        "sort(ys.begin(), ys.end());",
        "ys.erase(unique(ys.begin(), ys.end()), ys.end());",
        "auto upTo = [&](ll y) { return (int)(upper_bound(ys.begin(), ys.end(), y) - ys.begin()); };  // distinct add-y's <= y",
        "// one item per add, four per sum (its corners)",
        "struct Item {",
        "    ll x;",
        "    int y;",
        "    S amount;  // what an add adds; +1 / -1 for a corner",
        "    int query;",
        "};",
        "vector<Item> items;",
        "for (auto& e : events) {",
        "    if (e.query < 0) {",
        "        items.push_back({e.x1, upTo(e.y1), S(e.v), -1});",
        "    } else {",
        "        int top = upTo(e.y2), bot = upTo(e.y1 - 1);",
        "        items.push_back({e.x2, top, 1, e.query}), items.push_back({e.x1 - 1, top, -1, e.query});",
        "        items.push_back({e.x2, bot, -1, e.query}), items.push_back({e.x1 - 1, bot, 1, e.query});",
        "    }",
        "}",
        "vector<S> answers(queries, 0);",
        "int m = (int)ys.size(), n = (int)items.size();",
        "vector<S> bit(m + 1, 0);",
        "auto byX = [](const Item& a, const Item& b) { return a.x < b.x; };",
        "// blocks of `width` items, each already sorted by x; neighbors are an earlier and a later stretch of time",
        "for (int width = 1; width < n; width *= 2) {",
        "    for (int l = 0; l + width < n; l += 2 * width) {",
        "        int mid = l + width, r = min(mid + width, n), i = l;",
        "        for (int j = mid; j < r; j++) {",
        "            if (items[j].query < 0) continue;",
        "            for (; i < mid && items[i].x <= items[j].x; i++)  // the earlier adds at or left of this corner go into the tree",
        "                if (items[i].query < 0)",
        "                    for (int k = items[i].y; k <= m; k += k & -k) bit[k] += items[i].amount;",
        "            S total = 0;",
        "            for (int k = items[j].y; k > 0; k &= k - 1) total += bit[k];",
        "            answers[items[j].query] += items[j].amount * total;",
        "        }",
        "        for (int t = l; t < i; t++)  // take them back out",
        "            if (items[t].query < 0)",
        "                for (int k = items[t].y; k <= m; k += k & -k) bit[k] -= items[t].amount;",
        "        inplace_merge(items.begin() + l, items.begin() + mid, items.begin() + r, byX);",
        "    }",
        "}",
        "return answers;",
    ], 2) + ["    }", "};"]
    args = (ops, "offline-sweep", costs, "1", memory, "batch", [])
    write("batch-sum", header("batch-sum", "py", *args) + py, header("batch-sum", "cpp", *args) + cpp)


def main():
    batch_sum()
    print("batch: 1 folder")


if __name__ == "__main__":
    main()
