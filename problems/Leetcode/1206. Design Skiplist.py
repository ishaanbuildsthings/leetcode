class Node:
    def __init__(self, val, maxLevel):
        self.fwd = [None] * (maxLevel + 1)
        self.val = val
    
class Skiplist:

    def __init__(self):
        self.maxLevel = 32
        self.head = Node(-1, self.maxLevel)
    
    def randomLevel(self):
        currLevel = 0
        while currLevel < self.maxLevel:
            if random.randint(1, 2) == 1:
                currLevel += 1
            else:
                break
        return currLevel
        

    def search(self, target: int) -> bool:
        # find the max level with a node
        for lvl in range(self.maxLevel, -1, -1):
            if self.head.fwd[lvl] is None:
                continue
            break
        currMaxLevel = lvl

        curr = self.head
        for level in range(currMaxLevel, -1, -1):
            while curr.fwd[level] is not None and curr.fwd[level].val < target:
                curr = curr.fwd[level]
        if curr.fwd[0] and curr.fwd[0].val == target:
            return True
        
        return False
            

    def add(self, num: int) -> None:
        lvl = self.randomLevel()
        updates = [None] * (self.maxLevel + 1)
        currNode = self.head
        for level in range(self.maxLevel, -1, -1):
            while currNode.fwd[level] is not None and currNode.fwd[level].val < num:
                currNode = currNode.fwd[level]
            updates[level] = currNode # last node before insertion
        newNode = Node(num, lvl)
        for level in range(lvl + 1):
            newNode.fwd[level] = updates[level].fwd[level]
            updates[level].fwd[level] = newNode


    def erase(self, num: int) -> bool:
        if not self.search(num):
            return False
        currNode = self.head
        updates = [None] * (self.maxLevel + 1)
        for level in range(self.maxLevel, -1, -1):
            while currNode.fwd[level] is not None and currNode.fwd[level].val < num:
                currNode = currNode.fwd[level]
            updates[level] = currNode
        # to support duplicates we need to ensure when we delete its the same node
        trueDeleted = updates[0].fwd[0] # guaranteed to be the right value due to us searching at the beginning, this is also guaranteed to be the first node of this value type since we proceed only when the future node is < our value
        # HOWEVER NOTE the first node on each level of the same value could be different:
        # (thanks claude)

# Because the target doesn't exist on every level. Say 45(A) only exists on levels 0 and 1, but 45(B) exists on levels 0, 1, and 2:

# Level 2:  HEAD → 30 → 45(B) → 70
# Level 1:  HEAD → 30 → 45(A) → 45(B) → 70
# Level 0:  HEAD → 30 → 45(A) → 45(B) → 70
# Target is 45(A). On levels 0 and 1, updates[level].fwd[level] is 45(A) — great, unlink it.

# But on level 2, 45(A) doesn't exist. The first node with value 45 on level 2 is 45(B). If you just check .val == 45, you'd unlink 45(B) on level 2 — corrupting the structure by removing a level from a node you weren't trying to delete.

# With is target, level 2 sees that updates[2].fwd[2] is 45(B), which is not the same object as 45(A), so it breaks. Exactly the right behavior — you only unlink on levels where your specific node actually lives.

        # so this means we get the true node we want from the bottom level and then check every level to ensure that its the same first node

        for level in range(self.maxLevel + 1):
            lastNode = updates[level]
            if lastNode and lastNode.fwd[level] is trueDeleted:
                lastNode.fwd[level] = lastNode.fwd[level].fwd[level]
        return True


# Your Skiplist object will be instantiated and called as such:
# obj = Skiplist()
# param_1 = obj.search(target)
# obj.add(num)
# param_3 = obj.erase(num)