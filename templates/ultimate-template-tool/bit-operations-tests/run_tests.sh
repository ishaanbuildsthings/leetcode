#!/bin/bash
# Runs every bit-operations stress test, Python and C++. Run from anywhere: bash run_tests.sh
set -e
cd "$(dirname "$0")"
for t in test_basis test_sos test_sums; do
    python3 $t.py
    g++ -O2 -std=c++17 -Wall -Wextra -Werror $t.cpp -o /tmp/bitops_$t
    /tmp/bitops_$t
done
echo "all bit-operations tests passed"
