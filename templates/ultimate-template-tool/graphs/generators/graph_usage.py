"""The usage text of every graph template except the functional graph (which has its own generator): written into
each file's header comment and into site/lib/generated/graph-usage.ts for the Graphs tab's Usage panels, so the
two always match. Example outputs are computed by running the Python templates, so they can't drift.

    python3 graph_usage.py        (gen_floyd_warshall.py runs this too)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPHS = os.path.dirname(HERE)
SITE_TS = os.path.join(GRAPHS, "../../../site/lib/generated/graph-usage.ts")


def run(file, fn, *args, **kwargs):
    ns = {}
    exec(open(os.path.join(GRAPHS, file + ".py")).read(), ns)
    return ns[fn](*args, **kwargs)


def show(value, cpp, none):
    """A Python value as the language shows it: lists as [..] / {..}, None as the template's 'nothing' value."""
    if value is None:
        return none
    if isinstance(value, float) and value == float("inf"):
        return "INF"
    if isinstance(value, (list, tuple)):
        inner = ", ".join(show(x, cpp, none) for x in value)
        return "{" + inner + "}" if cpp else "[" + inner + "]"
    return str(value)


def lst(cpp, *xs):
    return show(list(xs), cpp, "")


def edgeList(edges, cpp):
    return show([list(e) for e in edges], cpp, "")


def boolWord(b, cpp):
    return ("true" if b else "false") if cpp else ("True" if b else "False")


def shape(directed, weighted, cpp):
    """How an edge list is written: [[from, to], ...] when directed, [[node1, node2], ...] when undirected."""
    names = ["from", "to"] if directed else ["node1", "node2"]
    if weighted:
        names.append("weight")
    inner = ", ".join(names)
    return "{{" + inner + "}, ...}" if cpp else "[[" + inner + "], ...]"


# ---------------------------------------------------------------- Dijkstra
def dijkstra(kind, cpp):
    fn = f"dijkstra{kind}"
    directed = kind == "Directed"
    none = "-1" if cpp else "None"
    edges = [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 5)]
    dist, prev = run(fn, fn, edges, 4, oneIndexed=True, source=1)
    call = (f"auto [dist, prev] = {fn}(edges, numNodes, oneIndexed, source);" if cpp
            else f"dist, prev = {fn}(edges, numNodes, oneIndexed, source)")
    exCall = f"{fn}({edgeList(edges, cpp)}, 4, {boolWord(True, cpp)}, 1)"
    route = [4]
    while prev[route[-1]] is not None:
        route.append(prev[route[-1]])
    route.reverse()
    return [
        call,
        f"  edges is a list of {'directed' if directed else 'undirected'} weighted edges "
        + shape(directed, True, cpp)
        + ("" if directed else ", usable both ways") + ", weights >= 0",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  oneIndexed is {boolWord(True, cpp)} when the nodes are 1..numNodes, {boolWord(False, cpp)} when they're 0..numNodes-1",
        "  source is the node every distance is measured from",
        f"  For example: {exCall}",
        "",
        f"dist -> the shortest distance from source to every node, e.g. {show(dist, cpp, none)}",
        f"  dist[node] is {none} if node can't be reached from source. With oneIndexed, dist[0] isn't a",
        f"  node and is always {none}. Here the best route to 4 costs {dist[4]}",
        "",
        f"prev -> the node right before each node on a shortest route from source, e.g. {show(prev, cpp, none)}",
        "  Only needed to rebuild the route itself: start at the target and keep stepping to prev until",
        "  you reach source, then reverse. Here the route to 4 is " + " -> ".join(map(str, route)) + ".",
        f"  {none} for source itself and for nodes that can't be reached",
        "",
        "O((V + E) log E) time, O(V + E) space. Negative weights "
        + ("throw invalid_argument" if cpp else "raise ValueError"),
    ]


