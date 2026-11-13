# Tree query templates: spec

The menu is `site/lib/tree-query-picker.ts`. This file says how every op on it gets a template. Built so far: the
shape templates and the node-, edge- and both-value templates (steps 1 to 3 in section 9).

## 1. Input (every template)

`Tree(edges, root, vals)`: `root` required, `vals` optional.

- `edges`: `[(a, b)]`, or `[(a, b, w)]` when edges carry a weight. An edge's weight is its value.
- Nodes are `0..n-1` or `1..n`, found from the smallest label in the edge list (from `root` when there are no edges).
- `vals[node]` is node's value: length `n` when 0-indexed, `n + 1` when 1-indexed (`vals[0]` ignored).
- Checked at build: every edge has the same length (2 or 3); `len(vals)` is the largest label + 1.
- All traversals are iterative (no recursion anywhere).

## 2. How a tree op becomes a range op

One heavy-light pass lays the nodes out in an array `pos[node]` so that:

- every heavy chain is one contiguous stretch, and
- every subtree is one contiguous stretch `[pos[node], pos[node] + size[node] - 1]`.

One range structure is built over that one array (a second one for edge values, each edge stored at its child end).

| Tree op | Becomes |
|---|---|
| one node / one edge | a point op at `pos` (an edge: at its deeper end, so `(a, b)` and `(b, a)` both work) |
| subtree of node | one range op (edge values: the same stretch without `pos[node]`) |
| path a..b | O(log n) range ops, one per chain piece (edge values: the piece holding the LCA skips the LCA) |

A generated tree file holds the range template's class, copied unchanged, then a `Tree` class that owns one and
translates calls. Complexity: subtree and one-node ops cost what the range op costs; path ops cost it times log(n).

## 3. Path ops: how the pieces combine

`a -> lca` pieces run against array order, `lca -> b` pieces run with it. That decides which range op each piece calls.

