class AuthenticationManager:

    def __init__(self, timeToLive: int):
        self.ttl = timeToLive
        self.expires = {} # maps a tokenId -> when it expires
        self.aliveTimes = deque() # holds a list of (expiryTime, tokenId), but multiple for a token can exist

    def generate(self, tokenId: str, currentTime: int) -> None:
        self.expires[tokenId] = self.ttl + currentTime
        self.aliveTimes.append((self.ttl + currentTime, tokenId))

    def renew(self, tokenId: str, currentTime: int) -> None:
        if tokenId not in self.expires:
            return
        if self.expires[tokenId] <= currentTime:
            return
        newTime = self.ttl + currentTime
        self.expires[tokenId] = newTime
        self.aliveTimes.append((newTime, tokenId))
        
    def countUnexpiredTokens(self, currentTime: int) -> int:
        while self.aliveTimes and self.aliveTimes[0][0] <= currentTime:
            lostTime, lostIdx = self.aliveTimes.popleft()
            if self.expires[lostIdx] == lostTime:
                del self.expires[lostIdx]
        return len(self.expires)
        


# Your AuthenticationManager object will be instantiated and called as such:
# obj = AuthenticationManager(timeToLive)
# obj.generate(tokenId,currentTime)
# obj.renew(tokenId,currentTime)
# param_3 = obj.countUnexpiredTokens(currentTime)