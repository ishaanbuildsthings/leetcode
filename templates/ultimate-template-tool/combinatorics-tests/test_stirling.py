"""Tests combinatorics/Stirling.{py,cpp} the way the Math tab serves it: for each single op and for all four, the file
is trimmed to the ticked ops (string-tests/eertree_strip.py), then both classes are checked against the recurrence on
small inputs, under big primes and small ones (and a composite mod for the table, which works for any mod). Calls come
in random order so the table regrows in both directions. The C++ trims, built with sanitizers, must print the same.

    python3 test_stirling.py
"""
import math
import os
import random
import subprocess
import sys
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "string-tests"))
from eertree_strip import strip  # noqa: E402

SRC = os.path.join(os.path.dirname(HERE), "combinatorics")
# op id -> (class, method)
OPS = {
    "formulaIdentical": ("StirlingByFormula", "waysToPutDistinctItemsIntoIdenticalBucketsWithMod"),
    "formulaDistinct": ("StirlingByFormula", "waysToPutDistinctItemsIntoDistinctBucketsWithMod"),
    "tableIdentical": ("StirlingByTable", "waysToPutDistinctItemsIntoIdenticalBucketsWithMod"),
    "tableDistinct": ("StirlingByTable", "waysToPutDistinctItemsIntoDistinctBucketsWithMod"),
}


@lru_cache(None)
def s2(n, k):
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    return s2(n - 1, k - 1) + k * s2(n - 1, k)


def main():
    py = open(os.path.join(SRC, "Stirling.py")).read()
    cpp = open(os.path.join(SRC, "Stirling.cpp")).read()
    rnd = random.Random(3)
    sets = [[op] for op in OPS] + [list(OPS)]
    total = 0
    os.makedirs("/tmp/stirling-test", exist_ok=True)
    for chosen in sets:
        ns = {}
        exec(strip(py, set(chosen)), ns)
        body, want = [], []
        for op in chosen:
            cls, method = OPS[op]
            mods = [10**9 + 7, 998244353, 13, 7] + ([1000, 1] if cls == "StirlingByTable" else [])
            for mod in mods:
                obj = ns[cls](mod=mod)
                body.append(f"    {{ {cls} s({mod});")
                for _ in range(60):
                    items, buckets = rnd.randint(0, 25), rnd.randint(0, 12)
                    if cls == "StirlingByFormula" and buckets >= mod:
                        continue
                    allow = rnd.random() < 0.5
                    if "Distinct" in op:
                        exact = buckets ** items if allow else s2(items, buckets) * math.factorial(buckets)
                    else:
                        exact = sum(s2(items, j) for j in range(buckets + 1)) if allow else s2(items, buckets)
                    got = getattr(obj, method)(items, buckets, allow)
                    assert got == exact % mod, (op, mod, items, buckets, allow, got, exact % mod)
                    body.append(f"      cout << s.{method}({items}, {buckets}, {'true' if allow else 'false'}) << \"\\n\";")
                    want.append(str(got))
                    total += 1
                body.append("    }")
        name = chosen[0] if len(chosen) == 1 else "all"
        path = f"/tmp/stirling-test/{name}"
        open(path + ".cpp", "w").write(strip(cpp, set(chosen)) + "\nint main() {\n" + "\n".join(body) + "\n}\n")
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", path, path + ".cpp"], capture_output=True, text=True)
        if r.returncode or "warning" in r.stderr:
            sys.exit(f"FAIL cpp {name}: compile\n{r.stderr[:1500]}")
        got = subprocess.run([path], capture_output=True, text=True, timeout=120).stdout.split("\n")[:-1]
        if got != want:
            sys.exit(f"FAIL cpp {name}: output differs from python")
    print(f"python + cpp: both Stirling classes agree with the recurrence, every trim ({total} calls)")


if __name__ == "__main__":
    main()
