"""Every query of a sparse template says, in its own doc comment, what the indices nobody wrote hold.

    add_empty_note(text, lang)    # called by note_lang.write_template on every file it writes
    python3 empty_note.py         # the same step on every sparse.py / sparse.cpp already in range-queries/

A sparse template is a huge array a[lo..hi] where every index starts at 0, so a query over a range nobody touched
answers as an array of zeros would (its max is 0, not -inf). The class and constructor comments say so once; this
repeats it on every method that returns a value, so the line a reader lands on is enough:

    # O(logU) -- max of a[l..r]; never-updated indices count as 0; needs lo <= l <= r <= hi, else IndexError
    # O(logU) -- a[i]; 0 if never updated; needs lo <= i <= hi, else IndexError

A class built from a list of (index, value) pairs says "indices not given in values count as 0" instead. Updates
(methods that return nothing) are left alone, and so is a method that says it already: running this twice changes
nothing.
"""
import os
import re

from bounds import _bounds, _classes, _ops

RANGE = ("never-updated indices count as 0", "indices not given in values count as 0")
POINT = ("0 if never updated", "0 if not given in values")
DIR = os.environ.get("RANGE_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")


def _doc(lines, note, lang, width=120):
    """the doc comment lines with '; <note>' added ahead of '; needs ...' (re-wrapped at width)"""
    cm = lines[0][:len(lines[0]) - len(lines[0].lstrip())] + ("#" if lang == "py" else "//")
    words = " ".join(ln.strip()[len(cm.strip()):].strip() for ln in lines)
    if note in words:
        return lines
    k = words.rfind("; needs ")
    words = words[:k] + "; " + note + words[k:] if k >= 0 else words + "; " + note
    m = re.search(r"needs (.{1,70}?), else", words)  # (a short rule stays on one line)
    if m:
        words = words[:m.start(1)] + m.group(1).replace(" ", " ") + words[m.end(1):]
    out, cur = [], cm
    for w in words.split(" "):
        if len(cur) + 1 + len(w) > width - 2 and cur != cm:
            out.append(cur)
            cur = cm
        cur += " " + w
    return [x.replace(" ", " ") for x in out + [cur]]


def _py_returns(lines, k):
    """does the method whose def is lines[k] hand back a value"""
    if re.search(r"\): return \S", lines[k]):
        return True
    j = k + 1
    while j < len(lines) and (not lines[j].strip() or lines[j].startswith("        ")):
        if re.search(r"\breturn\s+\S", lines[j]):
            return True
        j += 1
    return False


def _class(cls, ops, built, lang):
    py = lang == "py"
    lines, out, k = cls.split("\n"), [], 0
    sig = (re.compile(r"^    def (\w+)\(self") if py else
           re.compile(r"^    (?:LEETCODE_NO_SANITIZE )?(?:[\w:<>, *&]+?\s+)(\w+)\((?:[^)]*\)( const)? \{.*|[^)]*,)$"))
    mark = "    # " if py else "    // "
    while k < len(lines):
        m = sig.match(lines[k])
        if m and m.group(1) in ops and out and out[-1].startswith(mark):
            returns = _py_returns(lines, k) if py else not re.match(r"^    (?:LEETCODE_NO_SANITIZE )?void ", lines[k])
            if returns:
                start = len(out)
                while start > 0 and out[start - 1].startswith(mark):
                    start -= 1
                out[start:] = _doc(out[start:], (POINT if m.group(1) == "pointGet" else RANGE)[built], lang)
        out.append(lines[k])
        k += 1
    return "\n".join(out)


def add_empty_note(text, lang):
    ops = _ops(text)
    if not ops or not re.search(r"^(?:#|//)   layout: sparse$", text, re.M):
        return text
    out, last = [], 0
    for s, e in _classes(text, lang):
        cls = text[s:e]
        b = _bounds(cls, lang, True)
        if b is None or b[0] != "sparse":  # (a dense helper class inside a sparse file has no untouched indices)
            continue
        ctor = re.search(r"def __init__\(self, ([^)]*)\)" if lang == "py" else r"^    (?:explicit )?\w+\(([^)]*)\)", cls,
                         re.M)
        built = bool(ctor and re.search(r"\bvalues\b", ctor.group(1)))
        out.append(text[last:s] + _class(cls, ops, built, lang))
        last = e
    return "".join(out) + text[last:]


if __name__ == "__main__":
    changed = 0
    for folder in sorted(os.listdir(DIR)):
        for ext, lang in ((".py", "py"), (".cpp", "cpp")):
            path = os.path.join(DIR, folder, "sparse" + ext)
            if os.path.exists(path):
                text = open(path).read()
                new = add_empty_note(text, lang)
                if new != text:
                    open(path, "w").write(new)
                    changed += 1
    print(changed, "files rewritten")
