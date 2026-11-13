"""Keeps every template line within 120 columns. Run it after regenerating templates:

    python3 format_long_lines.py                  # rewrite
    python3 format_long_lines.py --check          # only list what is too long (exit 1 if any)

Comments are wrapped, and a prose comment paragraph broken early (a short line, then one that carries on the sentence)
is rewrapped; a trailing comment on a long line moves to its own line; long code is broken at commas, operators and
brackets. Each rewrite is proven safe before it is saved: the Python AST, or the C++ text outside comments and
whitespace, must be unchanged. Left alone: URLs and machine-read lines (@ tags, the @memory fields).
"""
import ast
import concurrent.futures
import os
import re
import sys

LIMIT = 120
HERE = os.path.dirname(os.path.abspath(__file__))
FOLDERS = ("range-queries", "sets", "union-find", "strings", "next-permutation", "generic-seg-trees", "matrices",
           "combinatorics", "bit-operations", "trees", "reroot", "bitset", "bubble-sort", "golden-references",
           "tree-queries")
TAG_FIELD = re.compile(r"^\s*(?://|#)\s+(?:layout|node|tags|other|note):")
OPENERS, CLOSERS = "([{", ")]}"


def exempt(line):
    return "http" in line or "@" in line.split("//")[-1].split("#")[-1][:4] or re.match(r"\s*(?://|#) ?@", line) \
        or TAG_FIELD.match(line) or line.rstrip().endswith("\\")


def scan(line, py, depth=0):
    """(where a trailing comment starts or -1, a list of (index, depth, in string) for every character)."""
    info, quote, i = [], None, 0
    while i < len(line):
        ch = line[i]
        if quote:
            info.append((i, depth, True))
            if ch == "\\" and i + 1 < len(line):
                info.append((i + 1, depth, True))
                i += 2
                continue
            if ch == quote:
                quote = None
        else:
            if (py and ch == "#") or (not py and line.startswith("//", i)):
                return i, info
            if ch in "\"'" and not (ch == "'" and not py and i and line[i - 1].isalnum()):
                quote = ch
            elif ch in OPENERS:
                depth += 1
            elif ch in CLOSERS:
                depth -= 1
            info.append((i, depth, quote is not None))
        i += 1
    return -1, info


def wrap_comment(line):
    m = re.match(r"(\s*(?://|#)\s*)(.*)", line)
    prefix, words = m[1], m[2].split(" ")
    out, cur = [], ""
    for w in words:
        if cur and len(prefix) + len(cur) + 1 + len(w) > LIMIT:
            out.append(prefix + cur)
            cur = w
        else:
            cur = cur + " " + w if cur else w
    out.append(prefix + cur)
    return out


def break_py(line, depth):
    """Break one Python statement, at depth depth when it starts, into lines of at most LIMIT columns (or None)."""
    indent = re.match(r"\s*", line)[0]
    cont = indent + " " * 4
    out, rest, d = [], line, depth
    while len(rest) > LIMIT:
        _, info = scan(rest, True, d)
        best = None
        for rank, test in enumerate((lambda c: rest[c - 1:c + 1] == ", ",
                                     lambda c: rest.startswith((" and ", " or ", " + ", " - ", " if ", " else "), c),
                                     lambda c: rest[c] in OPENERS)):
            cands = [(c, dp) for c, dp, s in info if not s and dp >= 1 and 8 < c < LIMIT - 1 and len(rest) > c and test(c)]
            if cands:
                low = min(dp for _, dp in cands)
                best = max(c for c, dp in cands if dp == low)
                best += 0 if rank != 2 else 1
                break
        if best is None:
            m = re.search(r'(\b[rbuf]*)(["\'])', rest)  # a long string inside brackets: split it at a space
            spaces = [c for c, dp, s in info if s and dp >= 1 and c < LIMIT - 2 and rest[c] == " " and m and c > m.end()]
            spaces = [c for c in spaces if rest[:c].count("{") == rest[:c].count("}")]
            if not spaces:
                return None
            c = spaces[-1] + 1
            out.append(rest[:c] + m[2])
            rest = cont + m[1] + m[2] + rest[c:]
            d = info[c][1]
            continue
        out.append(rest[:best].rstrip())
        d = info[best - 1][1] if rest[best - 1] not in OPENERS else info[best - 1][1]
        rest = cont + rest[best:].lstrip()
    out.append(rest)
    return out


def bracket_py(line):
    """No brackets to break inside: put the right-hand side (or the condition) in parentheses."""
    m = re.match(r"(\s*)(return|assert|if|elif|while) (.*?)(:?)$", line)
    if m:
        return f"{m[1]}{m[2]} ({m[3]}){m[4]}"
    _, info = scan(line, True)
    for c, dp, s in info:
        if not s and dp == 0 and line.startswith(" = ", c):
            return f"{line[:c]} = ({line[c + 3:]})"
    return None


