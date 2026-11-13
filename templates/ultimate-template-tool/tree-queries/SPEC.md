# Tree query templates: spec

The menu is `site/lib/tree-query-picker.ts`. This file says how every op on it gets a template. Built so far: the
shape templates and the node-value templates (steps 1 and 2 in section 9).

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

- Any selection: two templates, one for the `node...` ops and one for the `edge...` ops, two objects built from the
  same edge list (the layout is built twice; node and edge values never affect each other).
- Common ops get one combined template (one `Tree` class, one layout, two range structures). Common = Get, Assign,
  Add, Chmax, Chmin on one node / edge, path, subtree, and Sum, Min, Max on path and subtree. That is 65 range
  structures, so 65 x 65 = about 4,200 combined folders.

## 6. Size

| Part | Folders |
|---|---|
| Node-value templates (one per structure type and set of tree ops) | 530 today (grows as more path ops are covered) |
| Edge-value templates | about the same |
| Combined node + edge (common ops) | about 4,200 |
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

## 9. Order of work

1. Shape templates. DONE: `shape-heavy-light` (O(n) memory, log per op) and `shape-heavy-light-lca-table` (O(1) lca,
   n log n memory), written by `tree-query-tests/gen_tree_shape.py`, tested by `tree-query-tests/test_tree_shape.py`,
   on the site through `npm run gen:tree-queries`. No binary-lifting variant: heavy-light matches its cost per op with
   less memory.
2. Node-value templates. DONE: `tree-query-tests/gen_tree.py` writes `tree-queries/node-<range folder>/` (530 folders:
   one per structure type and set of tree ops, from the lightest range folder that gives it), tested by
   `tree-query-tests/test_tree.py` against a plain-tree brute force that reuses the range tests' op semantics.
   Every value template also has every shape op (the layout is already there; `SHAPE_OPS` in `gen_tree.py`).
   - Covered: one node (get, assign, add, chmax, chmin); every subtree update and query the range template has; on a
     path: the uniform updates, the arithmetic-sequence add, Sum / Min / Max / Gcd / XOR / AND / OR, counts and sums by
     value, nearest to x, max / min xor against x, max / min prefix and suffix sums, the prefix-sum searches, First /
     Last / NearestAncestor searches.
   - Not yet (they need more than the range template's public answers): on a path: hashing, max / min subarray sum,
     longest equal run, the by-rank ops, SumAbsDiffToMedian, AllEvenFrequency, CountDistinct / AllDistinct; and
     SubtreeAddByDepth. Range folders left out: those whose constructor takes something a Tree cannot pass through
     (brackets, an update list, a stride cutoff), that split their ops over two classes, or that only have updates
     (nothing would read a value back: the range versions rely on getAll, which the tree menu does not have).
2b. Edge-value templates: the same generator with the edge target (each edge at its child end; a path's lca piece skips
   the lca, a subtree skips its own position).
3. Combined node + edge for the common ops.
4. Single-log and static dedicated templates.
5. Persistent path-rank family, direction-aware merges, SubtreeAddByDepth.
6. Bitset path CountDistinct / AllDistinct.

## 10. Decided

1. `PathMult` / `PathAffine` exist only with MOD (`...MultMod`, `...AffineMod`): the range side has no version
   without it. Add, AddArithSeq, AddByDepth and Sum keep the "with fixed MOD" checkbox.
2. Not on the menu: path Mode and path Mex (offline only: Mo's algorithm on the tree, every query up front), and Kth
   match. Subtree Mode and Mex stay (one range query).
3. Path CountDistinct / AllDistinct stay, on bitsets (section 4).
