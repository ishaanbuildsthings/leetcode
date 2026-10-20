"""Per-language @memory notes.

A note may describe both implementations: "...; C++: X; Python: Y", "(C++: X; Python: Y)", or Python first. Each
language's file should only carry its own part, so lang_note keeps the segment for one language and drops the
other's. write_template applies it to a file's note line (# -> Python, // -> C++) as it writes the file.

Every file also starts with two attribution lines (template by <GitHub user>, then the file's own GitHub link).

    python3 note_lang.py    # rewrite the notes and attribution of every template.* / sparse.* in range-queries/
"""
import os
import re

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
LABELS = {"cpp": "C++: ", "py": "Python: "}
LABEL_RE = re.compile(r"(C\+\+|Python): ")


def _segment_end(text, i):
    """End of a labeled segment starting at i: the first ';' or ')' at paren depth 0 (or the end)."""
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                return i
            depth -= 1
        elif c == ";" and depth == 0:
            return i
        i += 1
    return i


def lang_note(note, lang):
    out, i = [], 0
    while True:
        m = LABEL_RE.search(note, i)
        if not m:
            out.append(note[i:])
            return "".join(out)
        before = note[i:m.start()]
        # a group of labeled segments joined by "; "
        segs, j = {}, m.start()
        while True:
            lm = LABEL_RE.match(note, j)
            if not lm:
                break
            end = _segment_end(note, lm.end())
            segs["cpp" if lm.group(1) == "C++" else "py"] = note[lm.end():end].strip()
            if note.startswith("; ", end) and LABEL_RE.match(note, end + 2):
                j = end + 2
                continue
            j = end
            break
        keep = segs.get(lang)
        if keep is None:  # nothing for this language: drop the group and the separator before it
            out.append(re.sub(r"[;,]?\s*$", "", before))
        else:
            if before.rstrip().endswith(".") or before == "":
                keep = keep[0].upper() + keep[1:]
            out.append(before + keep)
        i = j


def fix_text(text, lang):
    def fix(m):
        return m.group(1) + lang_note(m.group(2), lang)
    return re.sub(r"^((?:#|//)   note: )(.*)$", fix, text, count=1, flags=re.M)


GITHUB_USER = "https://github.com/ishaanbuildsthings"
GITHUB_FILES = GITHUB_USER + "/leetcode/blob/main/templates/range-queries/"
OLD_CREDIT = re.compile(r"^(#|//) TEMPLATE BY .*\n(\1\s*\n)?", re.M)  # older credit lines, replaced by the header below


def attribution_lines(path):
    cm = "#" if path.endswith(".py") else "//"
    folder, name = os.path.basename(os.path.dirname(path)), os.path.basename(path)
    return [f"{cm} Template by {GITHUB_USER}", f"{cm} {GITHUB_FILES}{folder}/{name}"]


def strip_attribution(text):
    """The file without its two attribution lines (if present)."""
    lines = text.split("\n")
    if len(lines) >= 2 and re.match(r"^(#|//) Template by https://github\.com/", lines[0]):
        return "\n".join(lines[2:])
    return text


def attribute(text, path):
    """Two first lines: who made the template, and where this file lives on GitHub."""
    body = OLD_CREDIT.sub("", strip_attribution(text))
    return "\n".join(attribution_lines(path)) + "\n" + body


def write_template(path, text):
    open(path, "w").write(attribute(fix_text(text, "py" if path.endswith(".py") else "cpp"), path))


if __name__ == "__main__":
    changed = 0
    for folder in sorted(os.listdir(DIR)):
        for stem in ("template", "sparse"):
            for ext, lang in ((".py", "py"), (".cpp", "cpp")):
                path = os.path.join(DIR, folder, stem + ext)
                if os.path.exists(path):
                    text = open(path).read()
                    new = attribute(fix_text(text, lang), path)
                    if new != text:
                        open(path, "w").write(new)
                        changed += 1
    print(changed, "files rewritten")
