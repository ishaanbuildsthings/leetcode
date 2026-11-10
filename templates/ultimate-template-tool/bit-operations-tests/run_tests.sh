#!/bin/bash
# Runs every bit-operations stress test, Python and C++. Run from anywhere: bash run_tests.sh
set -e
cd "$(dirname "$0")"
out=$(mktemp -d)  # (its own folder: a /tmp file another user left can't block the build)
trap 'rm -rf "$out"' EXIT
cxx=$(python3 ../find_compiler.py)
for t in test_basis test_sos test_sums; do
    python3 $t.py
    "$cxx" -O2 -std=c++17 -Wall -Wextra -Werror $t.cpp -o "$out/$t"
    "$out/$t"
done
echo "all bit-operations tests passed"
