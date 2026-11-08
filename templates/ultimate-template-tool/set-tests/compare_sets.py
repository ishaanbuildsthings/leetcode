"""Report what changed between two generated copies of templates/sets, and prove the public interface did not.

    python3 compare_sets.py OLD_DIR NEW_DIR

Lists changed / added / removed files per structure, and fails if any public method of a default template
(template.py / template.cpp) disappeared or changed its signature. New private helpers are fine.
"""
import collections
import hashlib
import os
import re
import sys

from cover_sets import split


def files(root):
    out = {}
    for folder in os.listdir(root):
        path = os.path.join(root, folder)
        if os.path.isdir(path):
            for name in os.listdir(path):
                if name.endswith((".py", ".cpp")):
                    out[f"{folder}/{name}"] = os.path.join(path, name)
    return out


def digest(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def public_api(path):
    """{method: signature} for the methods that carry an '-- ' doc comment, which is what the template publishes."""
    text = open(path).read()
    api = {}
    if path.endswith(".py"):
        for m in re.finditer(r"^    def ([a-zA-Z]\w*)\(([^)]*)\):", text, re.M):
            api[m.group(1)] = m.group(2)
        return api
    lines = text.split("\n")
    for i, line in enumerate(lines[:-1]):
        if line.strip().startswith("// O(") and " -- " in line:
            j = i + 1
            while j < len(lines) - 1 and lines[j].strip().startswith("//"):  # (a doc comment can wrap onto more lines)
                j += 1
            sig = re.sub(r"\b__attribute__\(\(.*?\)\)\s*|\bFENWICK_\w+\s+|\bFAST_\w+\s+", "", lines[j].strip())
            name = re.search(r"(\w+)\(", sig)
            if name:
                api[name.group(1)] = re.sub(r"\s*\{.*$", "", sig)
    return api


def main():
    old, new = files(sys.argv[1]), files(sys.argv[2])
    changed = collections.Counter()
    bad = []
    for key in sorted(set(old) & set(new)):
        if digest(old[key]) != digest(new[key]):
            changed[split(key.split("/")[0])[0]] += 1
            if key.split("/")[1].startswith(("template", "distinct")):
                a, b = public_api(old[key]), public_api(new[key])
                for m, sig in a.items():
                    if b.get(m) != sig:
                        bad.append(f"{key}: {m}({sig}) -> {b.get(m)}")
    added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
    print(f"changed {sum(changed.values())}, added {len(added)}, removed {len(removed)}, same {len(set(old) & set(new)) - sum(changed.values())}")
    for t, c in changed.most_common():
        print(f"  {t}: {c} changed")
    kinds = collections.Counter(a.split("/")[1] for a in added)
    if kinds:
        print("  added:", dict(kinds))
    for line in bad[:20]:
        print("INTERFACE CHANGED", line)
    if removed:
        print("REMOVED", removed[:10])
    sys.exit(1 if bad or removed else 0)


if __name__ == "__main__":
    main()
