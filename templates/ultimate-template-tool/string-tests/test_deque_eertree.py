import random
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eertree_strip import strip

OPS = ["append", "appendLeft", "pop", "popLeft", "numDistinctPals", "numPalsTotal", "longestPalEndingAtCurrentR",
       "longestPalStartingAtCurrentL", "longestPal", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL"]
LINKS = ["quickLinks", "itemLinks", "persistentLinks"]
SRC = open(os.path.join(HERE, "..", "strings", "DequeEertree.py")).read()
DequeEertree = None  # set per link structure in main()


def isPal(seq, i, j):
    while i < j:
        if seq[i] != seq[j]:
            return False
        i += 1
        j -= 1
    return True


def brute(seq):
    n = len(seq)
    distinct = set()
    total = 0
    for i in range(n):
        for j in range(i, n):
            if isPal(seq, i, j):
                distinct.add(tuple(seq[i:j + 1]))
                total += 1
    longR = max((n - i for i in range(n) if isPal(seq, i, n - 1)), default=0)
    longL = max((j + 1 for j in range(n) if isPal(seq, 0, j)), default=0)
    return len(distinct), total, longR, longL


def surfaces(seq):
    n = len(seq)
    pre = [max(l for l in range(1, n - i + 1) if isPal(seq, i, i + l - 1)) for i in range(n)]
    suf = [max(l for l in range(1, j + 2) if isPal(seq, j - l + 1, j)) for j in range(n)]
    return {(i, j) for i in range(n) for j in range(i, n) if pre[i] == suf[j] == j - i + 1}


def checkInternals(et, seq):
    m = et._mask
    surf = surfaces(seq)
    for i in range(len(seq)):
        node = et._preSurf[(et._l + i) & m]
        js = [j for (a, j) in surf if a == i]
        if js:
            assert node and et._lens[node] == js[0] - i + 1, "preSurf"
        else:
            assert node == 0, "preSurf extra"
    alive = len(et._to)
    assert alive == len({tuple(seq[i:j + 1]) for i in range(len(seq)) for j in range(i, len(seq)) if isPal(seq, i, j)})
    assert sum(et._cnt) == len(surf)


def check(et, seq, deep):
    got = (et.numDistinctPals(), et.numPalsTotal(), et.longestPalEndingAtCurrentR(), et.longestPalStartingAtCurrentL())
    exp = brute(seq)
    assert got == exp, (seq, got, exp)
    longest = max((j - i + 1 for i in range(len(seq)) for j in range(i, len(seq)) if isPal(seq, i, j)), default=0)
    assert et.longestPal() == longest, (seq, et.longestPal(), longest)
    n = len(seq)
    assert et.numPalsEndingAtCurrentR() == sum(isPal(seq, i, n - 1) for i in range(n))
    assert et.numPalsStartingAtCurrentL() == sum(isPal(seq, 0, j) for j in range(n))
    assert len(et) == len(seq)
    if deep:
        checkInternals(et, seq)


def randItem(kind, k):
    if kind == "str":
        return "abcdefghijklmnopqrstuvwxyz"[random.randrange(k)]
    if kind == "int":
        return random.randrange(k) - k // 2
    return (random.randrange(k) % 2, -(random.randrange(k) // 2))


def runCase(kind, k, deep):
    n0 = random.randint(0, 8)
    init = [randItem(kind, k) for _ in range(n0)]
    if kind == "str":
        et = DequeEertree("".join(init))
    elif kind == "int":
        et = DequeEertree(init)
    else:
        et = DequeEertree(tuple(init))
    seq = list(init)
    check(et, seq, deep)
    ops = random.randint(1, 60)
    pushBias = random.choice([0.3, 0.5, 0.7])
    for _ in range(ops):
        r = random.random()
        if r < pushBias or not seq:
            x = randItem(kind, k)
            if random.random() < 0.5:
                et.append(x)
                seq.append(x)
            else:
                et.appendLeft(x)
                seq.insert(0, x)
        else:
            if random.random() < 0.5:
                assert et.pop() == seq.pop()
            else:
                assert et.popLeft() == seq.pop(0)
        if len(seq) > 25:
            # drain to empty, then refill
            while seq:
                if random.random() < 0.5:
                    assert et.pop() == seq.pop()
                else:
                    assert et.popLeft() == seq.pop(0)
                check(et, seq, deep)
        check(et, seq, deep)
    for fn in (et.pop, et.popLeft):
        while seq:
            fn()
            seq.pop()
        try:
            fn()
            assert False
        except IndexError as e:
            assert str(e) == "pop from an empty DequeEertree"
    check(et, seq, deep)


def main():
    global DequeEertree
    random.seed(12345)
    cases = 0
    start = time.time()
    for link in LINKS:  # every op, once per link structure
        env = {}
        exec(strip(SRC, set(OPS) | {link}), env)
        DequeEertree = env["DequeEertree"]
        for kind in ("str", "int", "tuple"):
            for k in (1, 2, 3, 26):
                if kind == "tuple" and k == 26:
                    k = 8
                for t in range(600):
                    runCase(kind, k, deep=(t % 5 == 0))
                    cases += 1
        if link == "persistentLinks":  # the trie's reference counts: every node still referenced is reachable
            et = DequeEertree()
            for _ in range(3000):
                if random.random() < 0.55 or not len(et):
                    (et.append if random.random() < 0.5 else et.appendLeft)(random.randrange(6))
                else:
                    (et.pop if random.random() < 0.5 else et.popLeft)()
            live = len(et._trieRefs) - 1 - len(et._trieFree)
            reachable, stack = set(), [et._linkRoot[node] for node in et._to.values()]
            while stack:
                t = stack.pop()
                if t and t not in reachable:
                    reachable.add(t)
                    stack += [et._trieLeft[t], et._trieRight[t]]
            assert live == len(reachable), (live, len(reachable))  # nothing leaks, nothing reachable was freed
    print("python stress ok:", cases, "cases (all three link structures) in %.1fs" % (time.time() - start))


if __name__ == "__main__":
    main()
