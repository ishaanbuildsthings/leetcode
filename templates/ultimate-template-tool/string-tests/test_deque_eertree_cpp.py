# Strips DequeEertree.cpp once per link structure (every op kept), compiles test_deque_eertree.cpp against it with the
# sanitizers and runs its brute-force checks: python3 test_deque_eertree_cpp.py
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eertree_strip import strip

OPS = ["append", "appendLeft", "pop", "popLeft", "numDistinctPals", "numPalsTotal", "longestPalEndingAtCurrentR",
       "longestPalStartingAtCurrentL", "longestPal", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL"]
src = open(os.path.join(HERE, "..", "strings", "DequeEertree.cpp")).read()
work = tempfile.mkdtemp()
try:
    shutil.copy(os.path.join(HERE, "test_deque_eertree.cpp"), work)
    for link in ["quickLinks", "itemLinks", "persistentLinks"]:
        open(os.path.join(work, "deque_eertree_under_test.cpp"), "w").write(strip(src, set(OPS) | {link}))
        exe = os.path.join(work, "t")
        subprocess.run(["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-fsanitize=address,undefined",
                        os.path.join(work, "test_deque_eertree.cpp"), "-o", exe], check=True)
        out = subprocess.run([exe], capture_output=True, text=True)
        assert out.returncode == 0, (link, out.stdout[-2000:], out.stderr[-2000:])
        print(link, out.stdout.strip().splitlines()[-1])
finally:
    shutil.rmtree(work)
