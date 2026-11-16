# 2D / 3D range query templates: spec

The menu is `site/lib/range-2d-picker.ts` (the "2D range queries" tab). This file says which structure covers which
ops, what is built, and what is left. Every folder here is written by a generator in
`../range-query-2d-tests/generators/`; nothing in a folder is edited by hand.

```
cd ../range-query-2d-tests/generators && python3 gen_all.py     # (re)write every folder     (--check: only compare)
cd .. && python3 test_templates_2d.py                           # brute-force test, Python then C++
python3 test_generic_2d.py                                      # the generic rectangle / square sparse tables
cd ../../../site && npm run gen:range-queries-2d                # the picker's manifest + the copies it serves
```

## 1. The switch: what the constructor is given (`@input`)

| `@input` | Constructor | Coordinates | Costs in |
|---|---|---|---|
| `grid` | `(grid)`: R rows of C values. C++ also `(R, C)` where the template can change | 0-based `(r, c)` | R, C |
| `points` | `(points)`: every `(x, y)` that will ever be updated | any integers `(x, y)`, negative is fine | N = points given |
| `online` | `(xLo, xHi, yLo, yHi)` | any integers in that range | U = size of a coordinate range |
| `batch` | `()`; calls are recorded, `solve()` answers them all | any integers | N = calls recorded |
| `grid-3d` | `(X, Y, Z)` | 0-based `(x, y, z)` | X, Y, Z |

Rectangles are inclusive and given as the low corner then the high corner: `rectSum(r1, c1, r2, c2)`,
`boxSum(x1, y1, z1, x2, y2, z2)`.

## 2. Empty cells (`@empty-cells: yes`)

- A template **with min or max** that can be updated has empty cells: a cell is empty until set (`None` in a Python
  grid; the C++ `(R, C)` constructor; every point in `points` / `online` / `grid-3d`). Queries only see set cells. A
  min / max over no set cell is `None` in Python and `NO_MIN` / `NO_MAX` in C++; a sum / gcd / xor / OR over none is 0;
  an AND over none is -1. `pointAdd`, `pointChmax`, `pointChmin` on an empty cell set it to `v`.
- A template **without min or max** has no empty cells: whatever was not given is the number 0 (so an AND over a
  rectangle holding a cell nobody set is 0).
- Static templates (sparse tables, tables, prefix sums) and the k-d tree take full values: no empties. The k-d tree's
  points all start at 0; its min / max over a rectangle with no given point in it is still `None` / `NO_MIN` / `NO_MAX`.

The tester reads this from the tag, not from the op list.

## 3. Ops

| Group | Ops |
|---|---|
| Point | `pointGet`, `pointAssign`, `pointAdd`, `pointChmax`, `pointChmin` |
| Rectangle queries | `rectSum`, `rectMin`, `rectMax`, `rectGcd`, `rectXor`, `rectAnd`, `rectOr`; whole-grid `sumAll`, `minAll`, ... (O(1) wherever the structure can) |
| Corner queries | `maxLteLte(r, c)`, `maxLteGte`, `maxGteLte`, `maxGteGte`, and the four `min...`: one bound per axis |
| Rectangle updates | `rectAdd`, `rectAssign`, `rectChmax`, `rectChmin`, `getAll` |
| Squares / windows | `squareMin(r, c, side)` (also Max, Gcd, And, Or); `windowMin(r, c)`, `windowMax` for one h x w fixed at the build |
| Hashing | `rectHash`, `rectsEqual(r1, c1, r2, c2, r3, c3)`, `hashAll` |
| 3D | `boxSum`, `boxMin`, `boxMax`, `maxLteLteLte`, `maxGteGteGte`, `minLteLteLte`, `minGteGteGte`; the point ops with `(x, y, z)` |

Corner ops exist as their own ops so that a Fenwick tree or a plain table can win when a corner is all that's asked;
every segment tree with min / max lists them too (same cost as a rectangle).

## 4. What is built

