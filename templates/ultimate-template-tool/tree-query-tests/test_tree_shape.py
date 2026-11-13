"""Tests the tree shape templates (tree-queries/shape-*).

Random trees and op scripts run on the Python template and are checked against a brute force (parent pointers, every
path walked node by node). The same scripts are then fed to the C++ template, which has to print exactly what the
Python one did. Also checked: bad input is rejected with a clear error (not a wrong answer), both labelings (0..n-1 and
1..n), edges with and without weights, and long chains (nothing may recurse).

    python3 test_tree_shape.py           # both languages
    python3 test_tree_shape.py --py      # Python only
    python3 test_tree_shape.py --cpp     # C++ only (the Python template still runs, to say what to expect)
"""
import os
import random
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "tree-queries")
sys.path.insert(0, ROOT)
from find_compiler import cxx, sanitize_flags  # noqa: E402

FOLDERS = ("shape-heavy-light", "shape-heavy-light-lca-table")

# op -> what its arguments are: n = a node, k = a step count, d = a depth
OPS = {
    "lca": "nn", "unweightedDist": "nn", "depth": "n", "parent": "n", "kthAncestor": "nk", "isAncestor": "nn",
    "subtreeSize": "n", "countAtDepthInSubtree": "nd", "lcaRootedAt": "nnn", "parentRootedAt": "nn",
    "subtreeSizeRootedAt": "nn", "kthNodeOnPath": "nnk", "nextNodeOnPath": "nn", "isOnPath": "nnn",
    "unweightedDistToPath": "nnn", "unweightedDistBetweenPaths": "nnnn", "median": "nnn", "pathIntersection": "nnnn",
    "pathNodes": "nn",
}


def load_py(folder):
    ns = {}
    exec(open(os.path.join(DIR, folder, "template.py"), encoding="utf-8").read(), ns)
    return ns["Tree"]


# ------------------------------------------------------------------------------------------------ brute force
class Brute:
    def __init__(self, edges, root):
        nodes = sorted({x for e in edges for x in e[:2]} | {root})
        self.nodes, self.root = nodes, root
        self.adj = {v: [] for v in nodes}
        for e in edges:
            self.adj[e[0]].append(e[1])
            self.adj[e[1]].append(e[0])
        self.par, self.dep = self.rooted(root)
        self.below = {v: {u for u in nodes if v in self.up(u)} for v in nodes}  # v's subtree

    def rooted(self, r):
        par, dep, todo = {r: -1}, {r: 0}, [r]
        for v in todo:
            for u in self.adj[v]:
                if u not in par:
                    par[u], dep[u] = v, dep[v] + 1
                    todo.append(u)
        return par, dep

    def up(self, v, par=None):  # v, its parent, ..., the root
        par = par or self.par
        out = []
        while v != -1:
            out.append(v)
            v = par[v]
        return out

    def path(self, a, b, par=None):
        ua, ub = self.up(a, par), self.up(b, par)
        on = set(ua)
        c = next(x for x in ub if x in on)
        return ua[: ua.index(c) + 1] + ub[: ub.index(c)][::-1]

    def run(self, op, args):
        par, dep = self.par, self.dep
        if op == "lca":
            a, b = args
            p = self.path(a, b)
            return min(p, key=lambda x: dep[x])
        if op == "unweightedDist":
            return len(self.path(*args)) - 1
        if op == "depth":
            return dep[args[0]]
        if op == "parent":
            return par[args[0]]
        if op == "kthAncestor":
            chain = self.up(args[0])
            return chain[args[1]] if args[1] < len(chain) else -1
        if op == "isAncestor":
            return args[1] in self.below[args[0]]
        if op == "subtreeSize":
            return len(self.below[args[0]])
        if op == "countAtDepthInSubtree":
            return sum(1 for u in self.below[args[0]] if dep[u] == args[1])
        if op in ("lcaRootedAt", "parentRootedAt", "subtreeSizeRootedAt"):
            rpar, rdep = self.rooted(args[0])
            if op == "lcaRootedAt":
                return min(self.path(args[1], args[2], rpar), key=lambda x: rdep[x])
            if op == "parentRootedAt":
                return rpar[args[1]]
            return sum(1 for u in self.nodes if args[1] in self.up(u, rpar))
        if op == "kthNodeOnPath":
            p = self.path(args[0], args[1])
            return p[args[2]] if args[2] < len(p) else -1
        if op == "nextNodeOnPath":
            p = self.path(*args)
            return p[1] if len(p) > 1 else -1
        if op == "isOnPath":
            return args[2] in self.path(args[0], args[1])
        if op == "unweightedDistToPath":
            return min(len(self.path(args[2], x)) - 1 for x in self.path(args[0], args[1]))
        if op == "unweightedDistBetweenPaths":
            p, q = self.path(args[0], args[1]), self.path(args[2], args[3])
            return min(len(self.path(x, y)) - 1 for x in p for y in q)
        if op == "median":
            a, b, c = args
            (m,) = set(self.path(a, b)) & set(self.path(a, c)) & set(self.path(b, c))
            return m
        if op == "pathIntersection":
            q = set(self.path(args[2], args[3]))
            common = [x for x in self.path(args[0], args[1]) if x in q]
            return (common[0], common[-1]) if common else (-1, -1)
        if op == "pathNodes":
            return self.path(*args)
        raise AssertionError(op)


