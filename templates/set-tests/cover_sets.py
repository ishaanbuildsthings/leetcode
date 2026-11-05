"""Pick a small sample of templates that still exercises every pair of features on every structure.

    python3 cover_sets.py avl fenwick > sample.txt     # only these structures (default: all)
    python3 test_sets.py --list sample.txt

Testing every template takes hours. A bug usually needs one feature, or two features interacting, so a sample where
each structure sees every feature pair (on and off) catches most breakage in minutes. The full run is still the last
step before merging.
"""
import itertools
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.environ.get("SETS_DIR") or os.path.join(os.path.dirname(HERE), "sets")
TYPES = ["blocks-fenwick", "value-tree", "fenwick", "blocks", "avl", "treap", "splay", "trie", "pbds", "fastset"]


def split(folder):
    dtype = next(t for t in TYPES if folder == t or folder.startswith(t + "-"))
    rest = folder[len(dtype):].removeprefix("-with").removeprefix("-")
    return dtype, set(rest.split("-")) - {""}


def pairs(feats, every):
    out = set()
    for a, b in itertools.combinations(every, 2):
        out.add((a, a in feats, b, b in feats))
    return out


def sample(folders):
    every = sorted(set().union(*(f for _, f in folders)))
    if len(every) < 2:
        return [n for n, _ in folders]
    left = set().union(*(pairs(f, every) for _, f in folders))
    keep = []
    rng = random.Random(0)
    pool = list(folders)
    rng.shuffle(pool)
    while left:  # greedy: take whichever template covers the most uncovered pairs
        name, feats = max(pool, key=lambda t: len(pairs(t[1], every) & left))
        left -= pairs(feats, every)
        keep.append(name)
    return keep


def main():
    want = sys.argv[1:] or TYPES
    groups = {}
    for f in sorted(os.listdir(DIR)):
        if os.path.isdir(os.path.join(DIR, f)):
            dtype, feats = split(f)
            groups.setdefault(dtype, []).append((f, feats))
    for dtype in want:
        chosen = sample(groups.get(dtype, []))
        chosen = sorted(set(chosen) | ({dtype} if any(n == dtype for n, _ in groups.get(dtype, [])) else set()))
        print("\n".join(chosen))
        print(f"{dtype}: {len(chosen)} of {len(groups.get(dtype, []))}", file=sys.stderr)


if __name__ == "__main__":
    main()
