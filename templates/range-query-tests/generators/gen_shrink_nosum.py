"""The shrink trees (range mod / floor div / floor sqrt, pruned by the max) without range sums, so a max / min-only
user doesn't pay for the tot array:

    (retired: gen_seg_algebra.py writes lighter shrink trees into these folders)

Derived from ShrinkTree (no assign: mx, tot) and ShrinkSeg (assign: mx, mn, tot) by taking tot and rangeSum out;
every rewrite must leave no `tot` behind.
"""
import os
import re

from note_lang import strip_attribution, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SOURCES = ["leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv-rangeFloorSqrt-"
           "rangeMax-rangeMod-rangeSum-rightmostGtX-rightmostGteX",
           "leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-"
           "rangeAssign-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMin-rangeMod-rangeSum-rightmostGtX-rightmostGteX-"
           "rightmostLtX-rightmostLteX"]


def drop_blocks(text, pattern):
    """text without every blank-line-separated block containing a line that matches pattern"""
    pat = re.compile(pattern, re.M)
    return "\n\n".join(b for b in text.split("\n\n") if not pat.search(b))


def header(text, cm):
    text = re.sub(rf"^({re.escape(cm)} @operations:.*) rangeSum\b", r"\1", text, count=1, flags=re.M)
    text = re.sub(rf"^{re.escape(cm)}   rangeSum: .*\n", "", text, flags=re.M)
    text = re.sub(r" tot\[4\*N\]", "", text)
    text = re.sub(rf"^{re.escape(cm)} O\(logN\):\s+rangeSum\(l, r\).*\n", "", text, flags=re.M)
    return text


def py(text):
    text = header(text, "#")
    text = text.replace(', "tot")', ")")
    text = re.sub(r"^\s*self\.tot = \[0\] \* size\n", "", text, flags=re.M)
    text = re.sub(r"self\.mx\[(\w+)\] = self\.tot\[\1\] = ", r"self.mx[\1] = ", text)
    text = re.sub(r"^\s*self\.tot\[\w+\] = self\.tot\[\w+\] \+ self\.tot\[\w+\]\n", "", text, flags=re.M)
    text = re.sub(r"; self\.tot\[i\] = [^;\n]+", "", text)
    return drop_blocks(text, r"^    def (_rangeSum|_sum|rangeSum)\(")


def cpp(text):
    text = header(text, "//")
    text = text.replace("// T: int, long long, ...; sums accumulate in S (long long for small T).", "// T: int, long long, ...")
    text = re.sub(r"^    vector<S> tot;\n", "", text, flags=re.M)
    text = text.replace(", tot(4 * max(1, n))", "")
    text = re.sub(r", tot\[i\] = tot\[2 \* i\] \+ tot\[2 \* i \+ 1\]", "", text)
    text = re.sub(r"^\s*tot\[i\] = tot\[2 \* i\] \+ tot\[2 \* i \+ 1\];\n", "", text, flags=re.M)
    text = re.sub(r", tot\[i\] = [^;]+;", ";", text)
    return drop_blocks(text, r"^    S (qsum|rangeSum)\(")


def main():
    for src in SOURCES:
        dst = src.replace("-rangeSum", "")
        os.makedirs(os.path.join(DIR, dst), exist_ok=True)
        for ext, fn in (("py", py), ("cpp", cpp)):
            out = fn(strip_attribution(open(os.path.join(DIR, src, f"template.{ext}")).read()))
            body = out.split("@original-file-url")[0] + out[out.find("\n", out.find("@original-file-url")):]
            assert not re.search(r"\btot\b|rangeSum", body), (dst, ext, re.findall(r".*\btot\b.*|.*rangeSum.*", body)[:3])
            write_template(os.path.join(DIR, dst, f"template.{ext}"), out)
        print("wrote", dst)


if __name__ == "__main__":
    raise SystemExit("retired: gen_seg_algebra.py writes lighter (2N) shrink trees into those folders now")