# ---------------------------------------------------------------- topological sort
def topoSort(cpp):
    none = "{}" if cpp else "None"
    edges = [(1, 3), (2, 3), (3, 4)]
    order = run("topoSort", "topoSort", edges, 4, oneIndexed=True)
    cyc = run("topoSort", "topoSort", [(1, 2), (2, 1)], 2, oneIndexed=True)
    assert cyc is None
    return [
        ("vector<int> order = topoSort(edges, numNodes, oneIndexed);" if cpp else "order = topoSort(edges, numNodes, oneIndexed)"),
        "  edges is a list of directed edges " + shape(True, False, cpp)
        + ", meaning from has to come before to",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  oneIndexed is {boolWord(True, cpp)} when the nodes are 1..numNodes, {boolWord(False, cpp)} when they're 0..numNodes-1",
        f"  For example: topoSort({edgeList(edges, cpp)}, 4, {boolWord(True, cpp)})",
        "",
        f"order -> every node exactly once, with from before to for every edge, e.g. {show(order, cpp, none)}",
        "  Nodes with nothing pointing to them come first, like an order you could take courses in.",
        "  Reverse it if you want everything a node points to to come first",
        "",
        f"  {none} if the graph has a cycle, since then no order works. So this is also the",
        "  \"is it a DAG?\" check: " + ("isDag = !topoSort(edges, numNodes, oneIndexed).empty()  (for numNodes >= 1)" if cpp
                                       else "isDag = topoSort(edges, numNodes, oneIndexed) is not None"),
        "",
        "O(V + E) time and space",
    ]


# ---------------------------------------------------------------- strongly connected components
def scc(cpp):
    edges = [(1, 2), (2, 3), (3, 1), (4, 3)]
    s = run("scc", "buildScc", edges, 5, oneIndexed=True)
    big = max(range(s.numComponents), key=lambda c: len(s.componentNodes[c]))
    four = s.nodeToComponentId[4]
    return [
        ("Scc scc = buildScc(edges, numNodes, oneIndexed);" if cpp else "scc = buildScc(edges, numNodes, oneIndexed)"),
        "  A strongly connected component is a group of nodes that can all reach each other",
        "  edges is a list of directed edges " + shape(True, False, cpp)
        + "; repeated edges and self-loops are fine",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  oneIndexed is {boolWord(True, cpp)} when the nodes are 1..numNodes, {boolWord(False, cpp)} when they're 0..numNodes-1",
        f"  For example: buildScc({edgeList(edges, cpp)}, 5, {boolWord(True, cpp)})   (node 5 has no edges)",
        "",
        f"scc.numComponents -> how many components there are, e.g. {s.numComponents}",
        "",
        f"scc.nodeToComponentId[node] -> which component node is in, e.g. {show(s.nodeToComponentId, cpp, '-1')}",
        "  Component ids go from 0 to numComponents - 1. With oneIndexed, slot 0 isn't a node and is -1",
        "",
        f"scc.componentNodes[componentId] -> that component's nodes, increasing, e.g. {show(s.componentNodes, cpp, '')}",
        "",
        f"scc.componentAdj[componentId] -> the components it has edges into, e.g. {show(s.componentAdj, cpp, '')}",
        f"  Here component {four} (node 4) has an edge into component {big} (nodes "
        + ", ".join(map(str, s.componentNodes[big])) + "). Edges inside a component are",
        "  dropped, repeats are kept, and following these never loops back",
        "",
        "  Ids come out in reverse topological order: every edge goes from a bigger id to a smaller one,",
        "  so going through ids 0, 1, 2, ... handles a component only after everything it can reach",
        "",
        "O(V + E) time and space",
    ]


