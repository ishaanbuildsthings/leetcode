"""Writes the tree shape templates (no values): tree-queries/shape-heavy-light and shape-heavy-light-lca-table, each
template.py + template.cpp. Both lay the tree out with one heavy-light pass; the second adds a sparse table over
that layout so lca (and everything built on it) is O(1).

    python3 gen_tree_shape.py           # write
    python3 gen_tree_shape.py --check   # exit 1 if a file on disk differs from what this would write

The C++ file is fast mode by default (methods skip sanitizers, members are HotVector): there is no second file.
Lines between "@if table" / "@else" / "@end" markers are kept for one variant only.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "set-tests", "generators"))
from gen_sets import FAST_VECTOR_PRELUDE, check_finished, must_replace  # noqa: E402

# (one line of the shared prelude is past 120 columns: wrapped here the way format_long_lines.py wraps it)
PRELUDE = must_replace(
    FAST_VECTOR_PRELUDE,
    "operator[](size_t i) const { return this->_M_impl._M_start[i]; }",
    "operator[](size_t i) const {\n        return this->_M_impl._M_start[i];\n    }",
)

DIR = os.path.join(ROOT, "tree-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries"

# (folder, data structure type, has the lca table)
VARIANTS = (("shape-heavy-light", "heavy-light", False), ("shape-heavy-light-lca-table", "heavy-light-lca-table", True))

# op -> (cost without the table, cost with it)
COSTS = {
    "lca": ("log(N)", "1"),
    "unweightedDist": ("log(N)", "1"),
    "depth": ("1", "1"),
    "parent": ("1", "1"),
    "kthAncestor": ("log(N)", "log(N)"),
    "isAncestor": ("1", "1"),
    "subtreeSize": ("1", "1"),
    "countAtDepthInSubtree": ("log(N)", "log(N)"),
    "lcaRootedAt": ("log(N)", "1"),
    "parentRootedAt": ("log(N)", "log(N)"),
    "subtreeSizeRootedAt": ("log(N)", "log(N)"),
    "kthNodeOnPath": ("log(N)", "log(N)"),
    "nextNodeOnPath": ("log(N)", "log(N)"),
    "isOnPath": ("log(N)", "1"),
    "unweightedDistToPath": ("log(N)", "1"),
    "unweightedDistBetweenPaths": ("log(N)", "1"),
    "median": ("log(N)", "1"),
    "pathIntersection": ("log(N)", "1"),
    "pathNodes": ("K+log(N)", "K"),
}
BUILD = ("N", "N*log(N)")
LAYOUT_ARRAYS = "par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N]"
OTHER_ARRAYS = ("depthPos[1*N] depthStart[1*N]", "depthPos[1*N] depthStart[1*N] table[1*N*log(N)]")


def header(cm, folder, kind, table, ext):
    k = 1 if table else 0
    lines = [
        "Template by https://github.com/ishaanbuildsthings",
        f"{URL}/{folder}/template.{ext}",
        "@operations: " + " ".join(sorted(COSTS)),
        f"@data-structure-type: {kind}",
        "@complexities:",
        *[f"  {op}: {cost[k]}" for op, cost in COSTS.items()],
        f"  build: {BUILD[k]}",
        "@memory:",
        "  layout: none",
        f"  node: {LAYOUT_ARRAYS}",
        "  tags: none",
        f"  other: {OTHER_ARRAYS[k]}",
    ]
    return "".join(f"{cm} {line}\n" for line in lines)


def pick(text, table):
    """Keeps the lines of the chosen variant: "@if table" ... ["@else" ...] "@end" (the marker lines are dropped)."""
    out, keep = [], True
    for line in text.split("\n"):
        mark = line.strip().lstrip("#/").strip()
        if mark == "@if table":
            keep = table
        elif mark == "@else":
            keep = not table
        elif mark == "@end":
            keep = True
        elif keep:
            out.append(line)
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ what both say
HOW = """\
How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A path crosses O(log n) chains, so walking up chain by
chain finds an lca or a kth ancestor in O(log n) with O(n) memory."""
HOW_TABLE = """\
How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
stretch of positions (pos[node] .. pos[node] + sz[node] - 1). On top of that, a sparse table over the positions
answers lca in O(1): between two nodes' positions, the parent that sits earliest is their lca. Ancestor jumps still
walk chain by chain, O(log n)."""

# ------------------------------------------------------------------------------------------------ Python
PY = '''\
from bisect import bisect_left

# tree = Tree(edges, root)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1
#
#   Tree([(0, 1), (1, 2)], 0)    # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1)    # nodes 1..3, rooted at 1
#   Tree([], 1)                  # one node, labeled 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
@HOW@
class Tree:
    # @BUILD_COST@ -- builds the layout from the edge list; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n
    def __init__(self, edges, root):
        n = len(edges) + 1
        lo = float("inf")
        for e in edges:
            if len(e) != 2 and len(e) != 3:
                raise ValueError(f"Tree: every edge needs 2 or 3 numbers, (a, b) or (a, b, w), got {e}")
            if e[0] < lo:
                lo = e[0]
            if e[1] < lo:
                lo = e[1]
        if not edges:
            lo = root
        if lo != 0 and lo != 1:
            raise ValueError(f"Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is {lo}")
        hi = lo + n - 1
        if not lo <= root <= hi:
            raise ValueError(f"Tree: root must be one of the nodes {lo}..{hi}, got {root}")
        adj = [[] for _ in range(hi + 1)]
        for e in edges:
            a, b = e[0], e[1]
            if a > hi or b > hi:
                raise ValueError(f"Tree: {n - 1} edges means the nodes are {lo}..{hi}, got the edge ({a}, {b})")
            adj[a].append(b)
            adj[b].append(a)

        # parents and depths, top down (par is -2 until a node is reached)
        par = [-2] * (hi + 1)
        dep = [0] * (hi + 1)
        par[root] = -1
        bfs = [root]
        for v in bfs:
            d = dep[v] + 1
            for u in adj[v]:
                if par[u] == -2:
                    par[u] = v
                    dep[u] = d
                    bfs.append(u)
        if len(bfs) != n:
            raise ValueError("Tree: the edges do not form one tree (some node cannot be reached from root)")

        # subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz = [1] * (hi + 1)
        for i in range(n - 1, 0, -1):
            v = bfs[i]
            sz[par[v]] += sz[v]
        heavy = [-1] * (hi + 1)
        for i in range(1, n):
            v = bfs[i]
            p = par[v]
            if heavy[p] == -1 or sz[v] > sz[heavy[p]]:
                heavy[p] = v

        # positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head = [0] * (hi + 1)  # the top node of each node's chain
        pos = [0] * (hi + 1)
        order = [0] * n  # order[pos[v]] = v
        head[root] = root
        stack = [root]
        t = 0
        while stack:
            v = stack.pop()
            pos[v] = t
            order[t] = v
            t += 1
            h = heavy[v]
            p = par[v]
            for u in adj[v]:
                if u != p and u != h:
                    head[u] = u
                    stack.append(u)
            if h != -1:  # pushed last, so it is popped next
                head[h] = head[v]
                stack.append(h)

        # depthPos[depthStart[d] : depthStart[d + 1]] = the positions of the nodes at depth d, increasing
        maxDep = dep[bfs[-1]]
        depthStart = [0] * (maxDep + 2)
        for v in bfs:
            depthStart[dep[v] + 1] += 1
        for d in range(maxDep + 1):
            depthStart[d + 1] += depthStart[d]
        at = depthStart[:]
        depthPos = [0] * n
        for i in range(n):
            d = dep[order[i]]
            depthPos[at[d]] = i
            at[d] += 1
        #@if table

        # table[j][i] = the earliest parent position among the nodes at positions i .. i + 2^j - 1
        row = [0] * n
        for i in range(1, n):
            row[i] = pos[par[order[i]]]
        table = [row]
        half = 1
        while 2 * half < n:
            row = [row[i] if row[i] < row[i + half] else row[i + half] for i in range(n - 2 * half + 1)]
            table.append(row)
            half *= 2
        self.table = table
        #@end

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        #@if table
        if a == b:
            return a
        l, r = self.pos[a], self.pos[b]
        if l > r:
            l, r = r, l
        j = (r - l).bit_length() - 1
        row = self.table[j]
        x, y = row[l + 1], row[r - (1 << j) + 1]
        return self.order[x if x < y else y]
        #@else
        head, par, dep = self.head, self.par, self.dep
        while head[a] != head[b]:
            if dep[head[a]] > dep[head[b]]:
                a = par[head[a]]
            else:
                b = par[head[b]]
        return a if dep[a] < dep[b] else b
        #@end

    # the node k steps above node (k <= its depth): a whole chain at a time
    def _kth(self, node, k):
        head, pos, par = self.head, self.pos, self.par
        while True:
            h = head[node]
            d = pos[node] - pos[h]
            if k <= d:
                return self.order[pos[node] - k]
            k -= d + 1
            node = par[h]

    def _dist(self, a, b):
        dep = self.dep
        return dep[a] + dep[b] - 2 * dep[self._lca(a, b)]

    # of the three pairwise lcas two are equal and the third, the deeper one, is the median
    def _median(self, a, b, c):
        dep = self.dep
        x, y, z = self._lca(a, b), self._lca(a, c), self._lca(b, c)
        if dep[y] > dep[x]:
            x = y
        return z if dep[z] > dep[x] else x

    def _isAncestor(self, a, b):
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    def _onPath(self, a, b, node):
        return self._isAncestor(self._lca(a, b), node) and (self._isAncestor(node, a) or self._isAncestor(node, b))

    # the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    def _next(self, a, b):
        if self._isAncestor(a, b):
            return self._kth(b, self.dep[b] - self.dep[a] - 1)
        return self.par[a]

    # @LCA_COST@ -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # @LCA_COST@ -- number of edges on the path a..b
    def unweightedDist(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("unweightedDist", a, b)
        return self.dep[a] + self.dep[b] - 2 * self.dep[self._lca(a, b)]

    # O(1) -- edges from the root to node (the root is depth 0)
    def depth(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("depth", node)
        return self.dep[node]

    # O(1) -- node's parent (-1 for the root)
    def parent(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("parent", node)
        return self.par[node]

    # O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    def kthAncestor(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("kthAncestor", node)
        if k < 0:
            raise IndexError(f"kthAncestor: needs k >= 0, got {k}")
        return self._kth(node, k) if k <= self.dep[node] else -1

    # O(1) -- is a an ancestor of b? (True when a == b)
    def isAncestor(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("isAncestor", a, b)
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    # O(1) -- number of nodes in node's subtree (node included)
    def subtreeSize(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("subtreeSize", node)
        return self.sz[node]

    # O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    def countAtDepthInSubtree(self, node, d):
        if not self.lo <= node <= self.hi:
            self._bad("countAtDepthInSubtree", node)
        if d < 0 or d + 1 >= len(self.depthStart):
            return 0
        s, e = self.depthStart[d], self.depthStart[d + 1]
        l = self.pos[node]
        return bisect_left(self.depthPos, l + self.sz[node], s, e) - bisect_left(self.depthPos, l, s, e)

    # @LCA_COST@ -- lca of a and b if the tree were rooted at r instead
    def lcaRootedAt(self, r, a, b):
        if not (self.lo <= r <= self.hi and self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lcaRootedAt", r, a, b)
        return self._median(a, b, r)

    # O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    def parentRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("parentRootedAt", r, node)
        return -1 if node == r else self._next(node, r)

    # O(log n) -- size of node's subtree if the tree were rooted at r
    def subtreeSizeRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("subtreeSizeRootedAt", r, node)
        if node == r:
            return self.n
        if self._isAncestor(node, r):  # r hangs below node: everything but the child holding r
            return self.n - self.sz[self._kth(r, self.dep[r] - self.dep[node] - 1)]
        return self.sz[node]

    # O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    # k >= 0
    def kthNodeOnPath(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("kthNodeOnPath", a, b)
        if k < 0:
            raise IndexError(f"kthNodeOnPath: needs k >= 0, got {k}")
        dep = self.dep
        c = self._lca(a, b)
        up = dep[a] - dep[c]
        total = up + dep[b] - dep[c]
        if k > total:
            return -1
        return self._kth(a, k) if k <= up else self._kth(b, total - k)

    # O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    def nextNodeOnPath(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nextNodeOnPath", a, b)
        return -1 if a == b else self._next(a, b)

    # @LCA_COST@ -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # @LCA_COST@ -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # @LCA_COST@ -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # @LCA_COST@ -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # @LCA_COST@ -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # @PATH_COST@ -- every node on the path a..b, in order from a (K = how many)
    def pathNodes(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("pathNodes", a, b)
        par = self.par
        c = self._lca(a, b)
        out = []
        while a != c:
            out.append(a)
            a = par[a]
        out.append(c)
        tail = []
        while b != c:
            tail.append(b)
            b = par[b]
        tail.reverse()
        return out + tail
'''

# ------------------------------------------------------------------------------------------------ C++
FAST_NOTE = """\
// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.
"""

CPP = '''\
// Tree tree(edges, root);
//
// edges: the tree's n - 1 edges, vector<vector<int>> (vector<vector<long long>> works too). Whether nodes are 0..n-1
//        or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with
//        no edges, from root)
//   {{a, b}, ...}        e.g. {{0, 1}, {1, 2}}
//   {{a, b, w}, ...}     also accepted: the weights are ignored here
// root: the root node (required), e.g. 0 or 1
//
//   Tree tree({{0, 1}, {1, 2}}, 0);    // nodes 0..2, rooted at 0
//   Tree tree({{1, 2}, {2, 3}}, 1);    // nodes 1..3, rooted at 1
//   Tree tree({}, 1);                  // one node, labeled 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. Nothing recurses, so a 10^6-node chain is fine.
//
@HOW@
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    //@if table
    // table[j * n + i] = the earliest parent position among the nodes at positions i .. i + 2^j - 1
    HotVector<int> table;
    //@end

    // @BUILD_COST@ -- builds the layout from the edge list; throws invalid_argument when the edges are not one tree on
    // nodes 0..n-1 or 1..n
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root) : root(root) {
        n = (int)edges.size() + 1;
        long long least = root;
        if (!edges.empty()) {
            least = LLONG_MAX;
            for (const auto& e : edges) {
                if (e.size() != 2 && e.size() != 3)
                    throw invalid_argument("Tree: every edge needs 2 or 3 numbers, {a, b} or {a, b, w}");
                least = min({least, (long long)e[0], (long long)e[1]});
            }
        }
        if (least != 0 && least != 1)
            throw invalid_argument("Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is " +
                                   to_string(least));
        lo = (int)least, hi = lo + n - 1;
        string nodes = to_string(lo) + ".." + to_string(hi);
        if (root < lo || root > hi)
            throw invalid_argument("Tree: root must be one of the nodes " + nodes + ", got " + to_string(root));
        int size = hi + 1;

        // the neighbors of v are adj[start[v] .. start[v + 1])
        vector<int> start(size + 1, 0), adj(2 * (n - 1));
        for (const auto& e : edges) {
            if ((long long)e[0] > hi || (long long)e[1] > hi)
                throw invalid_argument("Tree: " + to_string(n - 1) + " edges means the nodes are " + nodes +
                                       ", got the edge (" + to_string(e[0]) + ", " + to_string(e[1]) + ")");
            start[e[0] + 1]++, start[e[1] + 1]++;
        }
        for (int v = 0; v < size; v++) start[v + 1] += start[v];
        vector<int> at(start.begin(), start.end() - 1);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            adj[at[a]++] = b, adj[at[b]++] = a;
        }

        // parents and depths, top down (par is -2 until a node is reached)
        par.assign(size, -2), dep.assign(size, 0);
        vector<int> bfs(n);
        int reached = 0;
        par[root] = -1, bfs[reached++] = root;
        for (int i = 0; i < reached; i++) {
            int v = bfs[i];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (par[u] == -2) par[u] = v, dep[u] = dep[v] + 1, bfs[reached++] = u;
            }
        }
        if (reached != n)
            throw invalid_argument("Tree: the edges do not form one tree (some node cannot be reached from root)");

        // subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz.assign(size, 1);
        for (int i = n - 1; i > 0; i--) sz[par[bfs[i]]] += sz[bfs[i]];
        vector<int> heavy(size, -1);
        for (int i = 1; i < n; i++) {
            int v = bfs[i], p = par[v];
            if (heavy[p] == -1 || sz[v] > sz[heavy[p]]) heavy[p] = v;
        }

        // positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head.assign(size, 0), pos.assign(size, 0), order.assign(n, 0);
        vector<int> todo = {root};
        todo.reserve(n);
        head[root] = root;
        int t = 0;
        while (!todo.empty()) {
            int v = todo.back();
            todo.pop_back();
            pos[v] = t, order[t++] = v;
            int h = heavy[v], p = par[v];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (u != p && u != h) head[u] = u, todo.push_back(u);
            }
            if (h != -1) head[h] = head[v], todo.push_back(h);  // pushed last, so it is popped next
        }

        int maxDep = dep[bfs[n - 1]];
        depthStart.assign(maxDep + 2, 0), depthPos.assign(n, 0);
        for (int i = 0; i < n; i++) depthStart[dep[bfs[i]] + 1]++;
        for (int d = 0; d <= maxDep; d++) depthStart[d + 1] += depthStart[d];
        vector<int> slot(depthStart.begin(), depthStart.end() - 1);
        for (int i = 0; i < n; i++) depthPos[slot[dep[order[i]]]++] = i;
        //@if table

        int levels = 1;
        while ((2 << (levels - 1)) < n) levels++;
        table.assign((size_t)levels * n, 0);
        for (int i = 1; i < n; i++) table[i] = pos[par[order[i]]];
        for (int j = 1; j < levels; j++) {
            int half = 1 << (j - 1);
            const int* below = &table[(size_t)(j - 1) * n];
            int* row = &table[(size_t)j * n];
            for (int i = 0; i + 2 * half <= n; i++) row[i] = below[i] < below[i + half] ? below[i] : below[i + half];
        }
        //@end
    }

    [[noreturn]] void bad(const char* name) const {
        throw out_of_range(string(name) + ": needs " + to_string(lo) + " <= node <= " + to_string(hi));
    }

    LEETCODE_NO_SANITIZE int lcaOf(int a, int b) const {
        //@if table
        if (a == b) return a;
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        int j = 31 - __builtin_clz(r - l);
        const int* row = &table[(size_t)j * n];
        int x = row[l + 1], y = row[r - (1 << j) + 1];
        return order[x < y ? x : y];
        //@else
        while (head[a] != head[b]) {
            if (dep[head[a]] > dep[head[b]]) a = par[head[a]];
            else b = par[head[b]];
        }
        return dep[a] < dep[b] ? a : b;
        //@end
    }

    // the node k steps above node (k <= its depth): a whole chain at a time
    LEETCODE_NO_SANITIZE int kthOf(int node, int k) const {
        while (true) {
            int h = head[node], d = pos[node] - pos[h];
            if (k <= d) return order[pos[node] - k];
            k -= d + 1;
            node = par[h];
        }
    }

    LEETCODE_NO_SANITIZE int distOf(int a, int b) const { return dep[a] + dep[b] - 2 * dep[lcaOf(a, b)]; }

    // of the three pairwise lcas two are equal and the third, the deeper one, is the median
    LEETCODE_NO_SANITIZE int medianOf(int a, int b, int c) const {
        int x = lcaOf(a, b), y = lcaOf(a, c), z = lcaOf(b, c);
        if (dep[y] > dep[x]) x = y;
        return dep[z] > dep[x] ? z : x;
    }

    LEETCODE_NO_SANITIZE bool above(int a, int b) const { return pos[a] <= pos[b] && pos[b] < pos[a] + sz[a]; }

    LEETCODE_NO_SANITIZE bool onPath(int a, int b, int node) const {
        return above(lcaOf(a, b), node) && (above(node, a) || above(node, b));
    }

    // the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    LEETCODE_NO_SANITIZE int nextOf(int a, int b) const {
        return above(a, b) ? kthOf(b, dep[b] - dep[a] - 1) : par[a];
    }

    LEETCODE_NO_SANITIZE int lowerPos(int s, int e, int x) const {  // first index in [s, e) with depthPos >= x
        while (s < e) {
            int m = (s + e) >> 1;
            if (depthPos[m] < x) s = m + 1;
            else e = m;
        }
        return s;
    }

    // @LCA_COST@ -- lowest common ancestor of a and b
    LEETCODE_NO_SANITIZE int lca(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("lca");
        return lcaOf(a, b);
    }

    // @LCA_COST@ -- number of edges on the path a..b
    LEETCODE_NO_SANITIZE int unweightedDist(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("unweightedDist");
        return distOf(a, b);
    }

    // O(1) -- edges from the root to node (the root is depth 0)
    LEETCODE_NO_SANITIZE int depth(int node) const {
        if (node < lo || node > hi) bad("depth");
        return dep[node];
    }

    // O(1) -- node's parent (-1 for the root)
    LEETCODE_NO_SANITIZE int parent(int node) const {
        if (node < lo || node > hi) bad("parent");
        return par[node];
    }

    // O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    LEETCODE_NO_SANITIZE int kthAncestor(int node, int k) const {
        if (node < lo || node > hi) bad("kthAncestor");
        if (k < 0) throw out_of_range("kthAncestor: needs k >= 0");
        return k <= dep[node] ? kthOf(node, k) : -1;
    }

    // O(1) -- is a an ancestor of b? (true when a == b)
    LEETCODE_NO_SANITIZE bool isAncestor(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("isAncestor");
        return above(a, b);
    }

    // O(1) -- number of nodes in node's subtree (node included)
    LEETCODE_NO_SANITIZE int subtreeSize(int node) const {
        if (node < lo || node > hi) bad("subtreeSize");
        return sz[node];
    }

    // O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    LEETCODE_NO_SANITIZE int countAtDepthInSubtree(int node, int d) const {
        if (node < lo || node > hi) bad("countAtDepthInSubtree");
        if (d < 0 || d + 1 >= (int)depthStart.size()) return 0;
        int s = depthStart[d], e = depthStart[d + 1], l = pos[node];
        return lowerPos(s, e, l + sz[node]) - lowerPos(s, e, l);
    }

    // @LCA_COST@ -- lca of a and b if the tree were rooted at r instead
    LEETCODE_NO_SANITIZE int lcaRootedAt(int r, int a, int b) const {
        if (r < lo || r > hi || a < lo || a > hi || b < lo || b > hi) bad("lcaRootedAt");
        return medianOf(a, b, r);
    }

    // O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    LEETCODE_NO_SANITIZE int parentRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("parentRootedAt");
        return node == r ? -1 : nextOf(node, r);
    }

    // O(log n) -- size of node's subtree if the tree were rooted at r
    LEETCODE_NO_SANITIZE int subtreeSizeRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("subtreeSizeRootedAt");
        if (node == r) return n;
        // r hangs below node: everything but the child holding r
        if (above(node, r)) return n - sz[kthOf(r, dep[r] - dep[node] - 1)];
        return sz[node];
    }

    // O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    // k >= 0
    LEETCODE_NO_SANITIZE int kthNodeOnPath(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("kthNodeOnPath");
        if (k < 0) throw out_of_range("kthNodeOnPath: needs k >= 0");
        int c = lcaOf(a, b), up = dep[a] - dep[c], total = up + dep[b] - dep[c];
        if (k > total) return -1;
        return k <= up ? kthOf(a, k) : kthOf(b, total - k);
    }

    // O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    LEETCODE_NO_SANITIZE int nextNodeOnPath(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nextNodeOnPath");
        return a == b ? -1 : nextOf(a, b);
    }

    // @LCA_COST@ -- does the path a..b pass through node? (a and b count)
    LEETCODE_NO_SANITIZE bool isOnPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("isOnPath");
        return onPath(a, b, node);
    }

    // @LCA_COST@ -- fewest edges from node to any node on the path a..b (0 if node is on it)
    LEETCODE_NO_SANITIZE int unweightedDistToPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("unweightedDistToPath");
        return distOf(node, medianOf(a, b, node));
    }

    // @LCA_COST@ -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    LEETCODE_NO_SANITIZE int unweightedDistBetweenPaths(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi)
            bad("unweightedDistBetweenPaths");
        int p = medianOf(a, b, c);  // where c's side meets the path a..b
        if (p != medianOf(a, b, d)) return 0;  // c and d meet it at different nodes, so c..d runs along it
        return distOf(p, medianOf(c, d, p));
    }

    // @LCA_COST@ -- the one node that lies on all three paths between a, b and c
    LEETCODE_NO_SANITIZE int median(int a, int b, int c) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi) bad("median");
        return medianOf(a, b, c);
    }

    // @LCA_COST@ -- the shared part of paths a..b and c..d as its two end nodes {p, q}, p first walking a -> b; p == q
    // if they share one node; {-1, -1} if they share none
    LEETCODE_NO_SANITIZE pair<int, int> pathIntersection(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("pathIntersection");
        int p = medianOf(a, b, c), q = medianOf(a, b, d);  // where c's side and d's side meet the path a..b
        if (p == q) return onPath(c, d, p) ? pair<int, int>{p, p} : pair<int, int>{-1, -1};
        return distOf(a, p) < distOf(a, q) ? pair<int, int>{p, q} : pair<int, int>{q, p};
    }

    // @PATH_COST@ -- every node on the path a..b, in order from a (K = how many)
    LEETCODE_NO_SANITIZE vector<int> pathNodes(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("pathNodes");
        int c = lcaOf(a, b), up = dep[a] - dep[c], len = up + dep[b] - dep[c] + 1;
        vector<int> out(len);
        int* p = out.data();
        for (int i = 0; a != c; a = par[a]) p[i++] = a;
        p[up] = c;
        for (int i = len - 1; b != c; b = par[b]) p[i--] = b;
        return out;
    }
};
'''


def fill(text, table, cm):
    how = (HOW_TABLE if table else HOW).split("\n")
    t = pick(text, table)
    t = t.replace("@HOW@", "\n".join(f"{cm} {line}" for line in how))
    t = t.replace("@BUILD_COST@", "O(n log n)" if table else "O(n)")
    t = t.replace("@LCA_COST@", "O(1)" if table else "O(log n)")
    t = t.replace("@PATH_COST@", "O(K)" if table else "O(K + log n)")
    return t


# ------------------------------------------------------------------------------------------------ for gen_tree.py
# The value templates (gen_tree.py) are the same layout and the same shape methods around a range structure: these
# hand out the pieces of the heavy-light text above, so there is one copy of that code.
def _between(text, start, end):
    a = text.index(start) + len(start)
    return text[a:text.index(end, a)]


def py_layout_body():
    """The constructor's body: from the edge list to self.par ... self.depthPos (uses edges, root; leaves n, lo, hi,
    order, pos, ... as locals too)."""
    return _between(fill(PY, False, "#"), "    def __init__(self, edges, root):\n", "\n    def _bad(")


def py_shape_methods():
    """_bad, the private helpers and every public shape method."""
    text = fill(PY, False, "#")
    return text[text.index("    def _bad("):]


def cpp_members():
    return _between(fill(CPP, False, "//"), "struct Tree {\n", "\n    // O(n) -- builds the layout")


def cpp_layout_body():
    """The constructor's body (uses edges, root; fills n, lo, hi and the layout arrays)."""
    return _between(fill(CPP, False, "//"), "int root) : root(root) {\n", "\n    }\n\n    [[noreturn]]")


def cpp_shape_methods():
    """bad, the private helpers and every public shape method (without the struct's closing brace)."""
    text = fill(CPP, False, "//")
    return text[text.index("    [[noreturn]] void bad("):text.rindex("};")]


def sources():
    out = {}
    for folder, kind, table in VARIANTS:
        py = header("#", folder, kind, table, "py") + "\n" + fill(PY, table, "#")
        cpp = (header("//", folder, kind, table, "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\n"
               "using ll = long long;\n\n" + FAST_NOTE + PRELUDE + fill(CPP, table, "//"))
        out[os.path.join(folder, "template.py")] = check_finished(py, f"{folder}/template.py")
        out[os.path.join(folder, "template.cpp")] = check_finished(cpp, f"{folder}/template.cpp")
    return out


def main():
    check = "--check" in sys.argv
    stale = []
    for rel, text in sources().items():
        path = os.path.join(DIR, rel)
        if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
            continue
        stale.append(rel)
        if not check:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(text)
    if check:
        for rel in stale:
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_shape.py writes (rerun it)")
        print(f"{len(stale)} stale tree shape files" if stale else "tree shape templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} tree shape files, {len(stale)} written")


if __name__ == "__main__":
    main()
