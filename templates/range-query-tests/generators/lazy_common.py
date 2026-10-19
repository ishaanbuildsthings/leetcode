"""Generate the 2N iterative lazy-tree family: node fields from {sum, min, max}, tags from {add, chmin, chmax, assign}.

Every variant is the same Al.Cash-style tree: values on leaves tree[n..2n), a tag on each internal node 1..n-1
meaning "applied here, not yet pushed to my children". An update pushes the tags on its two boundary root-to-leaf
paths, tags the O(log N) covering nodes, then rebuilds those two paths. Covering nodes are always perfect subtrees
of 2^level leaves, even when n is not a power of two, so a node's length is just 1 << level.
"""
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
FIELD_ARR = {"sum": "sm", "min": "mn", "max": "mx"}
FIELD_OP = {"sum": "rangeSum", "min": "rangeMin", "max": "rangeMax"}
FIELD_NAME = {("sum",): "Sum", ("min",): "Min", ("max",): "Max", ("min", "max"): "MinMax", ("sum", "min"): "SumMin",
              ("sum", "max"): "SumMax", ("sum", "min", "max"): "SumMinMax"}


def variants():
    out = []
    for fields in [("min",), ("max",), ("min", "max")]:
        for comps in ["C", "A", "B", "AB", "AC", "BC", "ABC"]:
            out.append(("clamp", fields, comps))
    for fields in [("sum",), ("sum", "min"), ("sum", "max"), ("sum", "min", "max")]:
        for tags in ["add", "assign", "add+assign"]:
            if fields == ("sum",) and tags == "add":
                continue  # two BITs do range add + range sum in 2N
            out.append(("sum", fields, tags))
    return out


def ops_of(kind, fields, tags):
    ops = set(POINT) | {FIELD_OP[f] for f in fields}
    if kind == "clamp":
        if "C" in tags: ops.add("rangeAdd")
        if "A" in tags: ops.add("rangeChmin")
        if "B" in tags: ops.add("rangeChmax")
        if "A" in tags and "B" in tags: ops.add("rangeAssign")
    else:
        if "add" in tags: ops.add("rangeAdd")
        if "assign" in tags: ops.add("rangeAssign")
    return sorted(ops)


def class_name(kind, fields, tags):
    if kind == "clamp":
        t = {"C": "Add", "A": "Chmin", "B": "Chmax", "AB": "ChminChmaxAssign", "AC": "AddChmin", "BC": "AddChmax", "ABC": "Clamp"}[tags]
    else:
        t = {"add": "Add", "assign": "Assign", "add+assign": "AddAssign"}[tags]
    return f"{t}{FIELD_NAME[fields]}Tree"


def tag_arrays(kind, tags):
    if kind == "clamp":
        return [{"A": "hi", "B": "lo", "C": "add"}[c] for c in "ABC" if c in tags]
    return (["add"] if "add" in tags else []) + (["asg", "hasAsg"] if "assign" in tags else [])


def header(cm, kind, fields, tags):
    ops = ops_of(kind, fields, tags)
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: lazy-seg-tree", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: log(N)" for o in ops] + [f"{cm}   build: N"]
    node = " ".join(f"{FIELD_ARR[f]}[2*N]" for f in fields)
    tagm = " ".join(f"{t}[1*N]" for t in tag_arrays(kind, tags))
    if kind == "clamp":
        what = "one clamp tag x -> " + {"C": "x + add", "A": "min(hi, x)", "B": "max(lo, x)", "AB": "min(hi, max(lo, x))",
                                        "AC": "min(hi, x + add)", "BC": "max(lo, x + add)", "ABC": "min(hi, max(lo, x + add))"}[tags]
    else:
        what = {"add": "a pending add", "assign": "a pending assign", "add+assign": "a pending assign or add (an add on an assigned node shifts the assigned value)"}[tags]
    lines += [f"{cm} @memory:", f"{cm}   layout: 2n-iterative", f"{cm}   node: {node}", f"{cm}   tags: {tagm}", f"{cm}   other: none",
              f"{cm}   note: tags live on the N internal nodes only; each holds {what}"]
    return "\n".join(lines) + "\n"


def describe(kind, fields, tags):
    words = {"rangeAdd": "add", "rangeChmin": "chmin", "rangeChmax": "chmax", "rangeAssign": "assign"}
    ops = ops_of(kind, fields, tags)
    upd = [words[o] for o in ("rangeAdd", "rangeAssign", "rangeChmin", "rangeChmax") if o in ops]
    qry = [f for f in ("sum", "min", "max") if f in fields]
    return f"range {' / '.join(upd)} with range {' / '.join(qry)} queries, plus point ops"


