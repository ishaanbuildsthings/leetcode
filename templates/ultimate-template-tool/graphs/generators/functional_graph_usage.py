def usageText(one, cpp):
    L = (lambda *xs: "{" + ", ".join(map(str, xs)) + "}") if cpp else (lambda *xs: "[" + ", ".join(map(str, xs)) + "]")
    nodes = ("1..edges.size()" if cpp else "1..len(edges)") if one else ("0..edges.size()-1" if cpp else "0..len(edges)-1")
    none = "-1" if cpp else "None"
    cyc = L(L(1, 3, 9), L(2), L(4, 10))
    t2 = "" if one else L(0, 2)
    if cpp:
        rows = [(L(1, 3, 9), L(L(5, 6, 3), L(7, 6))), (L(2), L(t2) if t2 else "{}"), (L(4, 10), L(L(8, 4)))]
        w = max(len(c) for c, _ in rows)
        compsEx = [f"  components()[{i}].cycle -> {c.ljust(w)}   components()[{i}].tails -> {t}" for i, (c, t) in enumerate(rows)]
        compsHead = "fg.components() -> one {cycle, tails} per component, in componentId order, e.g."
        compsBody = "  .cycle is the same list as fg.cycles()[componentId]. Each of .tails is a walk that starts"
    else:
        compsEx = [f"  [({L(1, 3, 9)}, {L(L(5, 6, 3), L(7, 6))}), ({L(2)}, {L(t2) if t2 else '[]'}), ({L(4, 10)}, {L(L(8, 4))})]"]
        compsHead = "fg.components() -> one (cycle, tails) per component, in componentId order, e.g."
        compsBody = "  cycle is the same list as fg.cycles()[componentId]. Each tail is a walk that starts at a"
    ctor = ("FunctionalGraph fg(edges);" if cpp else "fg = FunctionalGraph(edges)")
    edgesType = "vector<array<int, 2>> {{from, to}, ...}" if cpp else "[[from, to], ...]"
    lines = [
        ctor,
        f"  edges is a list of directed edges {edgesType}, with exactly one edge leaving",
        f"  each node, so the nodes are {nodes} (it errors otherwise)" + ("; there is no node 0" if one else ""),
        "",
        f"fg.cycles() -> a list of every cycle, e.g. {cyc}",
        "  Only nodes inside cycles, never the nodes on tails leading into them. Each cycle is in walking",
        "  order (1 -> 3 -> 9 -> 1) and starts at its smallest node. Here 2 points to itself",
        "",
        "fg.componentId(node) -> which component node is in, e.g. 1",
        "  Works for every node, on a cycle or not. It's an index into fg.cycles(), from 0 up to",
        f"  {'fg.cycles().size()' if cpp else 'len(fg.cycles())'} - 1: here 1 means node ends up on the cycle {L(2)}",
        "",
        "fg.numEdgesToCrossBeforeCycle(node) -> edges node crosses before it's inside a cycle, e.g. 2",
        "  0 if node is already on a cycle",
        "",
        "fg.firstCycleNodeHit(node) -> the first cycle node that node reaches, e.g. 3",
        "  node itself if it's already on a cycle",
        "",
        "fg.kthNext(node, k) -> the node you land on after k steps from node, e.g. 9",
        "  Any k >= 0, even 10^18. kthNext(node, 0) is node",
        "",
        "fg.stepsFromTo(a, b) -> how many steps it takes to walk from a to b, e.g. 4",
        f"  {none} if a never reaches b, 0 if a == b",
        "",
        compsHead,
    ] + compsEx + [
        compsBody,
    ]
    if cpp:
        lines += ["  at a node nothing points to and follows edges until it reaches a node already listed, which",
                  "  is included: {5, 6, 3} is 5 -> 6 -> 3, and {7, 6} is 7 -> 6, joining that walk at 6"]
    else:
        lines += ["  node nothing points to and follows edges until it reaches a node already listed, which is",
                  "  included: [5, 6, 3] is 5 -> 6 -> 3, and [7, 6] is 7 -> 6, joining that walk at 6"]
    lines += ["",
              "Build O(V) time and space. Every method is O(1) except kthNext, which is O(log V) when k",
              "stops before reaching the cycle. " + ("Invalid nodes or a negative k throw invalid_argument" if cpp
                                                     else "Invalid nodes or a negative k raise ValueError")]
    return lines

# the example graph behind the text, to check it
def exampleEdges(one):
    e = [(1, 3), (3, 9), (9, 1), (2, 2), (4, 10), (10, 4), (5, 6), (6, 3), (7, 6), (8, 4)]
    return e if one else e + [(0, 2)]
