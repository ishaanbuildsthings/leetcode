# Strips Eertree.cpp for a spread of op subsets (all with and without append / pop, plus random ones), compiles each
# with the sanitizers and runs test_eertree_main.cpp's brute-force checks: python3 test_eertree_cpp.py
import os, random, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eertree_strip import strip
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from find_compiler import cxx, sanitize_flags  # noqa: E402

QUERIES = ["leftmostLForPalEndingAtR", "leftmostLForPalEndingAtEachR", "rightmostRForPalStartingAtL", "rightmostRForPalStartingAtEachL",
           "numDistinctPalsInPrefixEndingAtEachR", "numPalsEndingAtEachR", "numDistinctPals", "numDistinctPalsInPrefixEndingAtR",
           "numPalsEndingAtR", "numPalsTotal", "distinctPalsWithCounts", "minPalPartition", "longestPalEndingAtCurrentR",
           "longestPalStartingAtCurrentL", "longestPal", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL"]
src = open(os.path.join(HERE, "..", "strings", "Eertree.cpp")).read()
random.seed(1)
subsets = [set(QUERIES) | set(m) for m in ([], ["append"], ["pop"])]
subsets += [set(QUERIES) | {"append", "pop", tag} for tag in ("quickLinks", "itemLinks", "persistentLinks")]
subsets += [{q for q in QUERIES if random.random() < 0.5} | {m for m in ["append", "pop"] if random.random() < 0.5} | {random.choice(["quickLinks", "itemLinks", "persistentLinks"])} for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6)]
work = tempfile.mkdtemp()
try:
    shutil.copy(os.path.join(HERE, "test_eertree_main.cpp"), work)
    for chosen in subsets:
        open(os.path.join(work, "eertree_under_test.cpp"), "w").write(strip(src, chosen))
        flags = [f"-DHAS_{op}" for op in sorted(chosen)]
        exe = os.path.join(work, "t")
        subprocess.run([cxx(), "-std=c++17", "-O1", "-Wall", "-Wextra", *sanitize_flags(), *flags,
                        os.path.join(work, "test_eertree_main.cpp"), "-o", exe], check=True)
        out = subprocess.run([exe], capture_output=True, text=True)
        assert out.returncode == 0 and out.stdout.strip() == "ok", (sorted(chosen), out.stdout, out.stderr)
        print("ok", sorted(chosen))
finally:
    shutil.rmtree(work)
