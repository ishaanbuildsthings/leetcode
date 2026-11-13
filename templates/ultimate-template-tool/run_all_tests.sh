#!/usr/bin/env bash
# Run every check on every template, in parallel, and print one summary.
#
#   ./run_all_tests.sh              # everything (expect a few hours: ~14.6k range-query folders, ~6.7k set folders)
#   ./run_all_tests.sh --py         # Python only (no compiler needed, much faster)
#   ./run_all_tests.sh --cpp        # C++ only (template.cpp, sparse / letters versions, fast.cpp, T = char)
#   JOBS=8 ./run_all_tests.sh       # parallel shards (default: number of CPU cores)
#
# Logs go to run_all_tests.logs/; the summary lists every FAIL line found in them. Exit code 0 means everything
# passed. Run it from a quiet checkout: a template being regenerated while its shard runs will show as a FAIL.
set -u
cd "$(dirname "$0")"
LANGS=("--py" "--cpp")
for a in "$@"; do case "$a" in --py) LANGS=("--py");; --cpp) LANGS=("--cpp");; esac; done
JOBS="${JOBS:-$( (nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4) )}"
LOGS=run_all_tests.logs
rm -rf "$LOGS" && mkdir -p "$LOGS"
START=$(date +%s)

run() {  # run <name> <command...>: one log per job, exit code recorded
    local name=$1; shift
    "$@" > "$LOGS/$name.log" 2>&1
    echo "$name $?" >> "$LOGS/exit-codes.txt"
}

echo "== syntax: every Python template must parse"
python3 - <<'PY' > "$LOGS/syntax.log" 2>&1
import ast, os, sys
bad = 0
for sub in ("range-queries", "sets", "union-find", "strings", "next-permutation", "tree-queries"):
    if not os.path.isdir(sub): continue
    for root, _, files in os.walk(sub):
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                try: ast.parse(open(p, encoding="utf-8").read())
                except SyntaxError as e: bad += 1; print(f"FAIL  {p}: {e}")
print(f"{bad} Python files with syntax errors" if bad else "all Python templates parse")
PY
tail -1 "$LOGS/syntax.log"

echo "== range queries: brute-force tests, $JOBS shards per language ($(ls range-queries | wc -l | tr -d ' ') folders)"
for lang in "${LANGS[@]}"; do
    for ((k = 0; k < JOBS; k++)); do
        run "range${lang}-$k" python3 range-query-tests/test_templates.py "$lang" --shard "$k/$JOBS" &
    done
    wait
    if [ "$lang" = "--cpp" ]; then
        for ((k = 0; k < JOBS; k++)); do
            run "range-fast-$k" python3 range-query-tests/test_templates.py --cpp --fast --shard "$k/$JOBS" &
        done
        wait
        for ((k = 0; k < JOBS; k++)); do  # the @letters: same and letters.cpp templates with T = char
            run "range-letters-cpp-$k" python3 range-query-tests/test_templates.py --letters --cpp --shard "$k/$JOBS" &
        done
        wait
    fi
done
if [[ " ${LANGS[*]} " == *" --py "* ]]; then  # the Python letters check, only when Python is chosen
    run range-letters python3 range-query-tests/test_templates.py --letters --py
fi
if [[ " ${LANGS[*]} " == *" --cpp "* ]]; then  # every fast.cpp matches what gen_fast.py makes from its source
    run range-fast-fresh python3 range-query-tests/check_fast_fresh.py
fi
run range-generic python3 range-query-tests/test_generic_fast.py
run range-catalog python3 range-query-tests/check_catalog.py

echo "== sets: brute-force tests, $JOBS shards per language ($(ls sets | wc -l | tr -d ' ') folders)"
for lang in "${LANGS[@]}"; do
    for ((k = 0; k < JOBS; k++)); do
        run "sets${lang}-$k" python3 set-tests/test_sets.py "$lang" --shard "$k/$JOBS" &
    done
    wait
done
run sets-catalog python3 set-tests/check_sets.py