# ---------------------------------------------------------------- Euler paths / circuits
def euler(kind, isPath, cpp):
    directed = kind == "Directed"
    fn = f"euler{'Path' if isPath else 'Circuit'}{kind}"
    none = "{}" if cpp else "None"
    edgesWord = ("directed edges " if directed else "undirected edges ") + shape(directed, False, cpp)
    if isPath:
        ex = [(1, 2), (2, 3), (3, 1), (1, 4)]
        good = run(fn, fn, ex)
        if directed:
            ex2, kw2, args2 = [(1, 2), (2, 1)], {"start": 2, "end": 2}, ("2", "2")
            bad = [(1, 2), (1, 3)]
        else:
            ex2, kw2, args2 = [(1, 2), (2, 3)], {"start": 3}, ("3",)
            bad = [(1, 2), (1, 3), (1, 4)]
    else:
        ex = [(1, 2), (2, 3), (3, 1)]
        good = run(fn, fn, ex)
        ex2, kw2, args2 = ex, {"start": 2}, ("2",)
        bad = [(1, 2), (2, 3)]
    second = run(fn, fn, ex2, **kw2)
    assert run(fn, fn, bad) is None

    def callStr(edges, kw, args):
        if cpp:
            return f"{fn}({edgeList(edges, cpp)}" + "".join(", " + a for a in args) + ")"
        return f"{fn}({edgeList(edges, cpp)}" + "".join(f", {k}={v}" for k, v in kw.items()) + ")"

    if isPath:
        picked = ("the node with one more edge out than in starts, and the node with one more in than out ends"
                  if directed else "with two odd-degree nodes, the path runs from one to the other")
        lines = [
            (f"vector<int> walk = {fn}(edges, start, end);   // start, end optional (-1 = not given)" if cpp
             else f"walk = {fn}(edges, start=None, end=None)"),
            f"  edges is a list of {edgesWord}; repeated edges and self-loops are fine",
            "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
            "  start and end are optional: the nodes the walk has to start and end at. Left out, they're",
            f"  picked for you: {picked}.",
            ("  If every node has as many edges in as out, the walk is a circuit from any node with edges" if directed
             else "  If every node has even degree, the walk is a circuit from any node with edges"),
            f"  For example: {callStr(ex, {}, ())}",
            "",
            f"walk -> the nodes in walking order, using every edge exactly once, e.g. {show(good, cpp, none)}",
            f"  It has {'edges.size()' if cpp else 'len(edges)'} + 1 nodes and may end where it started (a circuit counts)",
            "",
            f"  {none} if there's no such walk: the degrees don't allow one, some edge can't be reached",
            "  from the start, or the start / end you gave doesn't fit",
            f"  With no edges at all: just the start or end if you gave one, else {'{}' if cpp else '[]'}",
            "",
            f"  {callStr(ex2, kw2, args2)} -> {show(second, cpp, none)}",
            f"  {callStr(bad, {}, ())} -> {none}",
        ]
    else:
        oddRule = ("some node has more edges in than out (or out than in)" if directed else "some node has odd degree")
        lines = [
            (f"vector<int> walk = {fn}(edges, start);   // start optional (-1 = not given)" if cpp
             else f"walk = {fn}(edges, start=None)"),
            f"  edges is a list of {edgesWord}; repeated edges and self-loops are fine",
            "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
            "  start is optional: the node the circuit has to start and end at. Left out, any node with edges",
            f"  For example: {callStr(ex, {}, ())}",
            "",
            f"walk -> the nodes in walking order, using every edge exactly once, e.g. {show(good, cpp, none)}",
            f"  It has {'edges.size()' if cpp else 'len(edges)'} + 1 nodes, and the first and last are the same node",
            "",
            f"  {none} if there's no circuit: {oddRule}, some edge can't be reached",
            "  from the start, or the start you gave has no edges",
            f"  With no edges at all: just the start if you gave one, else {'{}' if cpp else '[]'}",
            "",
            f"  {callStr(ex2, kw2, args2)} -> {show(second, cpp, none)}",
            f"  {callStr(bad, {}, ())} -> {none}",
        ]
    return lines + ["", "O(V + E) time and space, V = number of nodes, E = number of edges"]