| Path op family | Per piece | Combine |
|---|---|---|
| Sum, SumMod, XOR, counts (`CountLtX`...), sums by value (`SumLtX`...), `CountOccurrences` | same range op | add (xor) |
| Min, Max, Gcd, AND, OR, nearest to x, Max/MinXorAgainstX | same range op | min / max / gcd / and / or |
| Assign, Add, Chmax, Chmin, XOR/OR/AND apply, AddMod, MultMod, AffineMod | same range update on every piece | none |
| AddArithSeq | `rangeAddArithSeq` with `+step` on with-order pieces, `-step` (from the far end) on against-order pieces | none |
| Hash, HashReversed, IsPalindrome, PathsEqual | `rangeHash` on with-order pieces, `rangeHashReversed` on against-order pieces | hash concatenation (needs each piece's length) |
| First / Last search (Gte, Gt, Lte, Lt, Eq), NearestAncestor | pieces in walking order; `leftmost...` on with-order pieces, `rightmost...` on against-order ones | first piece that answers |
| Max / Min prefix and suffix sum | `rangeSum` + `maxPrefixSum` (or `maxSuffixSum` on against-order pieces) | running sum + best |
| First prefix-sum / last suffix-sum searches | piece sum, then the range search inside the piece that crosses | running sum |
| AllEvenFrequency | random key per value, XOR over the path is 0 | xor |

## 4. What wrapping cannot do: dedicated templates

| Family | Method | Cost per op | Limits |
|---|---|---|---|
| Shape ops (no values) | heavy-light arrays: lca, kthAncestor, kthNodeOnPath, median, isOnPath, dist-to-path, path intersection, rooted-at-r forms; `countAtDepthInSubtree` by a per-depth list of positions | log(n) | none. Also a binary-lifting variant and an O(1)-lca variant (Euler tour + sparse table) to rank against |
| Path Sum / XOR, single log | Fenwick tree on the Euler tour (value at entry, minus at exit) | log(n) | one-node updates, or path/subtree add with one-node reads |
| Path Sum / XOR / Hash, no updates | prefix from the root | lca cost | static |
| Path Min / Max, no updates | sparse table over the layout | log(n) | static |
| Path KthSmallest / KthLargest, SumSmallestK, SumKth...Range, SumAbsDiffToMedian, and single-log counts / sums by value | persistent segment tree, one version per node (its root path); answer from versions a, b, lca, parent(lca) | log(U), or log(n) with values known up front | static |
| The same with one-node updates | Fenwick tree of value trees over the Euler tour | log(n)*log(U) | one-node assign / add only |
| Path MaxSubarraySum / MinSubarraySum, LongestEqualRun | heavy-light + segment tree whose merge knows direction | log^2(n) | with one-node or path assign / add |
| Path CountDistinct, AllDistinct | heavy-light + segment tree of bitsets, one bit per distinct value; a node's bitset is the OR of its children | log^2(n) * D/64 per query (D = distinct values) | memory about 2 * n * D / 8 bytes, so for up to a few thousand distinct values. Updates: one-node assign, path / subtree assign (not add). Values need not be known up front: each new value gets the next free bit, so only a cap on how many distinct values can ever appear (C++: a constructor argument; Python ints grow by themselves) |
| SubtreeAddByDepth | two coefficient arrays (`A + B * depth`) | log(n) | reads: one node, subtree sum, path sum (not min / max) |
| Subtree anything | none needed: one range op | the range op's cost | whatever the range template supports |

## 5. Node and edge values together

- A `both-` template: node values and edge weights in one `Tree`, two copies of one range structure over one layout
  (section 9, step 3). It needs one structure that covers both sides' ops.
- Where no single structure does, use a node- template and an edge- template side by side, built from the same edge
  list: node values and edge weights never affect each other.

## 6. Size

| Part | Folders |
|---|---|
| Node-value templates (one per structure type and set of tree ops) | 1,192 today (grows as more path ops are covered) |
| Edge-value templates | 1,192 today |
| Node values + edge weights in one Tree (both-) | 1,192 today |
| Dedicated (section 4) | 40 to 60 |

Each folder: `template.py` and one `template.cpp`. For scale: range queries are 14,760 folders, sets 6,734.

### One C++ file, fast by default

Range fast mode changes no logic: it marks the methods `LEETCODE_NO_SANITIZE` and makes the member vectors
`HotVector`. So a tree folder has one C++ file, built from the range folder's `fast.cpp` (from `template.cpp` for the
few range folders with no fast version), with the `Tree` class's own methods marked the same way. Its header says:

- this is fast mode: sanitizers are skipped inside the template, so a bad access in it goes unreported;
- to turn that off (when debugging with sanitizers), put `#define LEETCODE_NO_SANITIZE` above the template;
- it needs GCC or Clang.

Measured without sanitizers (g++-15 -O2, 3,000,000 mixed rangeAdd / rangeSum / rangeMin on n = 200,000, three runs
each): `template.cpp` 427 / 408 / 409 ms, `fast.cpp` 423 / 409 / 411 ms, same answers. One template, one compiler.

## 7. Generator and the dependency on range templates

- `tree-query-tests/gen_tree.py` reads each range template (its `@operations`, `@complexities`, `@memory` header and
  its class), and writes the tree folder. The tree-op -> range-op table lives in that one file.
- A range template's bug fix or speed-up: rerun `gen_tree.py`; the tree files pick it up.
- A range op renamed, or a constructor changed: update the table in `gen_tree.py`, rerun.
- Nothing fails silently: each generator's `--check` (run by `run_all_tests.sh`) fails when a tree file differs from
  what the generator makes now, and the generator stops with the op's name when a range op it needs is gone.

## 8. Tests

- Brute force: a plain parent-pointer tree that walks every path and subtree.
- Shapes: random, chain, star, caterpillar, binary, one node; both labelings; both value targets.
- Every tree op against every range structure family that backs it; all folders in the full run.
- A 100,000-node chain in Python for every shell, to prove no recursion.
- `test_tree.py --ordered`: the direction stress test. A wrong reading direction for one chain piece (in a search, a
  prefix sum, the best stretch, an arithmetic-sequence add) changes about one answer in a hundred even on trees built
  to show it, so a few folders that between them have every ordered op get 150 trials each on nested-chain trees,
  nearly every op an ordered one. After changing a generator, break it on purpose and check a test notices.

