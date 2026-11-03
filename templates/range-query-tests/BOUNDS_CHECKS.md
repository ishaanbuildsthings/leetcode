# Bounds checks on every index-taking method

## What happened

Solving CF 897C (Nephren) with the persistent treap template
(`templates/range-queries/append-appendLeft-copy-cut-...-trisect/template.cpp`), one query asked for
`pointGet(k - 1)` with `k = 10^18` on a 75-character array. That got **Time Limit Exceeded** instead of an error.

Why it hung instead of crashing:

- `locate(i)` walks down comparing `i` with the left subtree's size. With `i >= size()` it always goes right, and in
  O(log N) steps it reaches **node 0**, the "empty tree" sentinel.
- Node 0 is a real slot in the node arrays, with `L[0] = R[0] = 0` and `sz[0] = 0`, so nothing out of bounds is ever read
  and there's no segfault.
- At node 0 the loop does `i -= 1; t = R[0] = 0`, a self-loop that runs `i` times (10^18 here).
- With a small overshoot (e.g. `k = 100`) it returns `val[0]` (0 / `'\0'`) silently, which is worse: a wrong answer
  with no error.

The same thing can happen in any template that walks a tree with a sentinel node, or indexes arrays without checking. A
bad index should fail **immediately and loudly**, with a message saying what was expected.

## What I want

Every public method that takes an index, a range, a position or a count checks it up front, in **every template**
(range-queries, including sparse versions and letters versions, and the sets templates). This isn't just `pointGet`:
it's every method a user calls.

Convention (the sets templates already do this for rank ops, so match it):

- **C++:** `throw out_of_range("<method>: needs <rule>");`
- **Python:** `raise IndexError(f"<method>: needs <rule>, got <the values>")`
- The method's doc comment (shown in the site's usage panel) states the rule, e.g.
  `// O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range`.
- Check only in the public method, once, in O(1). No checks inside internal helpers or recursion. The hot path must not
  get slower beyond one or two comparisons.
- Don't change what valid calls return. Where a method already documents a "not found" value (-1, None / nullopt,
  `lo - 1` in sparse), that stays. This is only about **invalid arguments**, not empty results.

Rules, n = current length (sparse versions use their `[lo, hi]` instead of `[0, n - 1]`):

| method kind | rule |
|---|---|
| point ops (`pointGet`, `pointAssign`, `pointAdd`, `pointChmax`, `pointChmin`, ...) | `0 <= i < n` |
| range queries / updates / searches (`rangeSum`, `rangeAdd`, `leftmostGtX`, `countLtX`, `rangeReverse`, `rangeRotateLeft`, `rangeTwinSpin`, `cut`, `copy(l, r)`, ...) | `0 <= l <= r < n` |
| two ranges (`rangesEqual`, `rangeHash` pairs) | both ranges valid |
| insert positions (`insertAt`, `insertCopiesAt`, `paste(i, other)`) | `0 <= i <= n` |
| `split(k)` | `0 <= k <= n` |
| `trisect(l, r)` | `0 <= l <= r < n` |
| rank args (`kthSmallest`, `sumSmallestK`, `sumKth*Range`, `kthGtX` k, ...) | keep the existing rules (most already throw) |

If a method's existing doc deliberately allows something (e.g. an empty range, or `k` taking any value as in rotations,
where k is taken mod the length), keep that behavior and say so. Use judgment, but no input should silently loop or read
garbage.

## How

- **Edit the generators, never the generated files** (`templates/range-query-tests/generators/*.py` for the range
  templates, `templates/set-tests/generators/gen_sets.py` for sets). Hand-written templates with no generator get edited
  directly.
- After regenerating:
  - run `generators/gen_letters.py` last (the letters versions are derived from the templates);
  - run `python3 templates/range-query-tests/test_templates.py` (shard it in parallel; it's ~10k templates) and the
    sets tests;
  - run `npm run gen:range-queries` / `npm run gen:sets` in `code/leetcode/site`, then `npx tsc --noEmit -p .` and
    `python3 templates/range-query-tests/check_catalog.py`.
- Add harness coverage: for a sample of templates per family, call a few methods with out-of-range arguments and assert
  they raise (Python `IndexError`, C++ `out_of_range`) rather than hang or return.
- Keep lines at 120 columns max, and keep the comment style of the surrounding code.

## State of the repo you're starting from

- **Struct-per-node C++ treaps:** `generators/aos.py` (`aosify`) is now applied to the C++ output of
  `gen_treap_algebra.py`, `gen_treap_beats.py`, `gen_treap_more.py`, `gen_pair_algebra.py` and
  `gen_persistent_algebra.py`. It was benchmarked 1.4–1.9x faster.
  - The regeneration run that applies it was **interrupted**, so some treap folders may still be the old per-field
    version.
  - Regenerate those five generators, check every treap `template.cpp` has `struct Node`, then run the tests and the
    letters pass over the treap families.
  - Sorted runs (`gen_sorted_runs_cpp.py`, two node kinds) hasn't been converted yet.
- Nothing is committed; the user commits with `gacp` when told everything passes.