# ---------------------------------------------------------------- Floyd-Warshall
def floydWarshall(kind, one, cpp):
    fn = f"floydWarshall{kind}"
    file = fn + (".oneIndexed" if one else "")
    directed = kind == "Directed"
    s = lambda x: x + one
    edges = [(s(0), s(1), 4), (s(0), s(2), 1), (s(2), s(1), 2)]
    dist = run(file, fn, 4, edges)
    rowA = s(0)
    lines = [
        (f"auto dist = {fn}(numNodes, edges);" if cpp else f"dist = {fn}(numNodes, edges)"),
        f"  edges is a list of {'directed' if directed else 'undirected'} weighted edges "
        + shape(directed, True, cpp)
        + ("" if directed else ", usable both ways") + ", weights >= 0",
        "  Repeated edges keep the cheapest; self-loops are ignored",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  For example: {fn}(4, {edgeList(edges, cpp)})   (node {s(3)} has no edges)",
        "",
        f"dist[a][b] -> the shortest distance from a to b, e.g. dist[{rowA}] = {show(dist[rowA], cpp, '')}",
        "  INF if b can't be reached from a, and 0 from a node to itself.",
        f"  Here {s(0)} -> {s(1)} costs {dist[s(0)][s(1)]} by going through {s(2)}, instead of {4} directly",
    ]
    if one:
        lines += ["  dist is a (numNodes + 1) x (numNodes + 1) matrix: node 0 doesn't exist, so row 0 and",
                  "  column 0 are unused (all INF)"]
    else:
        lines += ["  dist is a numNodes x numNodes matrix"]
    lines += [
        "",
        ("INF -> LLONG_MAX / 4, set at the top of the file: change it there if you need to" if cpp
         else "INF -> float('inf'), set at the top of the file"),
        "",
        "O(V^3 + E) time, O(V^2) space. Negative weights " + ("throw invalid_argument" if cpp else "raise ValueError"),
        "(a loop with negative total weight would make distances meaningless)",
    ]
    return lines


# ---------------------------------------------------------------- undirected components
def undirectedComponents(cpp):
    edges = [(1, 2), (2, 3), (4, 5)]
    comps = run("undirectedComponents", "undirectedComponents", edges, 6, oneIndexed=True)
    lines = [
        ("vector<Component> components = undirectedComponents(edges, numNodes, oneIndexed);" if cpp
         else "components = undirectedComponents(edges, numNodes, oneIndexed)"),
        "  edges is a list of undirected edges " + shape(False, False, cpp)
        + "; repeated edges and self-loops are fine",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  oneIndexed is {boolWord(True, cpp)} when the nodes are 1..numNodes, {boolWord(False, cpp)} when they're 0..numNodes-1",
        f"  For example: undirectedComponents({edgeList(edges, cpp)}, 6, {boolWord(True, cpp)})   (node 6 has no edges)",
        "",
    ]
    if cpp:
        w = max(len(lst(cpp, *n)) for n, _ in comps)
        lines += ["components -> one {nodes, edgeList} per component, e.g."]
        lines += [f"  components[{i}].nodes -> {lst(cpp, *n).ljust(w)}   components[{i}].edgeList -> {edgeList(e, cpp)}"
                  for i, (n, e) in enumerate(comps)]
    else:
        lines += ["components -> one (nodes, edgeList) per component, e.g.",
                  "  [" + ", ".join(f"({lst(False, *n)}, {edgeList(e, False)})" for n, e in comps) + "]"]
    lines += [
        "  nodes are increasing, and edgeList is that component's edges in the order you gave them.",
        "  A node with no edges is a component by itself, with no edges",
        "",
        "  Components are ordered by their smallest node, and "
        + ("components.size()" if cpp else "len(components)") + " is how many there are",
        "",
        "O((V + E) α(V)) time (union-find, so practically linear), O(V + E) space",
    ]
    return lines


