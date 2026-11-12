"""Fails if any fast.cpp / sparse-fast.cpp / letters-fast.cpp is out of date with its source.

The fast versions are generated from template.cpp / sparse.cpp / letters.cpp by gen_fast.py, then wrapped by
format_long_lines.py. Editing a source without rerunning both leaves its fast copy stale. This reruns them on a
scratch copy of range-queries/ (the real folder is never written) and lists every fast file that would change.

    python3 check_fast_fresh.py     # exit 1 and one FAIL line per stale or missing fast file

Fix by running, from templates/ultimate-template-tool/:  python3 range-query-tests/gen_fast.py && python3 format_long_lines.py
"""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)
SRC = os.path.join(TOOL, "range-queries")
FAST = ("fast.cpp", "sparse-fast.cpp", "letters-fast.cpp")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "range-queries")
        # only the C++ files take part: the sources the generator reads and the fast files it writes
        shutil.copytree(SRC, work, ignore=lambda d, names: [n for n in names
                                                             if not os.path.isdir(os.path.join(d, n))
                                                             and not n.endswith(".cpp")])
        env = dict(os.environ, RANGE_DIR=work)
        gen = subprocess.run([sys.executable, os.path.join(HERE, "gen_fast.py")], env=env, capture_output=True,
                             text=True)
        if gen.returncode:
            print(gen.stdout[-2000:], gen.stderr[-2000:])
            print("FAIL  gen_fast.py crashed on the scratch copy")
            return 1
        # the formatter formats the folders beside its own file, so run a copy of it next to the scratch folder
        shutil.copy(os.path.join(TOOL, "format_long_lines.py"), tmp)
        fmt = subprocess.run([sys.executable, os.path.join(tmp, "format_long_lines.py")], capture_output=True,
                             text=True)
        if fmt.returncode:
            print(fmt.stdout[-2000:], fmt.stderr[-2000:])
            print("FAIL  format_long_lines.py crashed on the scratch copy")
            return 1
        stale, checked = [], 0
        for folder in sorted(os.listdir(work)):
            for name in FAST:
                fresh, committed = os.path.join(work, folder, name), os.path.join(SRC, folder, name)
                if os.path.exists(fresh) or os.path.exists(committed):
                    checked += 1
                if os.path.exists(fresh) != os.path.exists(committed):
                    stale.append(f"{folder}/{name}: {'missing' if os.path.exists(fresh) else 'no longer generated'}")
                elif os.path.exists(fresh) and not filecmp.cmp(fresh, committed, shallow=False):
                    stale.append(f"{folder}/{name}: out of date with its source")
    for line in stale:
        print(f"FAIL  {line}")
    if stale:
        print(f"{len(stale)} of {checked} fast files are stale: run range-query-tests/gen_fast.py, then "
              f"format_long_lines.py")
        return 1
    print(f"all {checked} fast files match their sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
