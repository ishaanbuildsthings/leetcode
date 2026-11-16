"""Tests the generic 2D sparse tables (templates/ultimate-template-tool/generic-2d/*): their example Node (min and max)
is switched on, and every rectangle / square of random small grids is checked against a plain loop.

    python3 test_generic_2d.py          # Python, then C++
    python3 test_generic_2d.py --py     # Python only
    python3 test_generic_2d.py --cpp    # C++ only
"""
import os
import random
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "generic-2d")
sys.path.insert(0, os.path.dirname(HERE))
from find_compiler import cxx, sanitize_flags  # noqa: E402


def test_py(name, cls_name, square):
    ns = {}
    exec(open(os.path.join(DIR, name + ".py"), encoding="utf-8").read(), ns)
    rng = random.Random(name)
    for _ in range(300):
        R, C = rng.randrange(1, 9), rng.randrange(1, 9)
        grid = [[rng.randrange(-50, 50) for _ in range(C)] for _ in range(R)]
        st = ns[cls_name](grid, lambda v, r, c: (v, v), lambda a, b: (min(a[0], b[0]), max(a[1], b[1])))
        for r1 in range(R):
            for c1 in range(C):
                assert st.pointGet(r1, c1) == (grid[r1][c1],) * 2
                if square:
                    for side in range(1, min(R - r1, C - c1) + 1):
                        cells = [grid[r][c] for r in range(r1, r1 + side) for c in range(c1, c1 + side)]
                        assert st.squareQuery(r1, c1, side) == (min(cells), max(cells)), (grid, r1, c1, side)
                else:
                    for r2 in range(r1, R):
                        for c2 in range(c1, C):
                            cells = [grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
                            assert st.rectQuery(r1, c1, r2, c2) == (min(cells), max(cells)), (grid, r1, c1, r2, c2)
        if not square:
            assert st.rectQueryAll() == (min(map(min, grid)), max(map(max, grid)))
        for bad in ((-1, 0), (R, 0), (0, C)):
            try:
                st.pointGet(*bad)
                raise AssertionError("pointGet off the grid did not raise")
            except IndexError:
                pass
    print(f"ok    {name}.py")


MAIN = r"""
int main() {
    mt19937 rng(7);
    for (int it = 0; it < 300; it++) {
        int R = rng() % 8 + 1, C = rng() % 8 + 1;
        vector<vector<RawVal>> grid(R, vector<RawVal>(C));
        for (auto& row : grid) for (auto& x : row) x = (long long)(rng() % 100) - 50;
        CLASS st(grid);
        for (int r1 = 0; r1 < R; r1++) for (int c1 = 0; c1 < C; c1++) {
            if (st.pointGet(r1, c1).mn != grid[r1][c1]) return puts("FAIL pointGet"), 1;
            QUERIES
        }
        try { st.pointGet(R, 0); return puts("FAIL no throw"), 1; } catch (const out_of_range&) {}
    }
    puts("ok");
    return 0;
}
"""
RECT = """for (int r2 = r1; r2 < R; r2++) for (int c2 = c1; c2 < C; c2++) {
                long long mn = LLONG_MAX, mx = LLONG_MIN;
                for (int r = r1; r <= r2; r++) for (int c = c1; c <= c2; c++) mn = min(mn, grid[r][c]), mx = max(mx, grid[r][c]);
                Node got = st.rectQuery(r1, c1, r2, c2);
                if (got.mn != mn || got.mx != mx) return puts("FAIL rectQuery"), 1;
            }"""
SQUARE = """for (int side = 1; r1 + side <= R && c1 + side <= C; side++) {
                long long mn = LLONG_MAX, mx = LLONG_MIN;
                for (int r = r1; r < r1 + side; r++) for (int c = c1; c < c1 + side; c++) mn = min(mn, grid[r][c]), mx = max(mx, grid[r][c]);
                Node got = st.squareQuery(r1, c1, side);
                if (got.mn != mn || got.mx != mx) return puts("FAIL squareQuery"), 1;
            }"""


def test_cpp(name, cls_name, square):
    text = open(os.path.join(DIR, name + ".cpp"), encoding="utf-8").read()
    head, rest = text.split("\n// A static", 1)
    head = re.sub(r"^(\s+)// (?=\S.*;\s*$)", r"\1", head, flags=re.M)  # the example Node, baseFn and combine switched on
    src = head + "\n// A static" + rest + MAIN.replace("CLASS", cls_name).replace("QUERIES", SQUARE if square else RECT)
    with tempfile.TemporaryDirectory() as tmp:
        path, exe = os.path.join(tmp, "t.cpp"), os.path.join(tmp, "t")
        open(path, "w").write(src)
        comp = subprocess.run([cxx(), "-std=c++17", "-O1", "-Wall", *sanitize_flags(), "-o", exe, path], capture_output=True, text=True)
        if comp.returncode != 0:
            print(f"FAIL  {name}.cpp does not compile:\n{comp.stderr[:2000]}")
            return False
        run = subprocess.run([exe], capture_output=True, text=True)
        if run.returncode != 0 or run.stdout.strip() != "ok":
            print(f"FAIL  {name}.cpp: {run.stdout[-300:]} {run.stderr[-1500:]}")
            return False
    print(f"ok    {name}.cpp")
    return True


def main():
    ok = True
    for name, cls_name, square in (("GenericRectSparseTable", "RectSparseTable", False), ("GenericSquareSparseTable", "SquareSparseTable", True)):
        if "--cpp" not in sys.argv:
            test_py(name, cls_name, square)
        if "--py" not in sys.argv:
            ok = test_cpp(name, cls_name, square) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