Aggregate subsets: a segment tree family has one folder per non-empty subset of sum, min, max, gcd, xor, and, or (127),
each aggregate its own flat array, so asking for less costs less memory.

### Small grid (`grid`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `grid-prefix-{sum,xor,sum-xor}` | prefix table | rect sum / xor, point get | O(1) | 1 R·C each |
| `grid-difference-array` | marks at four corners | `rectAdd` O(1), then `getAll` O(R·C) | | 2 R·C |
| `grid-corner-table-{max,min}-<corners>` (30) | one table per corner direction | corner max / min | O(1) | 1 R·C per direction |
| `grid-window-{min,max,min-max}` | monotonic queue along rows, then columns | `windowMin/Max` for one h x w | O(1), build R·C | 1 R·C each |
| `grid-hash` | prefix hash, one base per axis, mod 2^61 - 1, random bases | `rectHash`, `rectsEqual`, `hashAll` | O(1) | 1 R·C |
| `grid-bit-counts-{and,or,and-or}` | a prefix-count table per bit | rect AND / OR | O(bits) | bits · R·C |
| `grid-square-sparse-table-<aggs>` (31) | level k = every 2^k x 2^k window | square min / max / gcd / AND / OR | O(1) | R·C·log(min(R, C)) each |
| `grid-sparse-table-<aggs>` (31) | a table per (2^kr, 2^kc) | any rectangle, squares, corners | O(1) | R·C·log R·log C each |
| `grid-bit-{sum,xor,sum-xor}` | 2D Fenwick | point updates, rect sum / xor | log R · log C | 2 R·C |
| `grid-bit-rect-add` | Fenwick over corner marks | `rectAdd`, point ops | log R · log C | 1 R·C |
| `grid-bit-rect-add-rect-sum` | four Fenwicks (mark, mark·row, mark·col, mark·row·col) | `rectAdd`, `rectSum`, point ops | log R · log C | 4 R·C |
| `grid-bit-corner-{max,min}-<corners>` (30) | Fenwick per corner direction | `pointChmax` (`pointChmin`) + corner max (min) | log R · log C | 1 R·C per direction |
| `grid-seg-tree-<aggs>` (127) | bottom-up tree over rows of bottom-up trees over columns, flat | point updates, any rectangle, corners | log R · log C | 4 R·C each |
| `grid-kept-tags-{max,min}` | tree of trees whose tags are never pushed down | `rectChmax` + `rectMax` (`rectChmin` + `rectMin`) | log R · log C | 16 R·C |

A Fenwick corner max only works because the value can only go up (`pointChmax`). An assign that can lower a value
needs the segment tree; the picker gets this from the ops picked.

### Points known up front (`points`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `points-bit-{sum,xor,sum-xor}` | Fenwick over the distinct x's; each node a Fenwick over the sorted y's it covers | point updates, rect sum / xor | log² N | ~2 N log N |
| `points-bit-corner-{max,min}-<corners>` (30) | the same per corner direction (>= is the structure on negated coordinates) | `pointChmax` + corner max | log² N | ~2 N log N per direction |
| `points-seg-tree-<aggs>` (127) | bottom-up tree over the distinct x's; each node a bottom-up tree over its sorted y's | point updates, any rectangle, corners | log² N | ~2 N log N each, + N log N |
| `points-kd-tree-<aggs>` (7: sum, min, max) | one tree over the points in k-d order, bounding boxes, lazy assign / add tags | `rectAdd`, `rectAssign` with rect sum / min / max; point ops | sqrt N per rectangle, log N per point | linear |

Point lookups are binary searches on sorted arrays (no hash maps: nothing to attack).

### Nothing known (`online`)

| Folders | Structure | Ops | Cost per op | Memory per update |
|---|---|---|---|---|
| `online-seg-tree-<aggs>` (127) | dynamic tree over x whose nodes each own a dynamic tree over y | point updates, any rectangle, corners | log² U | log² U nodes |

### Whole input known (`batch`)