def break_cpp(line):
    indent = re.match(r"\s*", line)[0]
    cont = indent + " " * 4
    one = re.match(r"^(.*\S) \{ (.*;) \}(;?)$", line)
    if one and one[1].count("(") == one[1].count(")") and "{" not in one[2]:
        tail = break_cpp(indent + "    " + one[2]) if len(indent) + 4 + len(one[2]) > LIMIT else [indent + "    " + one[2]]
        head = break_cpp(one[1] + " {") if len(one[1]) + 2 > LIMIT else [one[1] + " {"]
        return None if head is None or tail is None else head + tail + [f"{indent}}}{one[3]}"]
    out, rest = [], line
    while len(rest) > LIMIT:
        _, info = scan(rest, False)
        best = None
        # (a return type like tuple<A, B, C> stays whole: everything before the first "(" is one piece)
        first_paren = max(rest.find("("), 0) if not out else 0
        first_paren = first_paren if first_paren < LIMIT - 1 else 0  # (unless that alone doesn't fit)
        for rank, test in enumerate((lambda c: rest[c - 1:c + 1] == ", " or rest[c - 1:c + 1] == "; ",
                                     lambda c: rest.startswith((" && ", " || ", " ? ", " : ", " + ", " - ", " * "), c),
                                     lambda c: rest[c - 1] == "(" or rest[c - 1:c + 1] == "{ " or rest.startswith(" = ", c))):
            cands = [(c, dp) for c, dp, s in info if not s and max(8, first_paren) < c < LIMIT - 1 and test(c)]
            if cands:
                low = min(dp for _, dp in cands)
                best = max(c for c, dp in cands if dp == low)
                break
        if best is None:
            return None
        out.append(rest[:best].rstrip())
        rest = cont + rest[best:].lstrip()
    out.append(rest)
    return out


def same_cpp(a, b):
    def strip(text):
        res, i, n = [], 0, len(text)
        while i < n:
            c = text[i]
            if text.startswith("//", i):
                while i < n and text[i] != "\n":
                    i += 1
            elif text.startswith("/*", i):
                i = text.index("*/", i) + 2
            elif c in "\"'" and not (c == "'" and i and text[i - 1].isalnum()):
                j = i + 1
                while text[j] != c:
                    j += 2 if text[j] == "\\" else 1
                res.append(text[i : j + 1])
                i = j + 1
            else:
                if not c.isspace():
                    res.append(c)
                i += 1
        return "".join(res)
    return strip(a) == strip(b)


def format_text(text, py):
    out, depth, in_triple, stuck = [], 0, None, 0
    for line in text.split("\n"):
        if py and (in_triple or '"""' in line or "'''" in line):
            for mark in ('"""', "'''"):
                odd = line.count(mark) % 2 == 1
                if odd and in_triple in (None, mark):
                    in_triple = None if in_triple else mark
            out.append(line)
            continue
        code_end, info = scan(line, py, depth)
        if not py and line.lstrip().startswith("#"):
            out.append(line)
            continue
        next_depth = info[-1][1] if info else depth
        if len(line) <= LIMIT or exempt(line):
            out.append(line)
            depth = next_depth
            continue
        indent = re.match(r"\s*", line)[0]
        if line.strip().startswith(("//", "#")):
            if indent and any(mark in line for mark in (" = ", "(", "{")) and "generic" in CURRENT[0]:
                out.append(line)  # (an example the tests switch on by uncommenting it)
                stuck += 1
            else:
                out.extend(wrap_comment(line))
            continue
        code, comment = line, ""
        if code_end != -1:
            code, comment = line[:code_end].rstrip(), line[code_end:].lstrip()
            mark = "#" if py else "//"
            note = indent + comment
            if code.endswith("{" if not py else ":") and (not py or depth == 0):
                note = indent + "    " + comment
                pieces = [code, *(wrap_comment(note) if len(note) > LIMIT else [note])]
            else:
                pieces = [*(wrap_comment(note) if len(note) > LIMIT else [note]), code]
            code_at = pieces.index(code)
        else:
            pieces, code_at = [code], 0
        if len(code) > LIMIT:
            broken = break_py(code, depth) if py else break_cpp(code)
            if broken is None and py and depth == 0 and bracket_py(code):
                broken = break_py(bracket_py(code), 0)
            if broken is None:
                stuck += 1
                broken = [code]
            pieces[code_at : code_at + 1] = broken
        out.extend(pieces)
        depth = next_depth
    return "\n".join(out), stuck


COMPARISON = re.compile(r"^\S+ (?:<=?|>=?|==|!=) ")  # "0 <= l <= r < n" kept on one line on purpose
OPERATOR = re.compile(r"^(?:<=?|>=?|==?|!=|[-+*/%^|&]|\*\*|//|<<|>>)[,;)]?$")
CODE_LIKE = re.compile(r"^[A-Za-z_][\w.]*(?:\s*(?:=|\(|\[|<<|::|->)|;$)|[{};]$")


