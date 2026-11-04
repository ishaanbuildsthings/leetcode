"""Sanity-check the template catalog as a whole (run after `npm run gen:range-queries` in site/).

    python3 check_catalog.py

1. Coverage: every op in the picker has at least one template, and every template op is in the picker.
2. Pareto: no template is dominated, i.e. no other template supports all of its ops with no more memory, no slower
   build, and no slower cost on any of those ops (amortized counts as slower than worst-case), while being strictly
   better somewhere. A dominated template is never the right pick and should be deleted.
Costs are compared at N = 2e5, U = 1e9, the same values the picker ranks with.
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "site", "lib", "generated", "range-query-templates.ts")
PICKER = os.path.join(ROOT, "site", "lib", "range-query-picker.ts")

N, U = 2e5, 1e9
# dominated, but the user wants them on the page anyway (2026-10-22: "lets keep the plain persistent ones too")
KEPT = {"persistent-order-stats", "persistent-order-stats-sums"}
FACTORS = {"1": 1, "N": N, "log(N)": math.log2(N), "log^2(N)": math.log2(N) ** 2, "sqrt(N)": math.sqrt(N),
           "log(U)": math.log2(U), "log(log(U))": math.log2(math.log2(U)), "U": U, "U/64": U / 64,
           "log64(U)": math.log2(U) / 6}


def value(cost):
    body = re.sub(r" (amortized|expected)$", "", re.sub(r" \?$", "", cost))
    return sum(math.prod(FACTORS[f] if f in FACTORS else float(f) for f in term.split("*")) for term in body.split("+"))


def amortized(cost):  # amortized or expected: weaker than a worst-case bound
    return "amortized" in cost or "expected" in cost


def dominates(y, x):
    """True if template y makes template x pointless."""
    if not set(x["operations"]) <= set(y["operations"]):
        return False
    if y.get("valuesOffline") and not x.get("valuesOffline"):  # needing every value up front is a real cost
        return False
    if x.get("sparse") and not y.get("sparse"):  # x's sparse version is a frontier point of its own
        return False
    mx, my = value(x["memory"]["total"]), value(y["memory"]["total"])
    bx, by = value(x["build"]), value(y["build"])
    if my > mx or by > bx:
        return False
    strict = my < mx or by < bx
    for op in x["operations"]:
        cx, cy = x["complexities"][op], y["complexities"][op]
        if value(cy) > value(cx) or (amortized(cy) and not amortized(cx)):
            return False
        strict |= value(cy) < value(cx) or (amortized(cx) and not amortized(cy))
    return strict


def load_manifest():
    """the templates in the site's compact manifest (tables + one row per template), as dicts like decodeRangeTemplates"""
    src = open(MANIFEST).read()
    t = {}
    for name in ("RANGE_OP_NAMES", "RANGE_COSTS", "RANGE_OP_LISTS", "RANGE_COST_LISTS", "RANGE_MEMORIES", "RANGE_TEMPLATE_ROWS"):
        start = src.index("= ", src.index(f"export const {name}")) + 2
        body = src[start: src.index(";\n", start)].strip()
        t[name] = json.loads(re.sub(r",\s*\]$", "]", body))
    lists = [[t["RANGE_OP_NAMES"][i] for i in l] for l in t["RANGE_OP_LISTS"]]

    def unpack(lst, cl, build, mem):
        ops = lists[lst]
        return {"operations": ops, "complexities": {op: t["RANGE_COSTS"][c] for op, c in zip(ops, t["RANGE_COST_LISTS"][cl])},
                "build": t["RANGE_COSTS"][build], "memory": t["RANGE_MEMORIES"][mem]}
    out = []
    for folder, langs, typ, flags, url, lst, cl, build, mem, sparse, letters in t["RANGE_TEMPLATE_ROWS"]:
        d = {"folder": folder, "langs": langs.split(), "dataStructureType": typ, **unpack(lst, cl, build, mem)}
        if "o" in flags:
            d["valuesOffline"] = True
        if "f" in flags or "F" in flags:
            d["fractionalCascading"] = "f" in flags
        if sparse:
            d["sparse"] = {"langs": sparse[0].split(), **unpack(*sparse[1:5])}
        out.append(d)
    return out


def main():
    templates = load_manifest()
    picker = open(PICKER).read()
    start = picker.index("export type OpId")
    picker_ops = set(re.findall(r'"(\w+)"', picker[start: picker.index(";", start)]))
    template_ops = {op for t in templates for op in t["operations"]}

    problems = 0
    for op in sorted(picker_ops - template_ops):
        print(f"picker op with no template: {op}")
        problems += 1
    for op in sorted(template_ops - picker_ops):
        print(f"template op missing from the picker: {op}")
        problems += 1
    for x in templates:
        better = next((y for y in templates if y is not x and dominates(y, x)), None)
        if better and x["folder"] in KEPT:
            print(f"kept on purpose: {x['folder']} (dominated by {better['folder']})")
        elif better:
            print(f"dominated: {x['folder']}  [{x['memory']['total']}]\n       by: {better['folder']}  [{better['memory']['total']}]")
            problems += 1
    print(f"{len(templates)} templates, {len(picker_ops)} ops: " + ("all good" if not problems else f"{problems} problem(s)"))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