## 9. Order of work

1. Shape templates. DONE: `shape-heavy-light` (O(n) memory, log per op) and `shape-heavy-light-lca-table` (O(1) lca,
   n log n memory), written by `tree-query-tests/gen_tree_shape.py`, tested by `tree-query-tests/test_tree_shape.py`,
   on the site through `npm run gen:tree-queries`. No binary-lifting variant: heavy-light matches its cost per op with
   less memory.
2. Node-value templates. DONE: `tree-query-tests/gen_tree.py` writes `tree-queries/node-<range folder>/` (1,192 folders:
   one per structure type and set of tree ops, from the lightest range folder that gives it), tested by
   `tree-query-tests/test_tree.py` against a plain-tree brute force that reuses the range tests' op semantics.
   Every value template also has every shape op (the layout is already there; `SHAPE_OPS` in `gen_tree.py`).
   - Covered: one node (get, assign, add, chmax, chmin); every subtree update and query the range template has; on a
     path: the uniform updates, the arithmetic-sequence add, Sum / Min / Max / Gcd / XOR / AND / OR, counts and sums by
     value, nearest to x, max / min xor against x, max / min prefix and suffix sums, the prefix-sum searches, First /
     Last / NearestAncestor searches, and max / min subarray sum (each piece gives its sum, best prefix, best suffix
     and best inner stretch: four range ops a piece), and hashing: Hash, HashReversed, IsPalindrome, PathsEqual (each
     piece gives its hash, or its reversed hash when read backwards, and the pieces are joined the way the range
     structure joins two halves, hash(A then B) = hash(A) * base^len(B) + hash(B), with its own base and modulus, so a
     path's hash equals the range structure's hash of the same values).
   - Not wrapped: the by-rank ops, AllEvenFrequency, CountDistinct / AllDistinct and the longest equal run on a path
     (they need more than the range template's public answers), and SubtreeAddByDepth. Each has its own template:
     steps 4 to 8. Range folders left out: those whose constructor takes something a Tree cannot pass through
     (brackets, an update list, a stride cutoff), that split their ops over two classes, or that only have updates
     (nothing would read a value back: the range versions rely on getAll, which the tree menu does not have).
2b. Edge-value templates. DONE: the same generator with the edge target writes `tree-queries/edge-<range folder>/` (1,192
   folders, the same coverage as the node ones). `Tree(edges, root)` with `[(a, b, w)]`; each edge's weight sits at its
   lower end's position, so a path's lca piece starts one past the lca and a subtree skips its own top. One edge is
   named `(a, b)` in either order; a search returns an edge as its lower end. With no edges to look at (a path a..a,
   a leaf's subtree) a query answers its neutral value, written in its own comment (`EMPTY` in `gen_tree.py`): 0 for
   sums, counts, xor, OR and gcd; +inf / -inf (C++: the type's largest / smallest value) for min / max; None / nullopt
   for nearest-to-x; -1 for AND; True for the all-distinct / all-even checks; -1 for searches. Queries with no neutral
   value (kth smallest, sum of the k smallest, mode, sum of |weight - median|) raise.
3. Node values and edge weights together. DONE, wider than first planned: `tree-queries/both-<range folder>/`, one per
   range folder that makes a node- folder (1,192). One `Tree(edges, root, vals)`, one layout, two copies of the same
   range structure (`nodeSeg`, `edgeSeg`), every node op and every edge op that structure gives. So a mixed selection
   is covered whenever one structure can do both sides, not only for the common ops; the cost is that the two sides
   cannot have different structures (a lighter one for the side that needs less). Pairing two different structures
   would be the square of the count and would need their classes and helpers renamed apart. The picker offers a both-
   template only when both a node op and an edge op are picked.
4. Single-log path sum / xor with one-value updates. DONE: `tree-queries/path-{sum,xor}-fenwick-{node,edge}` from
   `tree-query-tests/gen_tree_fenwick.py`: each value sits at its node's position in a Fenwick tree and is taken back
   just past that node's subtree, so a prefix is a root path and a path is two prefixes minus the part above the lca.
   Get / assign / add / chmax / chmin on one node or edge, path sum (or xor), subtree sum (or xor), all O(log n).
   The `path-even-fenwick-*` pair is the xor one over random keys (a key per distinct value, an even number of equal
   values xors to 0): PathAllEvenFrequency and SubtreeAllEvenFrequency, with the same one-value updates.
   Not yet: the static prefix-from-root and sparse-table versions, and path add with one-node reads.
5. By-rank on a path. DONE for fixed values: `tree-queries/path-rank-node` and `path-rank-edge`, written by
   `tree-query-tests/gen_tree_rank.py` (a persistent seg tree with a version per node: its path from the root; a path is
   `ver[a] + ver[b] - ver[lca] - ver[parent(lca)]`, for edges `ver[a] + ver[b] - 2 * ver[lca]`). Kth smallest / largest,
   sum of the k smallest / largest, sum of a rank range, sum of |value - median|, and in one log the counts and sums by
   value, nearest to x, sum, min, max. The same with updates: step 9.
6. Count distinct on a path. DONE: `tree-queries/path-distinct-bitset-node` and `path-distinct-bitset-edge`, written
   by `tree-query-tests/gen_tree_bitset.py`: a segment tree over the positions whose nodes each hold a bitset, one bit
   per distinct value under the node (a parent is the OR of its children). A path ORs the O(log n) nodes of each of
   its O(log n) chain pieces and counts the bits: O(log^2 n * D / 64) for D distinct values, 2 * n * D / 8 bytes, so
   for up to a few thousand distinct values. PathCountDistinct / PathAllDistinct, the same two on a subtree
   (O(log n * D / 64)), get / assign / add / chmax / chmin on one node or edge, and PathAssign / SubtreeAssign (lazy:
   a tree node's tag is the bit everything under it became; no path add, which would move every value to a new bit).
   A value gets its bit the first time it appears; C++ takes `distinctCap` (how many distinct values can ever appear:
   it sizes the bitsets, default the ones in the input) and throws `length_error` past it, Python ints grow by
   themselves. A bit is never handed back, so D counts every value that ever appeared. The site ranks the new cost
   factor `D/64` as 16 words. Measured in C++: 200,000 nodes, 1,000 distinct values, 100,000 mixed path assigns and
   path counts in about 0.2 to 0.4 s.
7. Longest equal run on a path. DONE: `tree-queries/path-run-node` and `path-run-edge`, written by
   `tree-query-tests/gen_tree_run.py`. Wrapping cannot give it: a chain piece must also say how it starts and ends
   (its first and last value and how many equal values it starts and ends with), which `longestEqualRun` does not, and
   reading that out of each range structure's internals would tie the tree files to them. So: its own segment tree
   over the positions, a node holding (first, last, run at the start, run at the end, longest run, size); two
   summaries join in O(1) and a piece read backwards is the same numbers swapped. PathLongestEqualRun in O(log^2 n),
   with lazy PathAssign / PathAdd / SubtreeAssign / SubtreeAdd (an assign makes a node one run, an add moves its two
   end values) and get / assign / add / chmax / chmin on one node or edge. To mix it with other queries, keep a
   second Tree beside it. Measured in C++: 200,000 nodes, 200,000 mixed path updates and queries in 0.3 to 1 s.
8. SubtreeAddByDepth. DONE: `tree-queries/subtree-depth-add-fenwick-{node,edge}` and
   `subtree-depth-add-mod-fenwick-{node,edge}` (type `euler-fenwick`), written by `tree-query-tests/gen_tree_depth.py`.
   `test_tree.py` now also takes folders that start with `subtree-`, and `Sim.run` holds the brute force for the new
   update. Measured in C++: 200,000 nodes, 400,000 mixed updates and sums in 0.2 s (0.4 s with MOD).
   Everything O(log n), on five Fenwick trees over the positions:
   - An update adds `A + B * depth(u)` to every u in a stretch of positions `l..r` whose top is at depth `e`. Node
     template: `l = pos[x]`, `e = depth(x)`; edge template: `l = pos[x] + 1`, `e = depth(x) + 1` (an edge is kept at
     its lower end, so its k is `depth(lower end) - depth(x) - 1`). `SubtreeAddByDepth(x, start, step)` is
     `A = start - step * e`, `B = step`; `SubtreeAdd(x, c)` is `A = c`, `B = 0`.
   - `ca`, `cb`: difference trees, so a prefix sum is the A (the B) that applies at a position.
   - `sa`, `sb`: their partners for sums over positions: `sa` gets `A * l` at `l` and `-A * (r + 1)` at `r + 1`; `sb`
     gets `B * depSum[l]` and `-B * depSum[r + 1]` (`depSum[i]` = the depths at positions < i, summed). Then the
     sum of the values at positions <= k is
     `first[k + 1] + (k + 1) * ca(k) - sa(k) + depSum[k + 1] * cb(k) - sb(k)`. An add to one value alone goes into
     `base[v]` and into `sa` as `-x` at its position.
   - `up`: a difference tree for sums along the path from the root. With `tri(d) = d * (d + 1) / 2`, an update adds
     `A * (1 - e) - B * tri(e - 1)` on `l..r`, and an add of x to one value adds x on that node's whole subtree. Then
     `S(v) = rootSum[v] + up(p) + ca(p) * depth(v) + cb(p) * tri(depth(v))` is the sum on the path root..v, and a path
     sum is `S(a) + S(b) - S(lca) - S(parent(lca))` (edges: `S(a) + S(b) - 2 * S(lca)`).
   - One value: `base[v] + ca(p) + cb(p) * depth(v)`.
   - C++: intermediate products can pass 64 bits though the answer fits (A is about `-step * depth`), so the plain
     version computes in `unsigned long long` (wraps, exact mod 2^64) and the MOD version in `__int128` residues.
   - Ops: get / assign / add on one node or edge (plus chmax / chmin without MOD), SubtreeAdd, SubtreeAddByDepth,
     SubtreeSum, PathSum (the MOD folders: SubtreeAddMod, SubtreeAddByDepthMod, SubtreeSumMod, PathSumMod; values kept
     in [0, MOD)). No path updates: a path add would break the sums from the root that make the path sum one log.
9. By-rank on a path with one-value updates. DONE: `tree-queries/path-rank-updates-node` and `path-rank-updates-edge`,
   written by `tree-query-tests/gen_tree_rank_updates.py` (the public path ops are `gen_tree_rank.py`'s, over a list
   of trees instead of three or four versions). The starting values stay in the persistent tree (a version per node);
   changes go into a Fenwick tree over the positions whose nodes are value trees from the same node pool: changing v
   from old to new counts old one time less and new one time more from `pos[v]` on, and the opposite just past v's
   subtree, so the Fenwick trees through `pos[u]` correct the path root..u. A query walks the value range once over
   the 4 versions plus the 4 * O(log n) Fenwick trees: O(log n * log U). Values are not known up front, so the value
   range comes from `valLo` / `valHi` constructor arguments, as in the range templates (U is its size).
   Every by-rank and by-value path query of the fixed-value templates, plus get / assign / add / chmax / chmin on one
   node or edge.
   Memory is the catch, and the template says so with numbers. Measured in C++ at n = 2 * 10^5, U = 10^9: 124 MB to
   start, then about 500 new tree nodes (10 KB) an update, never freed, so 10^4 updates add 100 MB. Time is no issue
   (10^4 updates in 0.07 s, 2 * 10^4 queries in 0.02 s). An alternative with small memory (a value tree whose nodes
   hold ordered sets of positions) costs another log per query and much more code; not planned.
10. Still to do: the static path templates (prefix from the root, sparse table).

## 10. Decided

1. `PathMult` / `PathAffine` exist only with MOD (`...MultMod`, `...AffineMod`): the range side has no version
   without it. Add, AddArithSeq, AddByDepth and Sum keep the "with fixed MOD" checkbox.
2. Not on the menu: path Mode and path Mex (offline only: Mo's algorithm on the tree, every query up front), and Kth
   match. Subtree Mode and Mex stay (one range query).
3. Path CountDistinct / AllDistinct stay, on bitsets (section 4).
