# TEMPLATE
# n means we initialize an empty DSU with nodes [0:n-1]
# unions by depth

class DSU:
    def __init__(self, n):
        self.parents = {} # maps a node to SOME parent, depends on the current amount of path compression, doesn't always map directly to the representative parent, may need to follow a chain
        self.depths = {} # maps the representative parent to its depth
        for node in range(n):
            self.parents[node] = node
            self.depths[node] = 1

    # finds the representative parent for a node and path compresses
    # def _find(self, node):
    # TODO: check path compression applies to everything
    #     while self.parents[node] != node:
    #         parent = self.parents[node]
    #         doubleParent = self.parents[parent]
    #         self.parents[node] = doubleParent
    #         node = doubleParent
    #     return node
    def _find(self, node):
      if self.parents[node] != node:
          self.parents[node] = self._find(self.parents[node])
      return self.parents[node]

    # unions two nodes, returns true/false inf successful
    def union(self, a, b):
        aRepParent = self._find(a)
        bRepParent = self._find(b)
        # if they are the same, they are already unioned
        if aRepParent == bRepParent:
            return False

        aDepth = self.depths[aRepParent]
        bDepth = self.depths[bRepParent]
        # bring a under b
        if aDepth < bDepth:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
        elif bDepth < aDepth:
            self.parents[bRepParent] = aRepParent
            del self.depths[bRepParent]
        else:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
            self.depths[bRepParent] += 1
        return True

    def areUnioned(self, a, b):
        return self._find(a) == self._find(b)

    # todo: test
    def uniqueComponents(self):
        return len(self.depths)