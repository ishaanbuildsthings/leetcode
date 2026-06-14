class Trie:
    def __init__(self, NODES, K):
        NODES += 1 # include root
        # children[nodeIdx][charIdx] -> next id if it exists
        self.children = [
            defaultdict(dict) for _ in range(NODES)
        ]
        self.K = K
        self.passed = [0] * NODES
        self.nextId = 1
        self.goodDepths = SortedList() # whenever a depth becomes good we add that depth to this container, also holding 0-indexed in here
    
    def insert(self, w):
        curr = 0
        for i, c in enumerate(w):
            self.passed[curr] += 1
            c_id = ord(c) - ord('a')
            if self.passed[curr] == self.K:
                self.goodDepths.add(i)
            if c_id not in self.children[curr]:
                self.children[curr][c_id] = self.nextId
                self.nextId += 1
            curr = self.children[curr][c_id]
        self.passed[curr] += 1
        if self.passed[curr] == self.K:
            self.goodDepths.add(len(w))
    
    def remove(self, w):
        curr = 0
        for i, c in enumerate(w):
            self.passed[curr] -= 1
            if self.passed[curr] == self.K - 1:
                self.goodDepths.remove(i)
            c_id = ord(c) - ord('a')
            curr = self.children[curr][c_id]
        self.passed[curr] -= 1
        if self.passed[curr] == self.K - 1:
            self.goodDepths.remove(len(w))
    

class Solution:
    def longestCommonPrefix(self, words: List[str], k: int) -> List[int]:
        INSERTS = sum(len(w) for w in words)
        t = Trie(INSERTS, k)
        for w in words:
            t.insert(w)
        res = []
        for i, w in enumerate(words):
            t.remove(w)
            res.append(t.goodDepths[-1] if t.goodDepths else 0)
            t.insert(w)
        return res