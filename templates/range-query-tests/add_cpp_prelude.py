"""Every C++ template the site serves starts with the same three lines, so a pasted template compiles on its own:

    #include <bits/stdc++.h>
    using namespace std;
    using ll = long long;

The range query generators don't write them, so run this after any of them (safe to run again; it skips finished files).
gen_sets.py writes them itself.

    python3 add_cpp_prelude.py [more folders ...]
"""

import os
import sys
import time

INCLUDE = "#include <bits/stdc++.h>\n"
STD = "using namespace std;\n"
LL = "using ll = long long;\n"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ROOTS = ["templates/range-queries", "templates/segment-trees/generic", "templates/next-permutation", "templates/bubble-sort",
         "site/public/range-query-templates"]


def with_prelude(text):
    if INCLUDE + STD + LL in text:
        return text
    if INCLUDE + STD in text:
        return text.replace(INCLUDE + STD, INCLUDE + STD + LL, 1)
    lines = text.split("\n")
    head = 2 if lines[0].startswith("// Template by") else 0
    return "\n".join(lines[:head]) + ("\n" if head else "") + INCLUDE + STD + LL + "\n" + "\n".join(lines[head:])


def main():
    roots = [os.path.join(REPO, r) for r in ROOTS] + sys.argv[1:]
    start, changed, seen = time.time(), 0, 0
    for root in roots:
        for folder, _, names in os.walk(root):
            for name in names:
                if not name.endswith(".cpp"):
                    continue
                path = os.path.join(folder, name)
                seen += 1
                text = open(path).read()
                new = with_prelude(text)
                if new != text:
                    open(path, "w").write(new)
                    changed += 1
                if time.time() - start > 150:
                    print(f"paused: {changed} changed of {seen} seen; run again to finish")
                    return
    print(f"finished: {changed} changed of {seen} files")


if __name__ == "__main__":
    main()