def wrap_prose(prefix, words):
    """greedy, but a line never starts with an operator ("a <= b" stays on one line)"""
    out, cur = [], []
    for w in words:
        if cur and len(prefix) + len(" ".join(cur + [w])) > LIMIT:
            carry = []
            while OPERATOR.match(w if not carry else carry[0]) and len(cur) > 1:  # (move the left side down too)
                carry.insert(0, cur.pop())
                if not OPERATOR.match(carry[0]):
                    break
            out.append(prefix + " ".join(cur))
            cur = carry
        cur.append(w)
    out.append(prefix + " ".join(cur))
    return out


def reflow_text(text, py):
    """Rejoin comment paragraphs that were broken early (a long line split in two leaves a short line before the next
    one). A break is rejoined only inside prose: same indent and marker, the line not ending a sentence (. : ; ! ?),
    the next not starting a new one (a capital, a bullet, "(", extra indent) and neither looking like code. A run is
    rewrapped greedily only when one of its lines leaves room for 10+ more columns that the next word would fill."""
    lines = text.split("\n")
    mark = "#" if py else "//"
    pat = re.compile(rf"^(\s*{re.escape(mark)} )(\S.*)$")
    prose = [None] * len(lines)  # (prefix, content) for a full-line prose comment, else None
    in_triple = None
    for k, line in enumerate(lines):
        if py and (in_triple or '"""' in line or "'''" in line):
            for q in ('"""', "'''"):
                if line.count(q) % 2 == 1 and in_triple in (None, q):
                    in_triple = None if in_triple else q
            continue
        m = pat.match(line)
        if m and not exempt(line) and "  " not in m[2] and not CODE_LIKE.search(m[2]):
            prose[k] = (m[1], m[2])

    def joins(k):
        a, b = prose[k], prose[k + 1] if k + 1 < len(lines) else None
        return (a and b and a[0] == b[0] and not re.search(r"[.:;!?]$", a[1])
                and not re.match(r"[A-Z(\-*|`>#]", b[1]) and not COMPARISON.match(b[1]))

    out, k = [], 0
    while k < len(lines):
        if not (prose[k] and joins(k)):
            out.append(lines[k])
            k += 1
            continue
        j = k
        while joins(j):
            j += 1
        run = lines[k:j + 1]
        roomy = any(len(run[i]) <= LIMIT - 10 and len(run[i]) + 1 + len(prose[k + i + 1][1].split(" ")[0]) <= LIMIT
                    for i in range(len(run) - 1))
        if roomy:
            prefix = prose[k][0]
            out.extend(wrap_prose(prefix, " ".join(prose[i][1] for i in range(k, j + 1)).split(" ")))
        else:
            out.extend(run)
        k = j + 1
    return "\n".join(out)


CURRENT = [""]


def long_lines(text):
    return [k for k, line in enumerate(text.split("\n"), 1) if len(line) > LIMIT and not exempt(line)]


def process(path, check):
    CURRENT[0] = path
    py = path.endswith(".py")
    text = open(path, encoding="utf-8").read()
    if check:
        return path, len(long_lines(text)), ""
    new = format_text(text, py)[0] if long_lines(text) else text
    new = reflow_text(new, py)
    if new == text:
        return path, len(long_lines(text)), ""
    try:
        ok = ast.dump(ast.parse(text)) == ast.dump(ast.parse(new)) if py else same_cpp(text, new)
    except (SyntaxError, ValueError, IndexError) as e:
        return path, len(long_lines(text)), f"REFUSED {path}: {e}"
    if not ok:
        return path, len(long_lines(text)), f"REFUSED {path}: the code would change"
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
    return path, len(long_lines(new)), ""


def main():
    check = "--check" in sys.argv
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = []
    for folder in FOLDERS:
        for root, _, names in os.walk(os.path.join(HERE, folder)):
            files += [os.path.join(root, n) for n in names if n.endswith((".py", ".cpp"))]
    if wanted:
        files = [f for f in files if any(w in f for w in wanted)]
    with concurrent.futures.ProcessPoolExecutor() as pool:
        results = list(pool.map(process, files, [check] * len(files), chunksize=64))
    left = sorted((n, os.path.relpath(p, HERE)) for p, n, _ in results if n)
    for _, _, message in results:
        if message:
            print(message)
    total = sum(n for n, _ in left)
    for n, p in left[-15:]:
        print(f"{n:5} {p}")
    print(f"{total} lines over {LIMIT} columns in {len(left)} of {len(files)} files")
    sys.exit(1 if check and total else 0)


if __name__ == "__main__":
    main()
