"""Tests ModCalc (combinatorics/ModCalc.{py,cpp}) the way the Math tab serves it: for every single op, and for all of
them, the file is trimmed to the ticked ops (string-tests/eertree_strip.py, the site's rules), then checked against brute
force on small inputs, under a big prime mod and small ones (where Lucas and the x >= mod cases kick in). The C++ file
gets the same trims, built with sanitizers, and has to print exactly what the Python one does.

    python3 test_modcalc.py
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

OPS = ["getFactorialWithMod", "getInverseFactorialWithMod", "nChooseKWithMod", "nPermuteKWithMod",
       "interleaveTwoSequencesWithMod", "waysToPutIdenticalItemsIntoDistinctBucketsWithMod",
       "waysToPutDistinctItemsIntoDistinctBucketsWithMod", "modPow", "modInv"]
SRC = os.path.join(os.path.dirname(HERE), "combinatorics")
MODS = [10**9 + 7, 998244353, 7, 13, 2]
# ops another op's code calls, so ticking it keeps them too
NEEDS = {op: {"nChooseKWithMod"} for op in ["interleaveTwoSequencesWithMod", "waysToPutIdenticalItemsIntoDistinctBucketsWithMod",
                                         "waysToPutDistinctItemsIntoDistinctBucketsWithMod"]}


@lru_cache(None)
def stirling2(n, k):
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    return stirling2(n - 1, k - 1) + k * stirling2(n - 1, k)


def calls(rnd, op, mod):
    """(args, brute answer) pairs for op"""
    out = []
    for _ in range(40):
        a, b = rnd.randint(0, 30), rnd.randint(-2, 30)
        items, buckets = rnd.randint(0, 12), rnd.randint(0, 7)
        if op == "getFactorialWithMod":
            out.append(((a,), math.factorial(a) % mod))
        elif op == "getInverseFactorialWithMod":
            if a < mod:
                out.append(((a,), pow(math.factorial(a) % mod, mod - 2, mod)))
        elif op == "nChooseKWithMod":
            out.append(((a, b), (math.comb(a, b) if 0 <= b <= a else 0) % mod))
        elif op == "nPermuteKWithMod":
            out.append(((a, b), (math.perm(a, b) if 0 <= b <= a else 0) % mod))
        elif op == "interleaveTwoSequencesWithMod":
            c = rnd.randint(0, 20)
            out.append(((a, c), math.comb(a + c, a) % mod))
        elif op == "waysToPutIdenticalItemsIntoDistinctBucketsWithMod":
            allow = rnd.random() < 0.5
            if buckets == 0:
                want = 1 if items == 0 else 0
            else:
                want = math.comb(items + buckets - 1, buckets - 1) if allow else (math.comb(items - 1, buckets - 1) if items >= 1 else 0)
            out.append(((items, buckets, allow), want % mod))
        elif op == "waysToPutDistinctItemsIntoDistinctBucketsWithMod":
            allow = rnd.random() < 0.5
            want = buckets ** items if allow else math.factorial(buckets) * stirling2(items, buckets)
            out.append(((items, buckets, allow), want % mod))
        elif op == "modPow":
            base, e = rnd.randint(0, 50), rnd.randint(0, 40)
            out.append(((base, e), pow(base, e, mod)))
        elif op == "modInv":
            x = rnd.randint(1, 10**6)
            if x % mod:
                out.append(((x,), pow(x, mod - 2, mod)))
    return out


def main():
    py = open(os.path.join(SRC, "ModCalc.py")).read()
    cpp = open(os.path.join(SRC, "ModCalc.cpp")).read()
    rnd = random.Random(1)
    sets = [[op] for op in OPS] + [OPS]
    lines_in, lines_out = [], []
    for chosen in sets:
        ns = {}
        exec(strip(py, set(chosen)), ns)
        for mod in MODS:
            mc = ns["ModCalc"](mod=mod)
            for op in chosen:
                for args, want in calls(rnd, op, mod):
                    got = getattr(mc, op)(*args)
                    assert got == want, (chosen, mod, op, args, got, want)
                    lines_in.append((tuple(chosen), mod, op, args))
                    lines_out.append(str(got))
            kept = set(chosen).union(*(NEEDS.get(op, set()) for op in chosen))
            others = [m for m in OPS if m not in kept]
            assert not any(hasattr(mc, m) for m in others), (chosen, "kept an op that wasn't ticked")
    print(f"python: every op agrees with brute force, alone and all together ({len(lines_out)} calls)")

    exe_dir = "/tmp/modcalc-test"
    os.makedirs(exe_dir, exist_ok=True)
    k = 0
    for chosen in sets:
        code = strip(cpp, set(chosen))
        body = []
        mine = [(i, x) for i, x in enumerate(lines_in) if x[0] == tuple(chosen)]
        for _, (_, mod, op, args) in mine:
            arg = ", ".join(("true" if a else "false") if isinstance(a, bool) else str(a) for a in args)
            body.append(f"    {{ ModCalc mc({mod}); cout << mc.{op}({arg}) << \"\\n\"; }}")
        src = code + "\nint main() {\n" + "\n".join(body) + "\n}\n"
        name = chosen[0] if len(chosen) == 1 else "all"
        path = os.path.join(exe_dir, name + ".cpp")
        open(path, "w").write(src)
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", path[:-4], path], capture_output=True, text=True)
        if r.returncode or "warning" in r.stderr:
            sys.exit(f"FAIL cpp {name}: compile\n{r.stderr[:1500]}")
        got = subprocess.run([path[:-4]], capture_output=True, text=True, timeout=120).stdout.split("\n")[:-1]
        want = [lines_out[i] for i, _ in mine]
        if got != want:
            j = next(j for j in range(len(want)) if j >= len(got) or got[j] != want[j])
            sys.exit(f"FAIL cpp {name}: call {mine[j][1]} gave {got[j] if j < len(got) else 'nothing'}, python {want[j]}")
        k += 1
    print(f"cpp: all {k} trims compile cleanly and print what python does")


if __name__ == "__main__":
    main()
