# 2D / 3D range query templates: spec

The menus are `site/lib/range-2d-picker.ts` (the "2D range queries" tab) and `site/lib/range-3d-picker.ts` (the "3D range
queries" tab, which reads the `3d-...` folders). This file says which structure covers which
ops, what is built, and what is left. Every folder here is written by a generator in
`../range-query-2d-tests/generators/`; nothing in a folder is edited by hand.

```
cd ../range-query-2d-tests/generators && python3 gen_all.py     # (re)write every folder     (--check: only compare)
cd .. && python3 test_templates_2d.py                           # brute-force test, Python then C++
python3 test_templates_2d.py --as-shipped                       # C++ again, built exactly as the files are served
python3 test_generic_2d.py                                      # the generic rectangle / square sparse tables
python3 bench_2d.py                                             # timings, built like LeetCode (-O2, sanitizers on)
cd ../../../site && npm run gen:range-queries-2d                # the picker's manifest + the copies it serves
```

## 1. The switch: what the constructor is given (`@input`)

| `@input` | Constructor | Coordinates | Costs in |
|---|---|---|---|
| `grid` | `(grid)`: R rows of C values. C++ also `(R, C)` where the template can change | 0-based `(r, c)` | R, C |
| `points` ("Compressed coordinates") | `points`: every (x, y) the point ops will use | points: listed ones only; rectangles and corners: any integers | N = distinct points |
| `online` | `(xLo, xHi, yLo, yHi)` | any integers in that range | U = size of a coordinate range |
| `grid-3d` | `(X, Y, Z)` | 0-based `(x, y, z)` | X, Y, Z |

Rectangles are inclusive and given as the low corner then the high corner: `rectSum(r1, c1, r2, c2)`,
`boxSum(x1, y1, z1, x2, y2, z2)`.

## 2. Empty cells (`@empty-cells: yes`)

- A template **with min or max** that can be updated has empty cells: a cell is empty until set (`None` in a Python
  grid; the C++ `(R, C)` constructor; every point of `points`, every cell of `online` / `grid-3d`). Queries only see set cells. A
  min / max over no set cell is `None` in Python and `NO_MIN` / `NO_MAX` in C++; a sum / gcd / xor / OR over none is 0;
  an AND over none is -1. `pointAdd`, `pointChmax`, `pointChmin` on an empty cell set it to `v`.
- A template **without min or max** has no empty cells: whatever was not given is the number 0 (so an AND over a
  rectangle holding a cell nobody set is 0).
- Static templates (sparse tables, tables, prefix sums) take full values: no empties.

The tester reads this from the tag, not from the op list.

## 3. C++ is fast by default

There is no slower twin: every `template.cpp` skips sanitizers inside itself, the same way the range query tab's fast
mode does (`lib2d.make_fast`, with that tab's own `LEETCODE_NO_SANITIZE` and `HotVector` text).

- Every method except the constructors starts with `LEETCODE_NO_SANITIZE`; vector members are `HotVector`.
- A function that skips sanitizers can't inline a standard-library call that doesn't, so inside the templates `min` /
  `max` are `hotMin` / `hotMax`, binary searches are `hotLowerBound` / `hotUpperBound`, and hot loops read raw pointers.
  Work a constructor would do on plain vectors is moved into a marked method (`fillLists`, `buildLevels`, `buildNode`).
- The drawback: a bad memory access inside a template goes unreported. Arguments are still checked and still throw.
- The tester would be blind with the skip on, so it builds with `-DLEETCODE_NO_SANITIZE=` (the templates only define the
  marker when nobody else has): sanitizers then look inside everything. `--as-shipped` builds the files as they are and
  must give the same answers.

`bench_2d.py`, g++ 13 at -O2 with address and undefined sanitizers on, milliseconds (before = fully sanitized):

| Case | Updates before → now | Queries before → now | Build before → now |
|---|---|---|---|
| grid seg tree, sum + max, 1000 x 1000, 200k assigns, 100k (max + sum) | 968 → 218 | 297 → 131 | 38 → 36 |
| grid Fenwick sum, 300k adds, 300k sums | 171 → 46 | 192 → 57 | 10 → 12 |
| grid rect chmax / rect max, 100k each | 2605 → 630 | 1159 → 407 | 102 → 104 |
| grid sparse table min, 400 x 400, 1M queries | | 157 → 65 | 179 → 67 |
| online seg tree max, +-10^9, 50k assigns, 50k queries | 9664 → about 3700 | 1490 → about 1050 | |
| 3D seg tree max, 60^3, 200k assigns, 200k queries | 1590 → 343 | 319 → 156 | |

With no sanitizers at all the ops take about the same time as "now" (the skip leaves nothing to gain there), except the
online tree's updates (2400), which still pay for sanitized vector growth.

## 4. Ops

| Group | Ops |
|---|---|
| Point | `pointGet`, `getAll`, `pointAssign`, `pointAdd`, `pointChmax`, `pointChmin` |
| Rectangle queries | `rectSum`, `rectMin`, `rectMax`, `rectGcd`, `rectXor`, `rectAnd`, `rectOr`; whole-grid `sumAll`, `minAll`, ... (O(1) wherever the structure can) |
| Corner queries | `sumLteLte(r, c)`, `sumLteGte`, `sumGteLte`, `sumGteGte`, the same four for `max` and `min`: one bound per axis |
| Rectangle updates | `rectAdd`, `rectAssign`, `rectChmax`, `rectChmin` |
| Hashing | `rectHash`, `rectsEqual(r1, c1, r2, c2, r3, c3)`, `hashAll` |
| 3D | `boxSum`, `boxMin`, `boxMax`, corners `sum/max/min` + `LteLteLte` / `GteGteGte`; the point ops with `(x, y, z)` |

Corner ops exist as their own ops so that a Fenwick tree or a plain table can win when a corner is all that's asked;
every segment tree with sum / min / max lists them too (same cost as a rectangle). On a Fenwick tree the all-<= sum is
one prefix walk instead of four.

## 5. What is built

Aggregate subsets: a segment tree family has one folder per non-empty subset of sum, min, max, gcd, xor, and, or (127),
each aggregate its own flat array, so asking for less costs less memory.

### Small grid (`grid`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `grid-prefix-{sum,xor,sum-xor}` | prefix table | rect sum / xor, point get | O(1) | 1 R·C each |
| `grid-difference-array` | marks at four corners | `rectAdd` O(1), then `getAll` O(R·C) | | 2 R·C |
| `grid-corner-table-{max,min}-<corners>` (30) | one table per corner direction | corner max / min | O(1) | 1 R·C per direction |
| `grid-hash` | prefix hash, one base per axis, mod 2^61 - 1, random bases | `rectHash`, `rectsEqual`, `hashAll` | O(1) | 1 R·C |
| `grid-bit-counts-{and,or,and-or}` | a prefix-count table per bit | rect AND / OR | O(bits) | bits · R·C |
| `grid-sparse-table-<aggs>` (31) | a table per (2^kr, 2^kc) | any rectangle, corners | O(1) | R·C·log R·log C each |
| `grid-bit-{sum,xor,sum-xor}` | 2D Fenwick | point updates, rect sum / xor | log R · log C | 2 R·C |
| `grid-bit-rect-add` | Fenwick over corner marks | `rectAdd`, point ops | log R · log C | 1 R·C |
| `grid-bit-rect-add-rect-sum` | four Fenwicks (mark, mark·row, mark·col, mark·row·col) | `rectAdd`, `rectSum`, point ops | log R · log C | 4 R·C |
| `grid-bit-corner-{max,min}-<corners>` (30) | Fenwick per corner direction | `pointChmax` (`pointChmin`) + corner max (min) | log R · log C | 1 R·C per direction |
| `grid-seg-tree-<aggs>` (127) | bottom-up tree over rows of bottom-up trees over columns, flat | point updates, any rectangle, corners | log R · log C | 4 R·C each |
| `grid-kept-tags-{max,min}` | tree of trees whose tags are never pushed down | `rectChmax` + `rectMax` (`rectChmin` + `rectMin`) | log R · log C | 16 R·C |

A Fenwick corner max only works because the value can only go up (`pointChmax`). An assign that can lower a value
needs the segment tree; the picker gets this from the ops picked.

### Compressed coordinates (`points`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `points-seg-tree-<aggs>` | a bottom-up tree over the distinct x's; each node keeps the sorted y's under it and a tree over just those | point updates, any rectangle, corners | log² N | N log N |
| `points-bit-sum`, `-xor`, `-sum-xor` | the same shape with Fenwick trees (lighter) | point updates, rectangle sum / xor, corners | log² N | N log N |
| `points-bit-corner-{max,min}-<corners>` | one Fenwick-of-Fenwicks per corner direction | `pointChmax` (`pointChmin`) + corner max (min) | log² N | N log N per direction |

The constructor takes every (x, y) a point op will use (`generators/gen_points.py`); a point op on anything else is
refused. Rectangles and corners take any integers and are never listed. Each point sits in log N x-nodes, one slot in
each, so memory is N log N however far apart the coordinates are. There are no rectangle updates here (a tag can't be
pushed down the outer tree): those are the small grid's, or online for rect chmax with point reads.

### Nothing known (`online`)

| Folders | Structure | Ops | Cost per op | Memory per update |
|---|---|---|---|---|
| `online-seg-tree-<aggs>` (127) | dynamic tree over x whose nodes each own a dynamic tree over y | point updates, any rectangle, corners | log² U | log² U nodes |

### 3D (`grid-3d`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `3d-seg-tree-<aggs>` (7: sum, min, max) | tree over x of trees over y of trees over z, flat | point updates, any box, all-<= / all->= corners (sum too) | log X · log Y · log Z | 8 X·Y·Z each |
| `3d-bit-sum` | 3D Fenwick | point updates, box sum, corner sums (all-<= is one prefix query) | log X · log Y · log Z | 2 X·Y·Z |
| `3d-bit-corner-{max,min}-<corners>` (6) | Fenwick per direction | `pointChmax` + corner max | log X · log Y · log Z | 1 X·Y·Z per direction |

### Generic (fill in Node, baseFn, combine): `../generic-2d/`

`GenericRectSparseTable` (any rectangle, R·C·log R·log C) and `GenericSquareSparseTable` (squares only, a single log): square queries are left to these.
They are in the "Generic seg trees" menu of the range query tab and the "Generic sparse tables" menu of the 2D tab.

## 6. Why rectangle updates split four ways

A tree of trees cannot push a tag down its outer tree: a row-node's tag would have to be merged into two whole column
trees. So:

| Ops | Structure | Cost |
|---|---|---|
| rect add + point get / rect sum | Fenwick over corner marks (built) | log² |
| rect chmax + rect max (chmin + min) | tags kept in place, read on the way down (built) | log² |
| any update + any query, short side small | one 1D lazy seg tree per row, looping the rows (not built) | R × the 1D cost |

Rect add with rect max has no log² structure here: only the last two rows cover it.

Online, rect chmax with point reads keeps its tags in place the same way (`online-kept-tags-*`, log² U).

## 7. Adding a family

1. A generator `gen_<family>.py` using `lib2d.py`: `header(...)` writes the tags, `write(folder, py, cpp)` the two files
   (it wraps long comments and refuses any other line over 120 columns). Add it to `gen_all.py`.
2. Costs: only factors in `site/scripts/catalog-lib.mjs` (`FACTORS`); a new one also goes in `FACTOR_VALUES` and
   `PRETTY_FACTORS` in `site/lib/template-picker.ts`.
3. New ops: add them to `OPS` and the brute force in `test_templates_2d.py`, and to the menu in
   `site/lib/range-2d-picker.ts`. A new structure type: `RANGE_2D_TYPES` there and `TYPES` in
   `site/scripts/build-range-2d-templates.mjs`.
4. Python and C++ must have the same ops and the same costs: the header is shared and the build compares them.
5. C++: write plain `vector` members and plain `min` / `max`; `write()` makes the file fast (section 3). Keep standard
   library calls and plain local vectors out of hot loops, and name a method `build` or `getAll` to leave it unmarked.
6. Every public method checks its arguments first (`IndexError` / `out_of_range`), and says so in its comment.