# ------------------------------------------------------------------------------------------------ cases
def shape_edges(n, shape, rng):
    """n - 1 edges on nodes 0..n-1."""
    if shape == "chain":
        return [(i, i + 1) for i in range(n - 1)]
    if shape == "star":
        return [(0, i) for i in range(1, n)]
    if shape == "binary":
        return [((i - 1) // 2, i) for i in range(1, n)]
    if shape == "caterpillar":  # a spine with one leg on some of its nodes
        spine = max(1, n * 2 // 3)
        return [(i, i + 1) for i in range(spine - 1)] + [(rng.randrange(spine), i) for i in range(spine, n)]
    if shape == "deep":  # each node hangs near the newest ones: long, a few branches
        return [(rng.randrange(max(0, i - 3), i), i) for i in range(1, n)]
    return [(rng.randrange(i), i) for i in range(1, n)]


SHAPES = ("random", "chain", "star", "binary", "caterpillar", "deep")


def make_tree(n, shape, rng):
    """(edges, root) with shuffled labels, 0..n-1 or 1..n, edges in random order and direction, sometimes weighted."""
    lo = rng.randrange(2)
    label = list(range(lo, lo + n))
    rng.shuffle(label)
    weighted = rng.random() < 0.3
    edges = []
    for a, b in shape_edges(n, shape, rng):
        a, b = label[a], label[b]
        if rng.random() < 0.5:
            a, b = b, a
        edges.append([a, b, rng.randrange(1, 100)] if weighted else [a, b])
    rng.shuffle(edges)
    return edges, rng.choice(label), lo


def make_queries(n, lo, count, rng, bad=0.03):
    hi = lo + n - 1
    out = []
    for _ in range(count):
        op = rng.choice(list(OPS))
        args = []
        for kind in OPS[op]:
            if kind == "n":
                args.append(rng.choice((lo - 1, hi + 1, hi + 5)) if rng.random() < bad else rng.randrange(lo, hi + 1))
            elif kind == "k":
                args.append(-1 if rng.random() < bad else rng.randrange(0, n + 2) if rng.random() < 0.5 else rng.randrange(0, 4))
            else:
                args.append(rng.randrange(-1, n + 2) if rng.random() < 0.5 else rng.randrange(-1, 6))
        out.append((op, args))
    return out


def show(res):
    if isinstance(res, bool):
        return "1" if res else "0"
    if isinstance(res, tuple):
        return f"{res[0]} {res[1]}"
    if isinstance(res, list):
        return " ".join(map(str, [len(res)] + res))
    return str(res)


def is_bad(op, args, lo, hi):
    return any((kind == "n" and not lo <= x <= hi) or (kind == "k" and x < 0) for kind, x in zip(OPS[op], args))


def run_py(Tree, edges, root, queries):
    """The lines the template prints for one case: how the build went, then one line per query."""
    try:
        tree = Tree(edges, root)
    except ValueError:
        return ["invalid"]
    out = ["ok"]
    for op, args in queries:
        try:
            out.append(show(getattr(tree, op)(*args)))
        except IndexError:
            out.append("ERR")
    return out


# trees that must be refused: (edges, root)
INVALID = [
    ([[2, 3], [3, 4]], 2),  # smallest label 2
    ([[0, 1], [1, 2]], 3),  # root is not a node
    ([[1, 2], [2, 3]], 0),  # root 0 on nodes 1..3
    ([[0, 1], [2, 3], [3, 4]], 0),  # a label past n - 1, two pieces
    ([[0, 1], [0, 1]], 0),  # the same edge twice: node 2 is unreachable
    ([[0, 1], [1, 2], [2, 0], [3, 4]], 0),  # a cycle and a separate piece
    ([[0, 0]], 0),  # a self loop
    ([[-1, 0]], 0),  # a negative label
    ([[1, 2], [3, 4], [1, 3], [1, 6]], 1),  # a label past n
    ([], 2),  # one node, but labeled 2
]


def cases(rng):
    """(edges, root, queries, brute-checked?)"""
    out = []
    for _ in range(360):  # small: everything against the brute force
        n = rng.choice((1, 1, 2, 2, 3, 4, 5, 6, 8, 11, 15, 22, 30))
        edges, root, lo = make_tree(n, rng.choice(SHAPES), rng)
        out.append((edges, root, make_queries(n, lo, 70, rng), True))
    for shape in SHAPES:  # bigger: the two templates and the two languages against each other
        for n in (200, 1500, 4000):
            edges, root, lo = make_tree(n, shape, rng)
            out.append((edges, root, make_queries(n, lo, 1500, rng, bad=0.005), False))
    for edges, root in INVALID:
        out.append((edges, root, [("depth", [root])], False))
    return out


# ------------------------------------------------------------------------------------------------ C++
DRIVER = r"""
// test driver: cases from stdin, one line per answer
template <typename E>
static void runCase(int m, int root) {
    vector<vector<E>> edges(m);
    for (auto& e : edges) {
        int len;
        scanf("%d", &len);
        e.resize(len);
        for (auto& x : e) {
            long long v;
            scanf("%lld", &v);
            x = (E)v;
        }
    }
    unique_ptr<Tree> t;
    try {
        t = make_unique<Tree>(edges, root);
        puts("ok");
    } catch (const invalid_argument&) {
        puts("invalid");
    }
    int q;
    scanf("%d", &q);
    char op[64];
    while (q--) {
        int cnt, a[4] = {0, 0, 0, 0};
        scanf("%63s %d", op, &cnt);
        for (int i = 0; i < cnt; i++) scanf("%d", &a[i]);
        if (!t) continue;
        string s = op;
        try {
            if (s == "lca") printf("%d\n", t->lca(a[0], a[1]));
            else if (s == "unweightedDist") printf("%d\n", t->unweightedDist(a[0], a[1]));
            else if (s == "depth") printf("%d\n", t->depth(a[0]));
            else if (s == "parent") printf("%d\n", t->parent(a[0]));
            else if (s == "kthAncestor") printf("%d\n", t->kthAncestor(a[0], a[1]));
            else if (s == "isAncestor") printf("%d\n", (int)t->isAncestor(a[0], a[1]));
            else if (s == "subtreeSize") printf("%d\n", t->subtreeSize(a[0]));
            else if (s == "countAtDepthInSubtree") printf("%d\n", t->countAtDepthInSubtree(a[0], a[1]));
            else if (s == "lcaRootedAt") printf("%d\n", t->lcaRootedAt(a[0], a[1], a[2]));
            else if (s == "parentRootedAt") printf("%d\n", t->parentRootedAt(a[0], a[1]));
            else if (s == "subtreeSizeRootedAt") printf("%d\n", t->subtreeSizeRootedAt(a[0], a[1]));
            else if (s == "kthNodeOnPath") printf("%d\n", t->kthNodeOnPath(a[0], a[1], a[2]));
            else if (s == "nextNodeOnPath") printf("%d\n", t->nextNodeOnPath(a[0], a[1]));
            else if (s == "isOnPath") printf("%d\n", (int)t->isOnPath(a[0], a[1], a[2]));
            else if (s == "unweightedDistToPath") printf("%d\n", t->unweightedDistToPath(a[0], a[1], a[2]));
            else if (s == "unweightedDistBetweenPaths")
                printf("%d\n", t->unweightedDistBetweenPaths(a[0], a[1], a[2], a[3]));
            else if (s == "median") printf("%d\n", t->median(a[0], a[1], a[2]));
            else if (s == "pathIntersection") {
                pair<int, int> r = t->pathIntersection(a[0], a[1], a[2], a[3]);
                printf("%d %d\n", r.first, r.second);
            } else if (s == "pathNodes") {
                vector<int> r = t->pathNodes(a[0], a[1]);
                printf("%d", (int)r.size());
                for (int x : r) printf(" %d", x);
                puts("");
            } else {
                printf("unknown op %s\n", op);
            }
        } catch (const out_of_range&) {
            puts("ERR");
        }
    }
}

int main() {
    // (the documented ways to write a small tree compile)
    Tree lit({{0, 1}, {1, 2}}, 0), one({}, 1);
    if (lit.lca(1, 2) != 1 || one.subtreeSize(1) != 1) return 3;
    int cases;
    scanf("%d", &cases);
    for (int c = 0; c < cases; c++) {
        int m, root;
        scanf("%d %d", &m, &root);
        if (c % 2) runCase<long long>(m, root);  // (both edge types the constructor takes)
        else runCase<int>(m, root);
    }
    // a chain of a million nodes, built and queried: nothing may recurse
    int n = 1000000;
    vector<vector<int>> chain(n - 1);
    for (int i = 0; i + 1 < n; i++) chain[i] = {i + 1, i + 2};
    Tree big(chain, 1);
    printf("%d %d %d %d\n", big.lca(n, n / 2), big.kthAncestor(n, n - 1), big.unweightedDist(1, n),
           big.countAtDepthInSubtree(7, n - 1));
}
"""


def script_text(all_cases):
    lines = [str(len(all_cases))]
    for edges, root, queries, _ in all_cases:
        lines.append(f"{len(edges)} {root}")
        lines += [" ".join(map(str, [len(e)] + list(e))) for e in edges]
        lines.append(str(len(queries)))
        lines += [" ".join(map(str, [op, len(args)] + args)) for op, args in queries]
    return "\n".join(lines) + "\n"


def run_cpp(folder, script, tmp, extra=()):
    src, exe = os.path.join(tmp, folder + ".cpp"), os.path.join(tmp, folder)
    open(src, "w").write(open(os.path.join(DIR, folder, "template.cpp"), encoding="utf-8").read() + DRIVER)
    build = subprocess.run([cxx(), "-std=c++17", "-O2", *sanitize_flags(), *extra, "-o", exe, src], capture_output=True, text=True)
    if build.returncode != 0:
        return None, build.stderr[-3000:]
    run = subprocess.run([exe], input=script, capture_output=True, text=True)
    if run.returncode != 0:
        return None, f"exit code {run.returncode}: {run.stderr[-2000:]}"
    return run.stdout.split("\n"), ""


def main():
    langs = [a for a in sys.argv[1:] if a in ("--py", "--cpp")] or ["--py", "--cpp"]
    rng = random.Random(20261112)
    all_cases = cases(rng)
    fails = 0
    expected = {}
    start = time.time()
    for folder in FOLDERS:
        Tree = load_py(folder)
        lines, checked = [], 0
        for edges, root, queries, brute in all_cases:
            got = run_py(Tree, edges, root, queries)
            lines += got
            if (got[0] == "invalid") != ((edges, root) in INVALID):
                fails += 1
                print(f"FAIL  {folder} (py): build said {got[0]} for edges {edges}, root {root}")
            if not brute:
                continue
            ref = Brute(edges, root)
            lo, hi = ref.nodes[0], ref.nodes[-1]
            for (op, args), line in zip(queries, got[1:]):
                want = "ERR" if is_bad(op, args, lo, hi) else show(ref.run(op, args))
                checked += 1
                if line != want:
                    fails += 1
                    print(f"FAIL  {folder} (py): {op}{tuple(args)} = {line}, expected {want}; edges {edges}, root {root}")
                    break
        # a long chain: 300,000 nodes built and queried without recursion
        n = 300000
        big = Tree([(i, i + 1) for i in range(1, n)], 1)
        deep = (big.lca(n, n // 2), big.kthAncestor(n, n - 1), big.unweightedDist(1, n), big.countAtDepthInSubtree(7, n - 1))
        if deep != (n // 2, 1, n - 1, 1):
            fails += 1
            print(f"FAIL  {folder} (py): long chain gave {deep}")
        expected[folder] = lines
        if "--py" in langs:
            print(f"PASS  {folder} (py): {checked} answers match the brute force, {len(all_cases)} trees" if not fails
                  else f"FAIL  {folder} (py)")
    if expected[FOLDERS[0]] != expected[FOLDERS[1]]:
        fails += 1
        print("FAIL  the two shape templates disagree with each other (py)")
    if "--cpp" in langs:
        script = script_text(all_cases)
        with tempfile.TemporaryDirectory() as tmp:
            for folder in FOLDERS:
                out, err = run_cpp(folder, script, tmp)
                want = expected[folder] + ["500000 1 999999 1", ""]
                if out is None:
                    fails += 1
                    print(f"FAIL  {folder} (cpp): {err}")
                elif out != want:
                    fails += 1
                    at = next((i for i, (x, y) in enumerate(zip(out, want)) if x != y), min(len(out), len(want)))
                    print(f"FAIL  {folder} (cpp): line {at} is {out[at:at + 1]}, the Python template printed {want[at:at + 1]}")
                else:
                    print(f"PASS  {folder} (cpp): {len(want) - 2} lines match the Python template, plus a 1,000,000-node chain")
            # the documented switch that turns sanitizer skipping off still compiles and agrees
            out, err = run_cpp(FOLDERS[0], script, tmp, extra=("-DLEETCODE_NO_SANITIZE=",))
            if out != expected[FOLDERS[0]] + ["500000 1 999999 1", ""]:
                fails += 1
                print(f"FAIL  {FOLDERS[0]} (cpp, LEETCODE_NO_SANITIZE defined empty): {err or 'different output'}")
    print(f"{'FAIL' if fails else 'PASS'}  tree shape templates: {fails} failures, {time.time() - start:.0f}s")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
