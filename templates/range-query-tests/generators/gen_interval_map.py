"""leftmostIndexOf / rightmostIndexOf (whole array or inside [l, r]) with RANGE ASSIGN: an interval map.

    python3 gen_interval_map.py

The array is kept as maximal-ish runs [start, next start) of one value: an ordered map start -> value, and per value
the ordered set of its runs' starts. A range assign splits the runs at l and r + 1, deletes the runs inside and adds
one: it adds at most 3 runs, so every run it deletes was paid for by an earlier op (O(log N) amortized). x's first
index in [l, r] is l if the run holding l has x, else the start of x's next run, if that is still <= r. Python takes
its SortedList from the point-update position lists template (one copy of that class to maintain).
"""
import os

from note_lang import strip_attribution, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SORTED_LIST_FROM = "countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rightmostIndexOf-rightmostIndexOfInRange"
OPS = sorted(["getAll", "leftmostIndexOf", "leftmostIndexOfInRange", "pointAdd", "pointAssign", "pointChmax", "pointChmin",
              "pointGet", "rangeAssign", "rightmostIndexOf", "rightmostIndexOfInRange"])
AMORT = {"pointAdd", "pointAssign", "pointChmax", "pointChmin", "rangeAssign"}


def header(cm):
    lines = [f"@operations: {' '.join(OPS)}", "@data-structure-type: interval-map", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N) amortized' if op in AMORT else 'log(N)'}" for op in OPS]
    lines += ["  build: N*log(N)", "@memory:", "  layout: none", "  node: runs[1*N] byVal[1*N]", "  tags: none", "  other: none",
              "  note: one entry per run of equal values (at most N, usually far fewer), in the run map and in its value's set"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


DOC = '''{c} "Where is x's first / last copy, in the whole array or inside a[l..r]?" with RANGE ASSIGN and point updates. All
{c} indices 0-based, ranges inclusive; -1 when there is no such index. The array is kept as runs of one value: an
{c} ordered map start -> value, and per value the ordered set of its runs' starts. An assign splits the runs at l and
{c} r + 1, deletes the runs inside and adds one, so it adds at most 3 runs and pays for every run it later deletes
{c} (O(log N) amortized). x's first index in [l, r] is l if the run holding l has x, else the start of x's next run.
'''

PY = '''

class IntervalMap:
    __slots__ = ("n", "starts", "val", "byVal")

    # O(N) -- arr: the initial array (equal neighbours become one run)
    def __init__(self, arr):
        n = self.n = len(arr)
        starts, val, by = [], {}, {}
        for i, v in enumerate(arr):
            if i == 0 or v != arr[i - 1]:
                starts.append(i)
                val[i] = v
                by.setdefault(v, []).append(i)
        self.starts = SortedList(starts)  # every run's start, in order
        self.val = val  # run start -> its value
        self.byVal = {v: SortedList(s) for v, s in by.items()}  # value -> the starts of its runs

    # O(logN) amortized -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l > r:
            return
        self._split(l)
        self._split(r + 1)
        starts, val, by = self.starts, self.val, self.byVal
        s = l
        while s is not None and s <= r:  # (the runs inside [l, r], each deleted once)
            nxt = starts.succ(s)
            starts.remove(s)
            v = val.pop(s)
            p = by[v]
            p.remove(s)
            if not len(p):
                del by[v]
            s = nxt
        starts.add(l)
        val[l] = x
        p = by.get(x)
        if p is None:
            p = by[x] = SortedList()
        p.add(l)

    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        p = self.byVal.get(x)
        return p.lists[0][0] if p is not None else -1

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        p = self.byVal.get(x)
        return self._end(p.lists[-1][-1]) if p is not None else -1

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    def leftmostIndexOfInRange(self, l, r, x):
        p = self.byVal.get(x)
        if p is None or l > r:
            return -1
        s = p.pred(l + 1)  # x's last run starting at or before l: does it reach l?
        if s is not None and self._end(s) >= l:
            return l
        s = p.succ(l)
        return s if s is not None and s <= r else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    def rightmostIndexOfInRange(self, l, r, x):
        p = self.byVal.get(x)
        if p is None or l > r:
            return -1
        s = p.pred(r + 1)  # x's last run starting at or before r
        if s is None:
            return -1
        e = min(self._end(s), r)
        return e if e >= l else -1

    # O(logN) -- a[i]
    def pointGet(self, i):
        val = self.val
        return val[i] if i in val else val[self.starts.pred(i)]

    # O(N) -- the whole array
    def getAll(self):
        out, val = [], self.val
        prev = None
        for b in self.starts.lists:
            for s in b:
                if prev is not None:
                    out += [val[prev]] * (s - prev)
                prev = s
        if prev is not None:
            out += [val[prev]] * (self.n - prev)
        return out

    # O(logN) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self.rangeAssign(i, i, v)

    # O(logN) amortized -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN) amortized -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        if v > self.pointGet(i):
            self.rangeAssign(i, i, v)

    # O(logN) amortized -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        if v < self.pointGet(i):
            self.rangeAssign(i, i, v)

    # ---- internals ----

    def _end(self, s):  # the last index of the run starting at s
        t = self.starts.succ(s)
        return (self.n if t is None else t) - 1

    def _split(self, i):  # make a run start at i (nothing if one does, or i == n)
        val = self.val
        if i >= self.n or i in val:
            return
        v = val[self.starts.pred(i)]
        self.starts.add(i)
        val[i] = v
        self.byVal[v].add(i)
'''

CPP = '''// T: int, long long, char, ... (any type usable as a std::map key).
template <typename T>
struct IntervalMap {
    int n;
    map<int, T> runs;          // run start -> its value; a run lasts until the next start
    map<T, set<int>> byVal;    // value -> the starts of its runs

    // O(N log N) -- arr: the initial array (equal neighbours become one run)
    explicit IntervalMap(const vector<T>& arr) : n((int)arr.size()) {
        for (int i = 0; i < n; i++)
            if (i == 0 || !(arr[i] == arr[i - 1])) runs.emplace_hint(runs.end(), i, arr[i]), byVal[arr[i]].insert(i);
    }

    // O(logN) amortized -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) {
        if (l > r) return;
        split(l), split(r + 1);
        auto it = runs.find(l);
        while (it != runs.end() && it->first <= r) {  // (the runs inside [l, r], each deleted once)
            auto p = byVal.find(it->second);
            p->second.erase(it->first);
            if (p->second.empty()) byVal.erase(p);
            it = runs.erase(it);
        }
        runs.emplace_hint(it, l, x);
        byVal[x].insert(l);
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const {
        auto p = byVal.find(x);
        return p == byVal.end() ? -1 : *p->second.begin();
    }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const {
        auto p = byVal.find(x);
        return p == byVal.end() ? -1 : end(*p->second.rbegin());
    }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        auto p = byVal.find(x);
        if (p == byVal.end() || l > r) return -1;
        auto j = p->second.upper_bound(l);  // x's next run after l; the one before it starts at or before l
        if (j != p->second.begin() && end(*prev(j)) >= l) return l;
        return j != p->second.end() && *j <= r ? *j : -1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        auto p = byVal.find(x);
        if (p == byVal.end() || l > r) return -1;
        auto j = p->second.upper_bound(r);  // x's last run starting at or before r is the one before
        if (j == p->second.begin()) return -1;
        int e = min(end(*prev(j)), r);
        return e >= l ? e : -1;
    }

    // O(logN) -- a[i]
    T pointGet(int i) const { return prev(runs.upper_bound(i))->second; }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (auto it = runs.begin(); it != runs.end(); ++it) {
            int e = next(it) == runs.end() ? n : next(it)->first;
            out.insert(out.end(), e - it->first, it->second);
        }
        return out;
    }

    // O(logN) amortized -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(logN) amortized -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAssign(i, i, pointGet(i) + delta); }

    // O(logN) amortized -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (pointGet(i) < v) rangeAssign(i, i, v); }

    // O(logN) amortized -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) rangeAssign(i, i, v); }

    // ---- internals ----

    int end(int s) const {  // the last index of the run starting at s
        auto it = next(runs.find(s));
        return (it == runs.end() ? n : it->first) - 1;
    }

    void split(int i) {  // make a run start at i (nothing if one does, or i == n)
        if (i >= n) return;
        auto it = runs.upper_bound(i);
        auto b = prev(it);
        if (b->first == i) return;
        runs.emplace_hint(it, i, b->second);
        byVal[b->second].insert(i);
    }
};
'''


def sorted_list_py():
    src = strip_attribution(open(os.path.join(DIR, SORTED_LIST_FROM, "template.py")).read())
    a = src.index("# SortedList: a self-contained sorted container")
    b = src.index("\n# ", src.index("class SortedList"))  # (up to the next top-level comment: the template's own doc)
    return src[src.index("from bisect"):src.index("\n", src.index("from bisect")) + 1] + "\n\n" + src[a:b].rstrip() + "\n"


def main():
    folder = os.path.join(DIR, "-".join(o for o in OPS if o != "getAll"))
    os.makedirs(folder, exist_ok=True)
    write_template(os.path.join(folder, "template.py"), header("#") + "\n" + sorted_list_py() + "\n" + DOC.format(c="#") + PY)
    write_template(os.path.join(folder, "template.cpp"), header("//") + "\n" + DOC.format(c="//") + CPP)
    print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
