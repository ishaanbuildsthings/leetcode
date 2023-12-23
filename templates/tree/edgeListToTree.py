# given a list of adjacenies for a tree, this constructs a tree in the form of `children` in O(n) time and space
# in theory we don't need a seen set, we can just pass the parent to the child each call

edgeMap = defaultdict(list)
for a, b in edges:
    edgeMap[a].append(b)
    edgeMap[b].append(a)

children = defaultdict(list) # maps a node to its children
seen = set()

def buildTree(node):
    seen.add(node)

    for adj in edgeMap[node]:
        # skip nodes we have already seen to prevent back and forth
        if adj in seen:
            continue
        children[node].append(adj)
        buildTree(adj)
buildTree(0) # arbitrary root at 0
