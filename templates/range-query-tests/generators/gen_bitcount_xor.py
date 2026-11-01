"""The xor-only BitCountTree: range xor= with range sum / and / or queries, without the AND tag that only and= / or= use.

    python3 gen_bitcount_xor.py      (after any change to the full BitCountTree)

Derived from the full template (pointAdd-...-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum-
rangeXorApply) by taking the AND tag out: with xor as the only update a tag is just the mask to flip, so per bit a
pending update is "flip or not" and the counts become length - count. Every rewrite below must match exactly once.
"""
import os

from note_lang import strip_attribution, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SRC = "pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum-rangeXorApply"
DST = "pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply"

COMMON = [
    ("@operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum rangeXorApply",
     "@operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeOrQuery rangeSum rangeXorApply"),
    ("{c}   rangeAndApply: log(N)*log(U)\n", ""), ("{c}   rangeOrApply: log(N)*log(U)\n", ""),
    ("{c}   tags: andTag[1*N] xorTag[1*N]", "{c}   tags: xorTag[1*N]"),
    ("Range and= / or= / xor= with range sum / and / or queries", "Range xor= with range sum / and / or queries"),
    ("Every\n{c} update is v -> (v & a) ^ x (and X = (X, 0), or X = (~X, X), xor X = (FULL, X)), and per bit that is \"keep\",\n"
     "{c} \"force 0\", \"force 1\" or \"flip\": force sets the count to 0 or the node length, flip turns c into length - c.",
     "A xor X\n{c} flips the bits set in X: per bit, a flip turns the count c into length - c, so the tag is just the mask to\n"
     "{c} flip (this is BitCountTree without the AND tag that only and= / or= need)."),
]

PY = [
    ('__slots__ = ("n", "h", "bits", "full", "cnt", "andTag", "xorTag")', '__slots__ = ("n", "h", "bits", "full", "cnt", "xorTag")'),
    ("        self.andTag = [full] * n  # tags on internal nodes only\n        self.xorTag = [0] * n",
     "        self.xorTag = [0] * n  # tags on internal nodes only"),
    ("    # v -> (v & a) ^ xr on node x, which covers k slots\n    def _apply(self, x, k, a, xr):",
     "    # v -> v ^ xr on node x, which covers k slots\n    def _apply(self, x, k, xr):"),
    ("            if not a >> b & 1:\n                c[x] = 0\n            if xr >> b & 1:", "            if xr >> b & 1:"),
    ("            self.andTag[x] &= a\n            self.xorTag[x] = (self.xorTag[x] & a) ^ xr", "            self.xorTag[x] ^= xr"),
    ("            a, xr = self.andTag[p], self.xorTag[p]", "            xr = self.xorTag[p]"),
    ("                if not a >> b & 1:\n                    v = 0\n", ""),
    ("    def _update(self, l, r, a, xr):", "    def _update(self, l, r, xr):"),
    ("                self._apply(i, k, a, xr)", "                self._apply(i, k, xr)"),
    ("                self._apply(j, k, a, xr)", "                self._apply(j, k, xr)"),
    ("        self._update(l, r, self.full, X & self.full)", "        self._update(l, r, X & self.full)"),
]
PY_MANY = [  # (push and getAll both)
    ("a, xr = self.andTag[x], self.xorTag[x]", "xr = self.xorTag[x]"),
    ("if a != full or xr:", "if xr:"),
    ("self._apply(2 * x, k, a, xr)", "self._apply(2 * x, k, xr)"),
    ("self._apply(2 * x + 1, k, a, xr)", "self._apply(2 * x + 1, k, xr)"),
    ("self.andTag[x], self.xorTag[x] = full, 0", "self.xorTag[x] = 0"),
]
CPP = [
    ("    vector<T> andTag, xorTag; // N: tags on internal nodes", "    vector<T> xorTag;  // N: tags on internal nodes"),
    ("cnt(2 * a.size() * bits), andTag(a.size(), full), xorTag(a.size(), 0) {", "cnt(2 * a.size() * bits), xorTag(a.size(), 0) {"),
    ("    // v -> (v & a) ^ xr on node x, which covers k slots\n    void apply(int x, int k, T a, T xr) {",
     "    // v -> v ^ xr on node x, which covers k slots\n    void apply(int x, int k, T xr) {"),
    ("            if (!(a >> b & 1)) c[b] = 0;\n", ""),
    ("        if (x < n) andTag[x] &= a, xorTag[x] = (xorTag[x] & a) ^ xr;", "        if (x < n) xorTag[x] ^= xr;"),
    ("                if (!(andTag[p] >> b & 1)) v = 0;\n", ""),
    ("    void update(int l, int r, T a, T xr) {", "    void update(int l, int r, T xr) {"),
    ("            if (i & 1) apply(i++, k, a, xr);\n            if (j & 1) apply(--j, k, a, xr);",
     "            if (i & 1) apply(i++, k, xr);\n            if (j & 1) apply(--j, k, xr);"),
    ("    void rangeXorApply(int l, int r, T X) { update(l, r, full, X & full); }", "    void rangeXorApply(int l, int r, T X) { update(l, r, X & full); }"),
]
CPP_MANY = [
    ("if (andTag[x] != full || xorTag[x]) {", "if (xorTag[x]) {"),
    ("apply(2 * x, k, andTag[x], xorTag[x]), apply(2 * x + 1, k, andTag[x], xorTag[x]);", "apply(2 * x, k, xorTag[x]), apply(2 * x + 1, k, xorTag[x]);"),
    ("andTag[x] = full, xorTag[x] = 0;", "xorTag[x] = 0;"),
]


def drop_block(text, start):
    """text without the blank-line-separated block that holds start"""
    i = text.index(start)
    a = text.rfind("\n\n", 0, i) + 2
    b = text.index("\n\n", i)
    return text[:a] + text[b + 2:]


def convert(text, cm, reps, many):
    for a, b in [(x.replace("{c}", cm), y.replace("{c}", cm)) for x, y in COMMON] + reps:
        assert text.count(a) == 1, (cm, a[:80], text.count(a))
        text = text.replace(a, b)
    for a, b in many:
        assert text.count(a) >= 1, (cm, a[:80])
        text = text.replace(a, b)
    if cm == "#":
        text = drop_block(text, "    def rangeAndApply(")
        text = drop_block(text, "    def rangeOrApply(")
    else:
        text = drop_block(text, "    void rangeAndApply(")
        text = drop_block(text, "    void rangeOrApply(")
    assert "andTag" not in text, cm
    return text


def main():
    os.makedirs(os.path.join(DIR, DST), exist_ok=True)
    for ext, cm, reps, many in (("py", "#", PY, PY_MANY), ("cpp", "//", CPP, CPP_MANY)):
        src = strip_attribution(open(os.path.join(DIR, SRC, f"template.{ext}")).read())
        write_template(os.path.join(DIR, DST, f"template.{ext}"), convert(src, cm, reps, many))
    print("wrote", DST)


if __name__ == "__main__":
    main()