| Folders | Structure | Ops | Cost | Memory |
|---|---|---|---|---|
| `batch-sum` | divide and conquer over time + one Fenwick over y | `pointAdd`, `rectSum` recorded, then `solve()` | log² N amortized | linear |

### 3D (`grid-3d`)

| Folders | Structure | Ops | Cost per op | Memory |
|---|---|---|---|---|
| `3d-seg-tree-<aggs>` (7: sum, min, max) | tree over x of trees over y of trees over z, flat | point updates, any box, all-<= / all->= corners | log X · log Y · log Z | 8 X·Y·Z each |
| `3d-bit-sum` | 3D Fenwick | point updates, box sum | log X · log Y · log Z | 2 X·Y·Z |
| `3d-bit-corner-{max,min}-<corners>` (6) | Fenwick per direction | `pointChmax` + corner max | log X · log Y · log Z | 1 X·Y·Z per direction |

### Generic (fill in Node, baseFn, combine): `../generic-2d/`

`GenericRectSparseTable` (any rectangle, R·C·log R·log C) and `GenericSquareSparseTable` (squares only, a single log).
They are in the "Generic seg trees" menu of the range query tab and the "Generic sparse tables" menu of the 2D tab.

## 5. Why rectangle updates split four ways

A tree of trees cannot push a tag down its outer tree: a row-node's tag would have to be merged into two whole column
trees. So:

| Ops | Structure | Cost |
|---|---|---|
| rect add + point get / rect sum | Fenwick over corner marks (built) | log² |
| rect chmax + rect max (chmin + min) | tags kept in place, read on the way down (built) | log² |
| any update + any query, points | k-d tree with lazy tags (built) | sqrt N |
| any update + any query, short side small | one 1D lazy seg tree per row, looping the rows (not built) | R × the 1D cost |

Rect add with rect max has no log² structure here: only the last two rows cover it.

## 6. Still to add

| What | How | Notes |
|---|---|---|
| One lazy seg tree per row (`grid`, type `rows-of-trees`) | copy a 1D lazy template's class unchanged, then a `Grid` class holding R of them (the tree-queries generators do the same kind of wrapping) | every 1D range update / query becomes a rect op at R × its cost |
| K-d tree over a small grid's cells | the points k-d tree with all R·C cells as points and a `(grid)` constructor | cost per rectangle is O(R + C) |
| Sparse table on rows × seg tree on columns | per power-of-two row block, a bottom-up column tree | static; log C per query with R·C·log R memory: between the seg tree and the full sparse table |
| 2D hashing with point updates | Fenwick or seg tree over `value · A^r · B^c`, a rectangle's hash scaled to its corner | log² per op |
| Fenwick of hash maps (`online`, sum and corner max) | outer / inner Fenwick indices as keys of one seeded hash map | lighter constant than the dynamic tree of trees; needs an unhackable hash in C++ |
| `batch`: corner max, point assign | sweep by x with a 1D Fenwick max; assign as an add of the difference | |
| `points`: starting values | `(points, values)` | today every point starts empty / 0 |
| C++ fast versions (`fast.cpp`) | the range query tab's fast mode | not started |

## 7. Adding a family

1. A generator `gen_<family>.py` using `lib2d.py`: `header(...)` writes the tags, `write(folder, py, cpp)` the two files
   (it wraps long comments and refuses any other line over 120 columns). Add it to `gen_all.py`.
2. Costs: only factors in `site/scripts/catalog-lib.mjs` (`FACTORS`); a new one also goes in `FACTOR_VALUES` and
   `PRETTY_FACTORS` in `site/lib/template-picker.ts`.
3. New ops: add them to `OPS` and the brute force in `test_templates_2d.py`, and to the menu in
   `site/lib/range-2d-picker.ts`. A new structure type: `RANGE_2D_TYPES` there and `TYPES` in
   `site/scripts/build-range-2d-templates.mjs`.
4. Python and C++ must have the same ops and the same costs: the header is shared and the build compares them.
5. Every public method checks its arguments first (`IndexError` / `out_of_range`), and says so in its comment.