# ---------------------------------------------------------------- cycle checks
def hasCycle(kind, cpp):
    directed = kind == "Directed"
    fn = f"hasCycle{kind}"
    ex = [(1, 2), (2, 3), (3, 1)]
    if directed:
        no, yes2 = [(1, 2), (1, 3), (2, 3)], [(1, 2), (2, 1)]
    else:
        no, yes2 = [(1, 2), (2, 3)], [(1, 2), (2, 1)]
    assert run(fn, fn, ex) is True and run(fn, fn, no) is False and run(fn, fn, yes2) is True
    T, F = boolWord(True, cpp), boolWord(False, cpp)
    lines = [
        (f"bool hasCycle = {fn}(edges);" if cpp else f"hasCycle = {fn}(edges)"),
        f"  edges is a list of {'directed' if directed else 'undirected'} edges " + shape(directed, False, cpp),
        "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
        "  (a node with no edges can't be on a cycle, so how many nodes there are doesn't matter)",
        f"  For example: {fn}({edgeList(ex, cpp)})",
        "",
    ]
    if directed:
        lines += [
            f"hasCycle -> {T} if you can start at some node, follow edges, and get back to it, e.g. {T}",
            "  A self-loop counts as a cycle. 1 -> 2 with 2 -> 1 is a cycle, but 1 -> 2, 1 -> 3, 2 -> 3 is not,",
            "  since you can't get back to where you started",
        ]
    else:
        lines += [
            f"hasCycle -> {T} if there's a loop anywhere in the graph, e.g. {T}",
            "  A self-loop counts as a cycle, and so do two copies of the same edge, since you can go out",
            "  along one and come back along the other",
        ]
    lines += [
        "",
        f"  {fn}({edgeList(no, cpp)}) -> {F}",
        f"  {fn}({edgeList(yes2, cpp)}) -> {T}" + ("" if directed else "    (the same edge twice)"),
        "",
        ("O(V + E) time and space, V = number of nodes, E = number of edges" if directed
         else "O(V + E α(V)) time (union-find, so practically linear), O(V) space, V = number of nodes"),
    ]
    return lines


# ---------------------------------------------------------------- minimum spanning tree
def minimumSpanningTrees(cpp):
    fn = "minimumSpanningTrees"
    edges = [(1, 2, 2), (2, 3, 2), (1, 3, 3), (3, 4, 1)]
    trees = run(fn, fn, edges)
    assert len(trees) == 1 and sum(e[2] for e in trees[0]) == 5
    apart = [(1, 2, 5), (3, 4, 1)]
    assert run(fn, fn, apart) == [[[1, 2, 5]], [[3, 4, 1]]]
    return [
        (f"vector<vector<array<ll, 3>>> trees = {fn}(edges);" if cpp else f"trees = {fn}(edges)"),
        "  edges is a list of undirected weighted edges " + shape(False, True, cpp) + "; negative",
        "  weights, repeated edges and self-loops are fine",
        "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
        f"  For example: {fn}({edgeList(edges, cpp)})",
        "",
        f"trees -> one minimum spanning tree for each separate piece of the graph, e.g. {show(trees, cpp, '')}",
        "  Each tree is a list of its edges, cheapest first, written exactly as you gave them. A connected",
        "  graph has one piece, so you get a list holding one tree: use trees[0]. Adding up a tree's",
        f"  weights gives its total, here {sum(e[2] for e in trees[0])}",
        "",
        f"  {fn}({edgeList(apart, cpp)}) -> {show(run(fn, fn, apart), cpp, '')}",
        "  1 - 2 and 3 - 4 aren't connected, so that's two trees. Trees are ordered by their smallest",
        "  node, and a node with no edges has no tree",
        "",
        "  What each tree minimizes:",
        "  - the total weight, over every way of picking edges that connects all the nodes of its piece",
        "  - the biggest edge you have to cross between any two nodes: the path through the tree has the",
        "    smallest possible biggest edge of any path between them in the whole graph. Here 1 to 3",
        "    through the tree crosses edges of weight 2 and 2, while the direct edge weighs 3",
        "",
        "  What it does NOT minimize: the distance between two nodes. 1 to 3 through the tree costs",
        "  2 + 2 = 4, but the direct edge costs 3. For distances use Dijkstra or Floyd-Warshall",
        "",
        "  If several trees tie for cheapest, you get one of them",
        "",
        "O(E log E) time, O(V + E) space, V = number of nodes, E = number of edges",
    ]