echo "== union find, strings"
if [ "${#LANGS[@]}" -eq 2 ]; then run union-find python3 union-find-tests/test_union_find.py
else run union-find python3 union-find-tests/test_union_find.py "${LANGS[0]}"; fi
run strings python3 string-tests/test_strings.py
run palindromes python3 string-tests/test_palindromes.py

echo "== tree queries: brute-force tests, $JOBS shards per language ($(ls tree-queries | wc -l | tr -d ' ') folders)"
if [ "${#LANGS[@]}" -eq 2 ]; then run tree-shape python3 tree-query-tests/test_tree_shape.py
else run tree-shape python3 tree-query-tests/test_tree_shape.py "${LANGS[0]}"; fi
for lang in "${LANGS[@]}"; do
    for ((k = 0; k < JOBS; k++)); do
        run "tree${lang}-$k" python3 tree-query-tests/test_tree.py "$lang" --shard "$k/$JOBS" &
    done
    wait
done
# the direction stress test: a few folders, many nested-chain trees, nearly every op one whose answer depends on the
# order a path is read in (a wrong piece direction changes about one answer in a hundred)
if [ "${#LANGS[@]}" -eq 2 ]; then run tree-ordered python3 tree-query-tests/test_tree.py --ordered
else run tree-ordered python3 tree-query-tests/test_tree.py --ordered "${LANGS[0]}"; fi
# every tree file matches what its generator writes from the range templates as they are now
run tree-fresh-shape python3 tree-query-tests/gen_tree_shape.py --check
run tree-fresh-values python3 tree-query-tests/gen_tree.py --check
run tree-fresh-rank python3 tree-query-tests/gen_tree_rank.py --check
run tree-fresh-rank-updates python3 tree-query-tests/gen_tree_rank_updates.py --check
run tree-fresh-fenwick python3 tree-query-tests/gen_tree_fenwick.py --check
run tree-fresh-bitset python3 tree-query-tests/gen_tree_bitset.py --check
run tree-fresh-run python3 tree-query-tests/gen_tree_run.py --check
run tree-fresh-depth python3 tree-query-tests/gen_tree_depth.py --check

echo "== small folders: bit operations, matrices, bubble sort, generics, combinatorics, permutations, trees, bitset"
run generic-brute-py python3 range-query-tests/test_generic_brute.py
run matrices-py python3 matrices/tests/test_matrices.py
run bubble-sort python3 range-query-tests/test_bubble_sort.py
if [[ " ${LANGS[*]} " == *" --cpp "* ]]; then
    run bit-operations bash bit-operations-tests/run_tests.sh
    run generic-brute-cpp python3 range-query-tests/test_generic_brute_cpp.py
    run matrices-cpp bash -c 'out=$(mktemp -d) && "$(python3 find_compiler.py)" -std=c++17 -O2 matrices/tests/test_matrices.cpp -o "$out/t" && "$out/t"'
fi
if [ "${#LANGS[@]}" -eq 1 ] && [ "${LANGS[0]}" = "--py" ]; then run misc python3 misc-tests/test_misc.py --py
else run misc python3 misc-tests/test_misc.py; fi
run line-length python3 format_long_lines.py --check

echo
echo "================ SUMMARY ($(( $(date +%s) - START ))s, logs in $LOGS/)"
FAILS=$(grep -h "^FAIL\|Traceback\|Error:" "$LOGS"/*.log | sort -u)
NONZERO=$(awk '$2 != 0 {print $1 " (exit " $2 ")"}' "$LOGS/exit-codes.txt")
for f in "$LOGS"/*.log; do printf "%-22s %s\n" "$(basename "$f" .log)" "$(grep -v '^PASS' "$f" | grep -v '^$' | tail -1 | cut -c1-110)"; done
if [ -n "$FAILS$NONZERO" ]; then
    echo; echo "FAILURES:"; echo "$FAILS" | head -100; [ -n "$NONZERO" ] && { echo "jobs that exited non-zero:"; echo "$NONZERO"; }; exit 1
fi
echo; echo "everything passed"
