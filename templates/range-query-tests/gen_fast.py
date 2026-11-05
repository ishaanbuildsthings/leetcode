"""Fast mode for the range query templates: writes fast.cpp beside template.cpp, sparse-fast.cpp beside sparse.cpp
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
# a vector member can also be built from a plain vector
PRELUDE = must_replace(FAST_VECTOR_PRELUDE, "    using vector<U>::vector;\n", """    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
""")
STEMS = (("template", "fast"), ("sparse", "sparse-fast"), ("letters", "letters-fast"))
FIELD = re.compile(r"^    (static inline |mutable )?vector<([^()\n]*)> ([\w, ]+)(;|\{)", re.M)
METHOD = r"^    (?!//|using |struct |template |explicit |{name}\b)((?:[\w:]+(?:<[^;(){{}}]*>)?[&*]* )+[\w]+\([^;{{}}]*\)(?: const)? \{{)"


def fast_cpp(text, source, target):
    names = re.findall(r"^template <typename T>\nstruct (\w+) \{", text, re.M)
    assert names, f"{target}: no template struct"
    name = names[-1]
    t = must_replace(text, source, target)
    start = t.index(f"template <typename T>\nstruct {name} {{")
    note = FAST_POOL_NOTE.replace("template.cpp", source)
    head, tail = t[:start] + note + PRELUDE, t[start:]
    tail, fields = FIELD.subn(r"    \1HotVector<\2> \3\4", tail)  # members only: signatures keep plain vector
    tail, methods = re.subn(METHOD.format(name=name), r"    LEETCODE_NO_SANITIZE \1", tail, flags=re.M)
    assert fields and methods >= 3, f"{target}: {fields} fields, {methods} methods"
    return head + tail


def main():
    written, folders, skipped = 0, 0, []
    for folder in sorted(os.listdir(DIR)):
        path = os.path.join(DIR, folder)
        if not os.path.exists(os.path.join(path, "template.cpp")):
            continue
        made = {}
        try:  # a folder gets fast mode in every version it has, or in none
            for stem, target in STEMS:
                source = os.path.join(path, stem + ".cpp")
                if os.path.exists(source):
                    out = fast_cpp(open(source).read(), stem + ".cpp", target + ".cpp")
                    made[target] = check_finished(out, f"{folder}/{target}.cpp")
        except AssertionError as e:
            skipped.append(f"{folder}: {e}")
            continue
        for target, out in made.items():
            target_path = os.path.join(path, target + ".cpp")
            if not os.path.exists(target_path) or open(target_path).read() != out:
                open(target_path, "w").write(out)
                written += 1
        folders += 1
    print(f"{folders} folders have fast mode, {written} files written, {len(skipped)} folders skipped")
    for line in skipped[:8]:
        print(" ", line[-90:])


if __name__ == "__main__":
    main()
