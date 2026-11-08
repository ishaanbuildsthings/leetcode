"""Binary tries for "v ^ x over the values v of a[l..r]" (the sets picker's XOR-with-x queries, asked about a subarray).

    python3 gen_xor_trie.py

One template per update kind, a Pareto frontier:
  persistent-trie-xor[-mex][-sumxor]  static array (append / pop allowed): version p is a trie of a[0..p-1], a[l..r] is
                                       version r + 1 minus version l. O(log U) per query. mex adds each node's smallest
                                       last index; sumxor adds per-bit prefix counts.
  bit-of-tries-xor                     point assign: a Fenwick tree over positions, each node a binary trie; a query
                                       walks the ~2 log N tries of the two prefixes together. O(log N log U).
  sqrt-tries-xor                       range xor-apply / range assign / point assign: sqrt(N) blocks, each a trie with
                                       a lazy xor and a lazy assign; a query walks every block's trie together (the
                                       partial ends go in a scratch trie). O(sqrt(N) log U).
The sources live in xor_trie/*.src with variant markers: whole-line blocks "#<tag>" ... "#</tag>" (C++: "//<tag>"),
and single lines ending in "#@tag" (kept only with tag) or "#@!tag" (kept only without it).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "range-queries")
SRC = os.path.join(HERE, "xor_trie")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries"

XOR_OPS = ["maxXorAgainstX", "minXorAgainstX", "kthXor", "countXorLtK", "countXorLteK", "countXorGtK", "countXorGteK",
           "largestXorLtK", "largestXorLteK", "smallestXorGtK", "smallestXorGteK"]
XOR_OPS += [f"{mm}XorWithV{c}M" for mm in ("max", "min") for c in ("Lt", "Lte", "Gt", "Gte")]
XOR_OPS += ["maxXorWithVInValRange", "minXorWithVInValRange"]
ORDER = ["countGtX", "countGteX", "countInValRange", "countLtX", "countLteX", "countOccurrences", "kthSmallest",
         "largestLtX", "largestLteX", "maxAll", "minAll", "rangeMax", "rangeMin", "smallestGtX", "smallestGteX"]
SUMS = ["sumAbsDiffToX", "sumGtX", "sumGteX", "sumInValRange", "sumKthLargestRange", "sumKthSmallestRange",
        "sumLargestK", "sumLtX", "sumLteX", "sumSmallestK"]
XORV = ["xorGtX", "xorGteX", "xorInValRange", "xorLtX", "xorLteX"]


def tag_ops(tags):
    """the ops a set of variant tags adds (beyond the xor-with-x ops and the plain order statistics)"""
    ops = (["mexXor", "rangeMex"] if "mex" in tags else []) + (["sumXor"] if "sumxor" in tags else [])
    ops += (["rangeSum"] if "sumany" in tags else []) + (["rangeXorQuery"] if "xorany" in tags else [])
    ops += [f"{a}{c}" for a in ("or", "and") if a in tags for c in ("LtX", "LteX", "GtX", "GteX", "InValRange")]
    return ops + (SUMS if "sums" in tags else []) + (XORV if "xorv" in tags else [])


def full_tags(tags):
    tags = set(tags)
    if tags & {"sums", "sumxor"}:
        tags.add("sumany")
    if tags & {"xorv", "sumxor"}:
        tags.add("xorany")
    if tags & {"or", "and"}:
        tags.add("orand")
    return tags


def strip(text, tags, cm):
    out, skip = [], []
    for line in text.split("\n"):
        m = re.match(rf"\s*{re.escape(cm)}<(/?)(!?)(\w+)>\s*$", line)
        if m:
            if m.group(1):
                skip.pop()
            else:
                skip.append((m.group(3) in tags) == bool(m.group(2)))
            continue
        if any(skip):
            continue
        m = re.search(rf"\s*{re.escape(cm)}@(!?)(\w+)(\s+\S.*)?$", line)
        if m:
            if (m.group(2) in tags) == bool(m.group(1)):
                continue
            line = line[:m.start()] + (f"  {cm} {m.group(3).strip()}" if m.group(3) else "")
        out.append(line)
    return "\n".join(out)


def header(cm, folder, dstype, costs, node, other, note, lang):
    ops = sorted(costs)
    lines = [f"Template by https://github.com/ishaanbuildsthings", f"{URL}/{folder}/template.{lang}"]
    if lang == "cpp":
        return lines, ops
    return lines, ops


def write(folder, dstype, costs, build, node, other, notes, tags, stem):
    os.makedirs(os.path.join(DIR, folder), exist_ok=True)
    ops = sorted(o for o in costs)
    for lang, cm in (("py", "#"), ("cpp", "//")):
        src = open(os.path.join(SRC, f"{stem}.{lang}.src")).read()
        snippet = open(os.path.join(SRC, f"orderstats.{lang}.src")).read().replace("COST", COST_TEXT[stem])
        src = src.replace(f"    {cm}@@ORDERSTATS\n", snippet.strip("\n") + "\n")
        body = strip(src, tags, cm)
        tag = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {dstype}", "@complexities:"]
        tag += [f"  {op}: {costs[op]}" for op in ops] + [f"  build: {build}"]
        tag += ["@memory:", "  layout: none", f"  node: {node}", "  tags: none", f"  other: {other}", f"  note: {notes[lang]}"]
        tag = "\n".join(f"{cm} {x}" for x in tag)
        top = f"{cm} Template by https://github.com/ishaanbuildsthings\n{cm} {URL}/{folder}/template.{lang}\n"
        if lang == "py":
            text = top + tag + "\n\n" + body.strip("\n") + "\n"
        else:
            text = top + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + tag + "\n\n" + body.strip("\n") + "\n"
        open(os.path.join(DIR, folder, f"template.{lang}"), "w").write(text)
    print("wrote", folder)


COST_TEXT = {"persistent": "O(logU)", "bit": "O(logN logU)", "sqrt": "O(sqrt(N) logU)"}


def persistent():
    LU = "1*N*log(U)"
    import itertools
    for flags in itertools.product((False, True), repeat=6):
        on = [t for t, f in zip(("mex", "sumxor", "sums", "xorv", "or", "and"), flags) if f]
        tags = full_tags(on)
        folder = "persistent-trie-xor" + "".join(f"-{t}" for t in on)
        costs = {op: "log(U)*log(U)" if op.startswith(("orL", "orG", "orI", "and")) else "log(U)"
                 for op in XOR_OPS + ORDER + ["append"] + tag_ops(tags)}
        costs.update(getAll="N", pointGet="1", pop="1", size="1")
        node = f"L[{LU}] R[{LU}] C[{LU}]" + "".join(f" {f}[{LU}]" for t, f in (("mex", "M"), ("sums", "S"), ("xorv", "X")) if t in tags)
        other = "root[1*N] arr[1*N]" + (f" P[{LU}]" if "sumxor" in tags else "")
        other += "".join(f" {f}[1*N*log(U)*log(U)]" for t, f in (("or", "OI"), ("and", "AI")) if t in tags)
        note = ("N = every value ever added (initial array plus each append); each adds one root-to-leaf path of "
                "log U + 1 nodes, U = 2^bits")
        write(folder, "persistent-trie", costs, "N*log(U)", node, other, {"py": note, "cpp": note}, tags, "persistent")


def bit():
    import itertools
    LNU = "1*N*log(N)*log(U)"
    for flags in itertools.product((False, True), repeat=3):
        on = [t for t, f in zip(("sumxor", "sums", "xorv"), flags) if f]
        tags = full_tags(on)
        folder = "bit-of-tries-xor" + "".join(f"-{t}" for t in on)
        costs = {op: "log(N)*log(U)" for op in XOR_OPS + ORDER + ["pointAssign"] + tag_ops(tags)}
        costs.update(getAll="N", pointGet="1", size="1")
        note = ("BIT over positions, each BIT node a binary trie of its block's values (U = 2^bits); nodes are never "
                "freed, so each point assign adds up to 2 log N log U of them")
        node = f"L[{LNU}] R[{LNU}] C[{LNU}]" + "".join(f" {f}[{LNU}]" for t, f in (("sums", "S"), ("xorv", "X")) if t in tags)
        other = "root[1*N] arr[1*N]" + (" F[1*N*log(U)]" if "sumxor" in tags else "")
        write(folder, "bit-of-tries", costs, "N*log(N)*log(U)", node, other, {"py": note, "cpp": note}, tags, "bit")


def sqrt():
    for on in ([], ["sumxor"]):
        tags = full_tags(on)
        folder = "sqrt-tries-xor" + "".join(f"-{t}" for t in on)
        costs = {op: "sqrt(N)*log(U)" for op in XOR_OPS + ORDER + ["pointAssign", "rangeAssign", "rangeXorApply"] + tag_ops(tags)}
        costs.update(getAll="N", pointGet="1", size="1")
        note = ("blocks of about sqrt N, each a binary trie of its stored values (at most its length times log U nodes, "
                "U = 2^bits) with a lazy xor and a lazy assign; a scratch trie of 2 sqrt N log U nodes for the partly "
                "covered ends of a query")
        other = "arr[1*N] tag[1*sqrt(N)] uni[1*sqrt(N)]" + (" ones[1*sqrt(N)*log(U)]" if "sumxor" in tags else "")
        write(folder, "sqrt-tries", costs, "N*log(U)", "L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]", other,
              {"py": note, "cpp": note}, tags, "sqrt")


if __name__ == "__main__":
    persistent()
    bit()
    sqrt()
