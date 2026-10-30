"""Per-language @memory notes.

A note may describe both implementations: "...; C++: X; Python: Y", "(C++: X; Python: Y)", or Python first. Each
language's file should only carry its own part, so lang_note keeps the segment for one language and drops the
other's. write_template applies it to a file's note line (# -> Python, // -> C++) as it writes the file.

Every file also starts with two attribution lines (template by <GitHub user>, then the file's own GitHub link).

    python3 note_lang.py    # rewrite the notes and attribution of every template.* / sparse.* in range-queries/
"""
import os
import re
import textwrap

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


# C++ sparse trees used to keep their nodes in a static pool shared by every tree of the type (resetPool() between
# test cases). Each tree now owns its pool: a plain member, freed when the tree goes out of scope, so a tree per test
# case needs nothing between them. own_pool turns a generated file into that form, code and prose; a comment paragraph
# it changes is re-wrapped at 120 columns.
POOL_PROSE = [  # applied to whole comment paragraphs (lines joined by spaces) and to the note line
    (r"\s*\(resetPool\(\) between test cases\)", ""),
    (r"[;,]\s*call resetPool\(\) between test cases", ""),
    (r"\s*Tree::resetPool\(\) between test cases is\b[^.]*\.", ""),
    (r"in one pool shared by every \w+(?:<T>)?", "in a pool the tree owns"),
    (r"one pool shared by every \w+(?:<T>)?", "a pool the tree owns"),
    (r"in one shared node pool", "in a node pool the tree owns"),
    (r"One shared node pool", "A node pool per tree"),
    (r"one shared node pool", "a node pool per tree"),
    (r"node 0 is the shared all-zeros block", "node 0 is the all-zeros block"),
    (r"node 0 is the shared\b", "node 0 is the"),
    (r"the shared all-zeros block", "the all-zeros block"),
]


def _prose(t):
    for pat, rep in POOL_PROSE:
        t = re.sub(pat, rep, t)
    return t


def own_pool(text):
    if "resetPool" not in text:
        return text
    # the pool arrays: "static inline vector<T> a, b{0};" lines
    names = set()
    for decl in re.findall(r"^    static inline vector<.*?> (.*?);", text, flags=re.M):
        while re.search(r"\{[^{}]*\}", decl):  # drop initializers, innermost first ("pool{Node{Agg{}, 0}}")
            decl = re.sub(r"\{[^{}]*\}", "", decl)
        names |= set(re.findall(r"(?:^|,)\s*([A-Za-z_]\w*)", re.sub(r"=[^,]*", "", decl)))
    # const methods that create nodes on demand (the beats trees' queries) still write the pool: it becomes mutable
    grows = any(re.search(rf"\b{n}\.(?:push_back|emplace_back|resize)\(|\b{n}\[[^\]]*\]\s*=[^=]", body)
                for body in re.findall(r"\) const \{.*?\n    \}", text, flags=re.S) for n in names)
    text = re.sub(r"^    static inline (vector<)", r"    mutable \1" if grows else r"    \1", text, flags=re.M)
    text = re.sub(r"\n(    //[^\n]*\n)?    static void resetPool\(\) \{[^\n]*\}\n", "\n", text)
    text = text.replace("    static void reservePool(", "    void reservePool(")
    # a static member function becomes a plain one only if it touches the pool, or calls one that does; pure helpers
    # stay static (const queries may call them)
    funcs = {}  # name -> body
    for m in re.finditer(r"^    static (?!constexpr|inline)[^\n(]*?\b(\w+)\(", text, flags=re.M):
        i, depth = text.index("{", m.end()), 0
        for j in range(i, len(text)):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            if not depth:
                break
        funcs[m.group(1)] = text[m.start():j + 1]
    touch = {f for f, body in funcs.items() if any(re.search(rf"\b{n}\b", body) for n in names)}
    while True:
        more = {f for f, body in funcs.items() if f not in touch and any(re.search(rf"\b{g}\(", body) for g in touch)}
        if not more:
            break
        touch |= more
    for f in touch:
        text = re.sub(rf"^    static ((?!constexpr|inline)[^\n(]*?\b{f}\()", r"    \1", text, flags=re.M)
    text = text.replace("const {  // const: it only touches the shared pool", "const {  // const: it only grows the (mutable) pool")
    text = text.replace("// node 0: the shared all-zeros block", "// node 0: the all-zeros block")
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^(\s*)// (?!@|  )", lines[i])
        if not m:
            out.append(_prose(lines[i]) if re.match(r"^\s*//   note: ", lines[i]) else lines[i])
            i += 1
            continue
        j = i  # a paragraph: consecutive "// " lines at one indent (not the @ header)
        while j < len(lines) and re.match(rf"^{m.group(1)}// (?!@|  )", lines[j]):
            j += 1
        block = lines[i:j]
        joined = " ".join(l[len(m.group(1)) + 3:] for l in block)
        changed = _prose(joined)
        if changed == joined:
            out += block
        else:
            out += textwrap.wrap(changed, 120, initial_indent=m.group(1) + "// ", subsequent_indent=m.group(1) + "// ",
                                 break_long_words=False, break_on_hyphens=False)
        i = j
    return "\n".join(out)


def fix_text(text, lang):
    def fix(m):
        return m.group(1) + lang_note(m.group(2), lang)
    if lang == "cpp":
        text = own_pool(text)
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
