class FileSharing:

    def __init__(self, m: int):
        self.avail = [] # min heap
        self.nextId = 1
        self.userToChunks = defaultdict(set)
        self.chunkToUsers = defaultdict(set)

    def join(self, ownedChunks: List[int]) -> int:
        if self.avail:
            mn = heapq.heappop(self.avail)
        else:
            mn = self.nextId
            self.nextId += 1
        self.userToChunks[mn] = set(ownedChunks)
        for chunk in ownedChunks:
            self.chunkToUsers[chunk].add(mn)
        return mn

    def leave(self, userID: int) -> None:
        heapq.heappush(self.avail, userID)
        for chunk in self.userToChunks[userID]:
            self.chunkToUsers[chunk].discard(userID)
        self.userToChunks[userID] = set()
        

    def request(self, userID: int, chunkID: int) -> List[int]:
        ans = sorted(self.chunkToUsers[chunkID])
        if ans:
            self.userToChunks[userID].add(chunkID)
            self.chunkToUsers[chunkID].add(userID)
        return ans
        


# Your FileSharing object will be instantiated and called as such:
# obj = FileSharing(m)
# param_1 = obj.join(ownedChunks)
# obj.leave(userID)
# param_3 = obj.request(userID,chunkID)