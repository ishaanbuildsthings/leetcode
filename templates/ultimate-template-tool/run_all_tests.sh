#!/usr/bin/env bash
# Run every check on every template, in parallel, and print one summary.
#
#   ./run_all_tests.sh              # everything (expect a few hours: ~14.6k range-query folders, ~6.7k set folders)
#   ./run_all_tests.sh --py         # Python only (no compiler needed, much faster)
#   ./run_all_tests.sh --cpp        # C++ only (template.cpp, sparse / letters versions, and fast.cpp)
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
for sub in ("range-queries", "sets", "union-find", "strings", "next-permutation"):
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
    fi
done
run range-letters python3 range-query-tests/test_templates.py --letters --py
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
run union-find python3 union-find-tests/test_union_find.py "${LANGS[@]}"
run strings python3 string-tests/test_strings.py
run palindromes python3 string-tests/test_palindromes.py

echo
echo "================ SUMMARY ($(( $(date +%s) - START ))s, logs in $LOGS/)"
FAILS=$(grep -h "^FAIL\|Traceback\|Error:" "$LOGS"/*.log | sort -u)
NONZERO=$(awk '$2 != 0 {print $1 " (exit " $2 ")"}' "$LOGS/exit-codes.txt")
for f in "$LOGS"/*.log; do printf "%-22s %s\n" "$(basename "$f" .log)" "$(grep -v '^PASS' "$f" | grep -v '^$' | tail -1 | cut -c1-110)"; done
if [ -n "$FAILS$NONZERO" ]; then
    echo; echo "FAILURES:"; echo "$FAILS" | head -100; [ -n "$NONZERO" ] && { echo "jobs that exited non-zero:"; echo "$NONZERO"; }; exit 1
fi
echo; echo "everything passed"
