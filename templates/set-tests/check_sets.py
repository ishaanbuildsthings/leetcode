"""Catalog checks for templates/sets: every op is covered, and no template is dominated by another.

    python3 check_sets.py

A dominates B when A supports every op B does, keeps no more current on every update (@tracks), needs no more
knowledge of the values up front (online <
online-range < offline), has a cost <= B's for each of B's ops and for the build, the same or a stronger guarantee
(worst case beats expected and amortized; expected and amortized don't compare), and memory <= B's; with at least
one of these strictly better. Python and C++ share headers.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.environ.get("SETS_DIR") or os.path.join(os.path.dirname(HERE), "sets")
sys.path.insert(0, os.path.join(HERE, "generators"))
from gen_sets import OPS  # noqa: E402

SIZES = {"N": 2e5, "U": 1e9, "Q": 2e5}
# Structures the user keeps as options although they lose to the AVL tree on paper (the value tree is often faster in
# practice; treap / splay / pb_ds are the classic alternatives). Losing on paper is reported for them, not a problem.
KEPT = {"value-tree", "treap", "splay", "pbds"}
KNOWLEDGE = {"online": 0, "online-range": 1, "online-bits": 1, "offline": 2}  # (bits: values in [0, 2^bits), a range too)


def value(expr):
    """'2*N*log(N)' -> a number for typical sizes."""
    total = 0.0
    for term in expr.split("+"):
        prod = 1.0
        for f in term.split("*"):
            f = f.strip()
            if re.fullmatch(r"\d+", f):
                prod *= int(f)
            elif f in SIZES:
                prod *= SIZES[f]
            elif f == "U/64":
                prod *= SIZES["U"] / 64
            elif f == "log64(U)":
                prod *= math.log2(SIZES["U"]) / 6
            else:
                m = re.fullmatch(r"log\^2\((\w)\)|log\((\w)\)|sqrt\((\w)\)", f)
                if not m:
                    raise ValueError(f"unknown factor {f!r} in {expr!r}")
                if m.group(1):
                    prod *= math.log2(SIZES[m.group(1)]) ** 2
                elif m.group(2):
                    prod *= math.log2(SIZES[m.group(2)])
                else:
                    prod *= math.sqrt(SIZES[m.group(3)])
        total += prod
    return total


def cost(c):
    """(number, guarantee) with guarantee in worst / expected / amortized."""
    kind = "worst"
    for k in ("amortized", "expected"):
        if c.endswith(" " + k):
            kind, c = k, c[: -len(k) - 1]
    return value(c), kind


def stronger_or_equal(a, b):
    return a == b or a == "worst"


def read(folder):
    for ext, cm in (("cpp", "//"), ("py", "#")):
        path = os.path.join(DIR, folder, f"template.{ext}")
        if os.path.exists(path):
            text = open(path).read()
            ops = re.search(rf"^{cm} @operations: (.*)$", text, re.M).group(1).split()
            vals = re.search(rf"^{cm} @values: (.*)$", text, re.M).group(1).strip()
            dtype = re.search(rf"^{cm} @data-structure-type: (.*)$", text, re.M).group(1).strip()
            tracks = set(re.search(rf"^{cm} @tracks: (.*)$", text, re.M).group(1).split()) - {"none"}
            comps = dict(re.findall(rf"^{cm}   (\w+): (.*)$", text, re.M))
            mem = sum(value(size) for size in re.findall(r"\w+\[([^\]]+)\]", "\n".join(
                line for line in text.split("\n") if re.match(rf"^{cm}   (node|tags|other): ", line))))
            if re.search(rf"^{cm}   layout: sparse", text, re.M):
                mem *= SIZES["Q"]  # a sparse value tree's memory is per add
            return dict(folder=folder, ops=set(ops), values=vals, comps=comps, mem=mem, dtype=dtype, tracks=tracks)
    return None


def main():
    temps = [t for t in (read(f) for f in sorted(os.listdir(DIR)) if os.path.isdir(os.path.join(DIR, f))) if t]
    problems, kept = [], []
    covered = set().union(*(t["ops"] for t in temps))
    for op in OPS:
        if op not in covered:
            problems.append(f"no template supports {op}")
    for b in temps:
        for a in temps:
            # keeping more current on every update (cached min / max, medians, mex) is never free, so a template that
            # tracks something b doesn't can't make b pointless
            if a is b or not b["ops"] <= a["ops"] or KNOWLEDGE[a["values"]] > KNOWLEDGE[b["values"]] or not a["tracks"] <= b["tracks"]:
                continue
            better, ok = False, True
            for key in sorted(b["ops"]) + ["build"]:
                ca, cb = cost(a["comps"][key]), cost(b["comps"][key])
                if ca[0] > cb[0] + 1e-9 or not stronger_or_equal(ca[1], cb[1]):
                    ok = False
                    break
                better |= ca[0] < cb[0] - 1e-9 or (ca[1] != cb[1])
            if not ok or a["mem"] > b["mem"] + 1e-9:
                continue
            better |= a["mem"] < b["mem"] - 1e-9 or a["ops"] > b["ops"] or KNOWLEDGE[a["values"]] < KNOWLEDGE[b["values"]]
            if better:
                (kept if b["dtype"] in KEPT else problems).append(f"{b['folder']} is dominated by {a['folder']}")
    for p in problems:
        print(p)
    dtype = {t["folder"]: t["dtype"] for t in temps}
    losers = {k.split(" ")[0] for k in kept}
    if losers:  # (per structure: thousands of folders would bury the problems)
        per = {d: sum(dtype[f] == d for f in losers) for d in sorted({dtype[f] for f in losers})}
        print("kept on purpose although they lose on paper: " + ", ".join(f"{d} ({k} variants)" for d, k in per.items()))
    print(f"{len(temps)} templates, {len(covered)} ops: " + ("all good" if not problems else f"{len(problems)} problems"))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
