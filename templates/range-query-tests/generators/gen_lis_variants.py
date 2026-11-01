"""Range LIS and its three siblings, each its own static template (one seaweed structure each, no shared overhead):

    python3 gen_lis_variants.py      (then python3 sparse_static.py for the strict ones' sparse versions)

    rangeLIS   longest strictly increasing subsequence   (pointGet-rangeLIS: the hand-written source)
    rangeLNDS  longest non-decreasing subsequence
    rangeLDS   longest strictly decreasing subsequence
    rangeLNIS  longest non-increasing subsequence

The seaweed algorithm needs a permutation, and the only difference between the four is how values are ranked into it:
by value up (increasing) or down (decreasing), with equal values ranked right to left (strict: two equal values can
never both be taken) or left to right (non-strict: a run of equal values is increasing in rank). This script copies
pointGet-rangeLIS and changes that ranking, the names and the comments.
"""
import os

from note_lang import strip_attribution, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SRC = "pointGet-rangeLIS"
# op, class, words, Python sort key (and reverse), C++ "i ranks before j", what equal values do
VARIANTS = [
    ("rangeLNDS", "RangeLNDS", "non-decreasing", "(arr[i], i)", "a[i] < a[j] || (!(a[j] < a[i]) && i < j)", "left-to-right => non-strict"),
    ("rangeLDS", "RangeLDS", "STRICTLY decreasing", "(arr[i], i), reverse=True", "a[j] < a[i] || (!(a[i] < a[j]) && i > j)", "right-to-left => strict"),
    ("rangeLNIS", "RangeLNIS", "non-increasing", "arr.__getitem__, reverse=True", "a[j] < a[i] || (!(a[i] < a[j]) && i < j)", "left-to-right => non-strict"),
]


def convert(text, lang, op, cls, words, pykey, cppcmp, ties):
    low = words.lower()
    text = text.replace("@operations: pointGet rangeLIS", f"@operations: pointGet {op}").replace("  rangeLIS: ", f"  {op}: ")
    text = text.replace("Static range LIS: length of the longest STRICTLY increasing subsequence",
                        f"Static range {op[5:]}: length of the longest {words} subsequence")
    up = op == "rangeLNDS"  # LNDS ranks by value up, LDS / LNIS by value down
    text = text.replace("(equal values ranked right-to-left, so \"strictly increasing\" survives)",
                        f"(by value {'up' if up else 'down'}, ties {ties.split(' =>')[0]}: \"{low}\" survives)")
    text = text.replace("RangeLIS", cls).replace("def rangeLIS(", f"def {op}(").replace("int rangeLIS(", f"int {op}(")
    text = text.replace("length of the longest strictly increasing subsequence of a[l..r]",
                        f"length of the longest {low} subsequence of a[l..r]")
    if lang == "py":
        old = "order = sorted(range(n), key=lambda i: (arr[i], -i))  # equal values ranked right-to-left => strict LIS"
        assert old in text
        key = pykey if pykey.startswith("arr.") else f"lambda i: {pykey}"  # (reverse=True, not negation: letters work too)
        text = text.replace(old, f"order = sorted(range(n), key={key})  # equal values ranked {ties}")
    else:
        old = "sort(order.begin(), order.end(), [&](int i, int j) { return a[i] < a[j] || (!(a[j] < a[i]) && i > j); });"
        assert old in text
        text = text.replace(old, f"sort(order.begin(), order.end(), [&](int i, int j) {{ return {cppcmp}; }});")
        text = text.replace("perm[order[r]] = r;  // equal values ranked right-to-left => strict LIS",
                            f"perm[order[r]] = r;  // equal values ranked {ties}")
    return text


def main():
    for op, cls, words, pykey, cppcmp, ties in VARIANTS:
        folder = os.path.join(DIR, f"pointGet-{op}")
        os.makedirs(folder, exist_ok=True)
        for ext, lang in (("py", "py"), ("cpp", "cpp")):
            src = strip_attribution(open(os.path.join(DIR, SRC, f"template.{ext}")).read())
            write_template(os.path.join(folder, f"template.{ext}"), convert(src, lang, op, cls, words, pykey, cppcmp, ties))
        print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
