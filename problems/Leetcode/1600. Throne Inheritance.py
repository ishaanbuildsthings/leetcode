class ThroneInheritance:

    def __init__(self, kingName: str):
        self.k = kingName
        self.children = defaultdict(list)
        self.dead = set()
        self.currOrder = [kingName]
        

    def birth(self, parentName: str, childName: str) -> None:
        self.children[parentName].append(childName)

    def death(self, name: str) -> None:
        self.dead.add(name)
        

    def getInheritanceOrder(self) -> List[str]:
        res = []
        def dfs(node):
            if node not in self.dead:
                res.append(node)
            for child in self.children[node]:
                dfs(child)
        dfs(self.k)
        return res


# Your ThroneInheritance object will be instantiated and called as such:
# obj = ThroneInheritance(kingName)
# obj.birth(parentName,childName)
# obj.death(name)
# param_3 = obj.getInheritanceOrder()