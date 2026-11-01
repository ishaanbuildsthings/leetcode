"""Letters (a list of characters) support, worked out and written for every template:

    python3 gen_letters.py [filters]     (after any generator; it is the last step)

For each template with at least one query that makes sense on characters (test_templates.CHAR_SAFE: compare, copy, move,
hash; not sums or other arithmetic):
  1. run it as is on order-preserving letters, with just those ops: if it passes, its header gets "@letters: same"
     (the very same file takes characters)
  2. otherwise make a letters version of its Python file and run that: character sentinels instead of the infinite
     ones ("" sorts below every character, chr(0x10FFFF) above every one) and ord(c) where a hash adds to a value.
     If it passes it is written as letters.py, next to letters.cpp (the C++ file as is: it is generic over T, so T =
     char), both listing just the character ops. The number version never pays for any of this.
  3. otherwise the template is for numbers only.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import test_templates as T  # noqa: E402
from note_lang import strip_attribution, write_template  # noqa: E402

DIR = T.DIR
TRIALS = 60
LETTERS_NOTE = ("Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and "
                "only the operations that make sense on characters are listed.")


def with_ops(text, cm, ops):
    """text with its @operations / @complexities cut down to ops (and no @letters tag)."""
    out, in_comp = [], False
    for ln in text.split("\n"):
        if ln.startswith(f"{cm} @letters:"):
            continue
        if ln.startswith(f"{cm} @operations:"):
            ln = f"{cm} @operations: {' '.join(ops)}"
        if ln.startswith(f"{cm} @complexities:"):
            in_comp = True
            out.append(ln)
            continue
        if in_comp:
            m = re.match(rf"^{re.escape(cm)}   (\w+): ", ln)
            if m:
                if m.group(1) != "build" and m.group(1) not in ops:
                    continue
            else:
                in_comp = False
        out.append(ln)
    return "\n".join(out)


def drop_methods(text, lang, ops):
    """text without the public methods of ops (each is its own blank-line-separated block, comment included)"""
    if not ops or lang != "py":  # (C++ never compiles a member nobody calls: those stay, harmless)
        return text
    pat = re.compile(rf"^    def ({'|'.join(ops)})\(", re.M)
    return "\n\n".join(b for b in text.split("\n\n") if "class " in b or not pat.search(b))


def note(cm):
    import textwrap
    return "\n".join(f"{cm} {ln}" for ln in textwrap.wrap(LETTERS_NOTE, 116)) + "\n"


def set_tag(path, cm, on):
    """add (on) or remove the "@letters: same" line, right before @complexities"""
    text = open(path).read()
    lines = [ln for ln in text.split("\n") if not ln.startswith(f"{cm} @letters:")]
    if on:
        k = next(i for i, ln in enumerate(lines) if ln.startswith(f"{cm} @complexities:"))
        lines.insert(k, f"{cm} @letters: same")
    new = "\n".join(lines)
    if new != text:
        open(path, "w").write(new)


def to_letters_py(text):
    """the Python file made to take characters: character sentinels, ord(c) in hashes"""
    text = re.sub(r'float\("-inf"\)', '""', text)
    text = re.sub(r'float\("inf"\)', "chr(0x10FFFF)", text)
    text = re.sub(r"(?<![\w)\]])-INF\b", '""', text)
    text = re.sub(r"\(([\w.\[\]]+) \+ _HO\)", r"(ord(\1) + _HO)", text)
    return text


CXX = T.find_cxx()


def letters_pass(folder, ops, stem, cpp_stem=None):
    """None if stem.py (and, given, cpp_stem.cpp with T = char) answers every query right on characters (just ops),
    else what went wrong"""
    trials, ctx = T.make_trials(folder, ops, TRIALS, letters=True)
    extra = T.domain(folder, ops)[2]
    if "isRBS" in ops:
        extra = T.rbs_extra(folder, True)
    try:
        got = T.run_python(folder, ops, trials, extra, stem)
        if cpp_stem and CXX:
            cgot = T.run_cpp(folder, ops, trials, extra, CXX, cpp_stem, chars=True)[0]
            bad = T.first_mismatch(cgot, T.expected_outputs(trials, ctx), trials, False)
            if bad:
                return "cpp: " + bad
    except Exception as e:  # noqa: BLE001
        return f"{type(e).__name__}: {e}"
    try:
        return T.first_mismatch(got, T.expected_outputs(trials, ctx), trials, False)
    except Exception as e:  # noqa: BLE001 -- an answer that can't even be read is a wrong one
        return f"{type(e).__name__}: {e}"


def main():
    args = sys.argv[1:]
    exact = None
    if "--from" in args:  # --from FILE: exactly the folders listed in FILE (one per line)
        k = args.index("--from")
        exact = set(open(args[k + 1]).read().split())
        args = args[:k] + args[k + 2:]
    filters = [a for a in args if not a.startswith("--")]
    same = made = numbers = 0
    for folder in sorted(os.listdir(DIR)):
        if filters and not any(f in folder for f in filters) or exact is not None and folder not in exact:
            continue
        base = os.path.join(DIR, folder)
        py, cpp = os.path.join(base, "template.py"), os.path.join(base, "template.cpp")
        for stem_file in ("letters.py", "letters.cpp"):
            if os.path.exists(os.path.join(base, stem_file)):
                os.remove(os.path.join(base, stem_file))
        for path, cm in ((py, "#"), (cpp, "//")):
            if os.path.exists(path):
                set_tag(path, cm, False)
        if not os.path.exists(py):
            continue
        ops = T.parse_ops(py, "#")
        cops = [o for o in ops if o in T.CHAR_SAFE]
        if not any(not T.is_update(o) for o in cops):
            continue  # nothing to ask on characters
        if letters_pass(folder, cops, "template", "template" if os.path.exists(cpp) else None) is None:
            for path, cm in ((py, "#"), (cpp, "//")):
                if os.path.exists(path):
                    set_tag(path, cm, True)
            same += 1
            continue
        src = strip_attribution(open(py).read())
        dropped = [o for o in ops if o not in cops]
        conv = to_letters_py(with_ops(src, "#", cops))
        if conv == with_ops(src, "#", cops):  # nothing to change: numbers only
            numbers += 1
            continue
        lp = os.path.join(base, "letters.py")
        write_template(lp, drop_methods(conv, "py", dropped).replace("\n\n", "\n\n" + note("#"), 1))
        if os.path.exists(cpp):
            ctext = drop_methods(with_ops(strip_attribution(open(cpp).read()), "//", cops), "cpp", dropped)
            write_template(os.path.join(base, "letters.cpp"), ctext.replace("\n\n", "\n\n" + note("//"), 1))
        if letters_pass(folder, cops, "letters", "letters" if os.path.exists(cpp) else None) is not None:
            for f in ("letters.py", "letters.cpp"):
                if os.path.exists(os.path.join(base, f)):
                    os.remove(os.path.join(base, f))
            numbers += 1
            continue
        made += 1
    print(f"letters: {same} templates take characters as they are, {made} got a letters version, {numbers} are numbers only")


if __name__ == "__main__":
    main()
