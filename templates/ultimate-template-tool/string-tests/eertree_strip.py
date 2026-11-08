# Keeps only the parts of a marked template that the chosen ops need: the same rules as site/lib/eertree-picker.ts.
# A line "# @if a b+c" (or "// @if ...") opens a block kept when any space-separated term holds, where a term holds when
# every '+'-joined op in it is chosen; "@else" and "@endif" close it; blocks nest. Marker lines never reach the output.
import re

MARK = re.compile(r"^\s*(?:#|//) @(if|else|endif)\b ?(.*)$")


def strip(code, chosen):
    out, stack = [], []  # stack of (parentKeeps, thisBranchKeeps)
    keeping = True
    for line in code.split("\n"):
        m = MARK.match(line)
        if not m:
            if keeping:
                out.append(line)
            continue
        kind, rest = m.group(1), m.group(2).strip()
        if kind == "if":
            cond = any(all(op in chosen for op in term.split("+")) for term in rest.split())
            stack.append((keeping, cond))
            keeping = keeping and cond
        elif kind == "else":
            parent, cond = stack[-1]
            stack[-1] = (parent, not cond)
            keeping = parent and not cond
        else:
            keeping = stack.pop()[0]
    assert not stack, "unclosed @if"
    return "\n".join(out)
