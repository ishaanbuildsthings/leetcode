"""Fast mode for the seg trees and lazy seg trees: writes fast.cpp beside template.cpp, sparse-fast.cpp beside sparse.cpp
and letters-fast.cpp beside letters.cpp. The logic is unchanged: sanitizers are skipped inside the template, and its
vectors become HotVector, whose [] and size() still inline with sanitizers off. Public signatures keep plain vector.
Run this after the range query generators and add_cpp_prelude.py.

    python3 gen_fast.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "set-tests", "generators"))
from gen_sets import FAST_POOL_NOTE, FAST_VECTOR_PRELUDE, check_finished, must_replace  # noqa: E402

DIR = os.environ.get("RANGE_DIR") or os.path.join(os.path.dirname(HERE), "range-queries")
FAMILIES = ("seg-tree", "lazy-seg-tree")
STEMS = (("template", "fast"), ("sparse", "sparse-fast"), ("letters", "letters-fast"))
FIELD = re.compile(r"^    vector<([^()\n]*)> ([\w, ]+)(;|\{)", re.M)
METHOD = r"^    (?!//|using |struct |template |explicit |{name}\b)((?:[\w:]+(?:<[^;(){{}}]*>)?[&*]* )+[\w]+\([^;{{}}]*\)(?: const)? \{{)"


def fast_cpp(text, source, target):
    name = re.findall(r"^template <typename T>\nstruct (\w+) \{", text, re.M)[-1]
    t = must_replace(text, source, target)
    start = t.index(f"template <typename T>\nstruct {name} {{")
    note = FAST_POOL_NOTE.replace("template.cpp", source)
    head, tail = t[:start] + note + FAST_VECTOR_PRELUDE, t[start:]
    tail, fields = FIELD.subn(r"    HotVector<\1> \2\3", tail)  # members only: signatures keep plain vector
    tail, methods = re.subn(METHOD.format(name=name), r"    LEETCODE_NO_SANITIZE \1", tail, flags=re.M)
    assert fields and methods >= 3, f"{target}: {fields} fields, {methods} methods"
    return head + tail


def main():
    written, folders = 0, 0
    for folder in sorted(os.listdir(DIR)):
        path = os.path.join(DIR, folder)
        base = os.path.join(path, "template.cpp")
        if not os.path.exists(base):
            continue
        family = re.search(r"@data-structure-type: (\S+)", open(base).read(2000))
        if not family or family.group(1) not in FAMILIES:
            continue
        folders += 1
        for stem, target in STEMS:
            source = os.path.join(path, stem + ".cpp")
            if os.path.exists(source):
                out = fast_cpp(open(source).read(), stem + ".cpp", target + ".cpp")
                open(os.path.join(path, target + ".cpp"), "w").write(check_finished(out, f"{folder}/{target}.cpp"))
                written += 1
    print(f"wrote {written} fast files in {folders} folders")


if __name__ == "__main__":
    main()
