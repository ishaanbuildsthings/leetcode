"""Writes graphs/floydWarshall{Directed,Undirected}{,.oneIndexed}.{py,cpp}.  python3 gen_floyd_warshall.py"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
GH = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/"

for kind in ("Directed", "Undirected"):
    directed = kind == "Directed"
    for one in (False, True):
        fn = f"floydWarshall{kind}"
        file = fn + (".oneIndexed" if one else "")
        lo, hi = ("1", "numNodes") if one else ("0", "numNodes - 1")
        edgeWord = "a -> b" if directed else "a <-> b, usable both ways"
        if one:
            pyEx = [
                f"#   dist = {fn}(4, [(1, 2, 4), (1, 3, 1), (3, 2, 2)])",
                "#   dist[1] -> [INF, 0, 3, 1, INF]    1 -> 2 costs 3 (through 3); node 4 has no edges, so it's INF",
                ("#   dist[2] -> [INF, INF, 0, INF, INF]  nothing leaves 2" if directed
                 else "#   dist[2] -> [INF, 3, 0, 2, INF]"),
                "#   dist[0] -> [INF, INF, INF, INF, INF]  row 0 is unused",
            ]
            shape = ["# Returns dist, a (numNodes + 1) x (numNodes + 1) matrix indexed by your labels: dist[a][b] = the shortest",
                     "# distance from a to b, INF if b can't be reached from a, 0 for a to itself.",
                     "# Node 0 doesn't exist: row 0 and column 0 are unused (all INF), ignore them."]
        else:
            pyEx = [
                f"#   dist = {fn}(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2)])",
                "#   dist[0] -> [0, 3, 1, INF]    0 -> 1 costs 3 (through 2); node 3 has no edges, so it's INF",
                ("#   dist[1] -> [INF, 0, INF, INF]  nothing leaves 1" if directed
                 else "#   dist[1] -> [3, 0, 2, INF]"),
            ]
            shape = ["# Returns dist, a numNodes x numNodes matrix: dist[a][b] = the shortest distance from a to b, INF if b",
                     "# can't be reached from a, 0 for a to itself."]
        head = [
            f"Floyd-Warshall, {kind.lower()} graph, {'1' if one else '0'}-indexed: shortest distance between every pair of nodes.",
            f"numNodes: how many nodes there are; the nodes are {lo}..{hi}. (A node with no edges never shows up",
            "in the edge list, so the count has to be passed.)",
            f"edges: [a, b, w] meaning {edgeWord}, with weight w >= 0. Repeated edges keep the cheapest; self-loops",
            "are ignored. A negative weight is an error (a negative loop would make some distances meaningless).",
        ]
        cx = "O(V^3 + E) time, O(V^2) space, V = numNodes, E = number of edges."
        size = "numNodes + 1" if one else "numNodes"

        # ---------- Python ----------
        py = [f"# Template by https://github.com/ishaanbuildsthings", f"# {GH}{file}.py", ""]
        py += ["# " + l for l in head]
        py += shape
        py += ["# Example:"] + pyEx
        py += ["# " + cx + " Negative weights raise ValueError.", "",
               "INF = float('inf')  # what unreachable pairs hold", "", "",
               f"def {fn}(numNodes, edges):",
               f"    size = {size}",
               f"    dist = [[INF] * size for _ in range(size)]",
               f"    for node in range({lo}, size):",
               f"        dist[node][node] = 0",
               f"    for a, b, w in edges:",
               f"        if not ({lo} <= a < size and {lo} <= b < size):",
               f"            raise ValueError(f\"{fn}: edge ({{a}}, {{b}}) is outside the nodes {lo}..{{size - 1}}\")",
               f"        if w < 0:",
               f"            raise ValueError(f\"{fn}: edge ({{a}}, {{b}}) has negative weight {{w}}\")",
               f"        if w < dist[a][b]:",
               f"            dist[a][b] = w"]
        if not directed:
            py += [f"        if w < dist[b][a]:",
                   f"            dist[b][a] = w"]
        py += [f"    # allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper",
               f"    for mid in range({lo}, size):",
               f"        midRow = dist[mid]",
               f"        for a in range({lo}, size):",
               f"            row = dist[a]",
               f"            toMid = row[mid]",
               f"            if toMid == INF:",
               f"                continue",
               f"            for b in range({lo}, size):",
               f"                through = toMid + midRow[b]",
               f"                if through < row[b]:",
               f"                    row[b] = through",
               f"    return dist", ""]
        if one:  # the min over row 0 / column 0 keeps them INF: nothing reaches node 0 and node 0 reaches nothing
            pass
        open(os.path.join(OUT, file + ".py"), "w").write("\n".join(py))

        # ---------- C++ ----------
        cppEx = [l.replace("#", "//", 1).replace("[", "{").replace("]", "}").replace("(", "{").replace(")", "}") for l in pyEx]
        # restore the call line's parentheses and the prose parentheses
        callArgs = "4, {{1, 2, 4}, {1, 3, 1}, {3, 2, 2}}" if one else "4, {{0, 1, 4}, {0, 2, 1}, {2, 1, 2}}"
        cppEx[0] = f"//   auto dist = {fn}({callArgs});"
        cppEx = [l.replace("{through 3}", "(through 3)").replace("{through 2}", "(through 2)") for l in cppEx]
        cppEx = [l.replace("dist{", "dist[").replace("} ->", "] ->", 1) if "dist{" in l else l for l in cppEx]
        cpp = [f"// Template by https://github.com/ishaanbuildsthings", f"// {GH}{file}.cpp",
               "#include <bits/stdc++.h>", "using namespace std;", "using ll = long long;", ""]
        cpp += ["// " + l for l in head]
        cpp += [l.replace("#", "//", 1) for l in shape]
        cpp += ["// Example:"] + cppEx
        cpp += ["// " + cx + " Negative weights throw invalid_argument.", "",
                "const ll INF = LLONG_MAX / 4;  // what unreachable pairs hold (/ 4 so adding two distances can't overflow)", "",
                f"vector<vector<ll>> {fn}(int numNodes, const vector<array<ll, 3>>& edges) {{",
                f"    int size = {size};",
                f"    vector<vector<ll>> dist(size, vector<ll>(size, INF));",
                f"    for (int node = {lo}; node < size; node++) dist[node][node] = 0;",
                f"    for (auto [a, b, w] : edges) {{",
                f"        if (a < {lo} || a >= size || b < {lo} || b >= size)",
                f"            throw out_of_range(\"{fn}: an edge is outside the nodes {lo}..{hi}\");",
                f"        if (w < 0) throw invalid_argument(\"{fn}: negative edge weight\");",
                f"        dist[a][b] = min(dist[a][b], w);"]
        if not directed:
            cpp += [f"        dist[b][a] = min(dist[b][a], w);"]
        cpp += ["    }",
                "    // allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper",
                f"    for (int mid = {lo}; mid < size; mid++) {{",
                "        const vector<ll>& midRow = dist[mid];",
                f"        for (int a = {lo}; a < size; a++) {{",
                "            ll toMid = dist[a][mid];",
                "            if (toMid == INF) continue;",
                "            vector<ll>& row = dist[a];",
                f"            for (int b = {lo}; b < size; b++) row[b] = min(row[b], toMid + midRow[b]);",
                "        }", "    }",
                "    return dist;", "}", ""]
        open(os.path.join(OUT, file + ".cpp"), "w").write("\n".join(cpp))

# the headers come from the shared usage text (graph_usage.py), same as the Usage panels
import sys
sys.path.insert(0, HERE)
from graph_usage import rewriteAll
rewriteAll()