# ---------------------------------------------------------------- bridges / articulation points
def bridgesUsage(cpp):
    fn = "bridges"
    edges = [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (4, 5)]
    got = run(fn, fn, edges)
    assert got == [[3, 4]]
    chain = [(1, 2), (2, 3)]
    assert run(fn, fn, chain) == [[1, 2], [2, 3]]
    return [
        (f"vector<pair<int, int>> bridgeEdges = {fn}(edges);" if cpp else f"bridgeEdges = {fn}(edges)"),
        "  edges is a list of undirected edges " + shape(False, False, cpp) + "; repeated edges and",
        "  self-loops are fine",
        "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
        "  (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)",
        f"  For example: {fn}({edgeList(edges, cpp)})",
        "",
        f"bridgeEdges -> every edge that, if removed, splits its component in two, e.g. {edgeList(got, cpp)}",
        "  Each edge is written exactly as you gave it, in the order you gave them",
        "",
        "  Here 1, 2, 3 form a triangle, so removing any one of those edges still leaves another way",
        "  around. Removing 3 - 4 cuts 4 and 5 off. 4 - 5 is listed twice, so neither copy is a bridge:",
        "  the other copy still connects them",
        "",
        f"  {fn}({edgeList(chain, cpp)}) -> {edgeList(run(fn, fn, chain), cpp)}    (in a tree, every edge is a bridge)",
        "",
        "O(V + E) time and space, V = number of nodes, E = number of edges",
    ]


def articulationPointsUsage(cpp):
    fn = "articulationPoints"
    edges = [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)]
    got = run(fn, fn, edges)
    assert got == [3, 4]
    star = [(1, 2), (1, 3), (1, 4)]
    assert run(fn, fn, star) == [1]
    return [
        (f"vector<int> cutNodes = {fn}(edges);" if cpp else f"cutNodes = {fn}(edges)"),
        "  edges is a list of undirected edges " + shape(False, False, cpp) + "; repeated edges and",
        "  self-loops are fine",
        "  The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed",
        "  (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)",
        f"  For example: {fn}({edgeList(edges, cpp)})",
        "",
        f"cutNodes -> every node that, if removed with its edges, splits its component into two or more",
        f"  pieces, increasing, e.g. {lst(cpp, *got)}",
        "",
        "  Here removing 3 separates the triangle's 1 and 2 from 4 and 5, and removing 4 cuts 5 off.",
        "  Removing 1 or 2 leaves everything else connected",
        "",
        f"  {fn}({edgeList(star, cpp)}) -> {lst(cpp, 1)}    (removing the center leaves three pieces)",
        "",
        "O(V + E) time and space, V = number of nodes, E = number of edges",
    ]


# ---------------------------------------------------------------- bipartite split
def bipartiteUsage(cpp):
    fn = "bipartiteSplit"
    edges = [(1, 2), (2, 3), (3, 4)]
    side1, side2 = run(fn, fn, edges, 5, oneIndexed=True)
    assert (side1, side2) == ([1, 3, 5], [2, 4])
    odd = [(1, 2), (2, 3), (3, 1)]
    assert run(fn, fn, odd, 3, oneIndexed=True) is None
    lines = [
        (f"BipartiteSplit split = {fn}(edges, numNodes, oneIndexed);" if cpp
         else f"split = {fn}(edges, numNodes, oneIndexed)"),
        "  edges is a list of undirected edges " + shape(False, False, cpp) + "; repeated edges are fine",
        "  numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)",
        f"  oneIndexed is {boolWord(True, cpp)} when the nodes are 1..numNodes, {boolWord(False, cpp)} when they're 0..numNodes-1",
        f"  For example: {fn}({edgeList(edges, cpp)}, 5, {boolWord(True, cpp)})   (node 5 has no edges)",
        "",
    ]
    if cpp:
        lines += [
            "split.possible -> true if the nodes can be split into two sides with every edge going between",
            "  the sides (none inside a side), e.g. true",
            "",
            f"split.side1, split.side2 -> the two sides, each increasing, e.g. {lst(cpp, *side1)} and {lst(cpp, *side2)}",
            "  Empty when it's not possible.",
        ]
    else:
        lines += [
            f"split -> the two sides (side1, side2), each increasing, e.g. ({lst(cpp, *side1)}, {lst(cpp, *side2)})",
            "  Every edge goes between the two sides, none inside a side.",
        ]
    lines += [
        "  Each component's smallest node goes on side1. A node with no edges is on side1 too (it could go",
        "  on either side)",
        "",
        f"  {'split.possible is false' if cpp else 'None'} if it's impossible: that happens exactly when there's a loop with an odd",
        "  number of edges, like a triangle. A self-loop always makes it impossible",
        "",
        f"  {fn}({edgeList(odd, cpp)}, 3, {boolWord(True, cpp)}) -> {'{false, {}, {}}' if cpp else 'None'}",
        "",
        "O(V + E) time and space",
    ]
    return lines


def allUsages():
    out = {}
    for lang in ("py", "cpp"):
        cpp = lang == "cpp"
        for kind in ("Directed", "Undirected"):
            out.setdefault(f"dijkstra{kind}", {})[lang] = dijkstra(kind, cpp)
            for isPath in (True, False):
                out.setdefault(f"euler{'Path' if isPath else 'Circuit'}{kind}", {})[lang] = euler(kind, isPath, cpp)
            for one in (0, 1):
                out.setdefault(f"floydWarshall{kind}" + (".oneIndexed" if one else ""), {})[lang] = floydWarshall(kind, one, cpp)
        out.setdefault("topoSort", {})[lang] = topoSort(cpp)
        out.setdefault("scc", {})[lang] = scc(cpp)
        out.setdefault("undirectedComponents", {})[lang] = undirectedComponents(cpp)
        out.setdefault("minimumSpanningTrees", {})[lang] = minimumSpanningTrees(cpp)
        out.setdefault("bridges", {})[lang] = bridgesUsage(cpp)
        out.setdefault("articulationPoints", {})[lang] = articulationPointsUsage(cpp)
        out.setdefault("bipartiteSplit", {})[lang] = bipartiteUsage(cpp)
        for kind in ("Directed", "Undirected"):
            out.setdefault(f"hasCycle{kind}", {})[lang] = hasCycle(kind, cpp)
    return out


def rewriteHeader(path, usage, cpp):
    """Replace the header comment block (after the byline / includes, before the code) with the usage text."""
    lines = open(path).read().split("\n")
    mark = "//" if cpp else "#"
    i = 2  # past the byline
    while i < len(lines) and not lines[i].startswith(mark):  # includes, usings, blank lines
        i += 1
    j = i
    while j < len(lines) and lines[j].startswith(mark):
        j += 1
    assert i > 2 and j > i, path
    new = [(f"{mark} {line}").rstrip() for line in usage]
    open(path, "w").write("\n".join(lines[:i] + new + lines[j:]))


def rewriteAll():
    usages = allUsages()
    for file, byLang in usages.items():
        for lang, usage in byLang.items():
            rewriteHeader(os.path.join(GRAPHS, f"{file}.{lang}"), usage, lang == "cpp")
    ts = ["// Generated by templates/ultimate-template-tool/graphs/generators/graph_usage.py: the graph templates' Usage",
          "// panel text, the same lines as each file's header", "",
          "export const GRAPH_USAGE: Record<string, { py: string; cpp: string }> = {"]
    for file in sorted(usages):
        ts.append(f"  {json.dumps(file)}: {{")
        for lang in ("py", "cpp"):
            ts.append(f"    {lang}: {json.dumps(chr(10).join(usages[file][lang]))},")
        ts.append("  },")
    ts.append("};")
    open(SITE_TS, "w").write("\n".join(ts) + "\n")


if __name__ == "__main__":
    rewriteAll()
