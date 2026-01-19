class AuctionSystem:

    def __init__(self):
        self.userIdItemIdToAmt = {} # maps (userId, itemId) -> current amt
        self.itemToBids = defaultdict(lambda: SortedList()) # maps itemId -> (bidAmt, userId)

    def addBid(self, userId: int, itemId: int, bidAmount: int) -> None:
        if not (userId, itemId) in self.userIdItemIdToAmt:
            self.userIdItemIdToAmt[(userId, itemId)] = bidAmount
            self.itemToBids[itemId].add((bidAmount, userId))
        else:
            self.updateBid(userId, itemId, bidAmount)

    def updateBid(self, userId: int, itemId: int, newAmount: int) -> None:
        old = self.userIdItemIdToAmt[(userId, itemId)]
        sl = self.itemToBids[itemId]
        sl.remove((old, userId))
        sl.add((newAmount, userId))
        self.userIdItemIdToAmt[(userId, itemId)] = newAmount

    def removeBid(self, userId: int, itemId: int) -> None:
        amt = self.userIdItemIdToAmt[(userId, itemId)]
        del self.userIdItemIdToAmt[(userId, itemId)]
        self.itemToBids[itemId].remove((amt, userId))

    def getHighestBidder(self, itemId: int) -> int:
        sl = self.itemToBids[itemId]
        if not sl:
            return -1
        return sl[-1][1]


# Your AuctionSystem object will be instantiated and called as such:
# obj = AuctionSystem()
# obj.addBid(userId,itemId,bidAmount)
# obj.updateBid(userId,itemId,newAmount)
# obj.removeBid(userId,itemId)
# param_4 = obj.getHighestBidder(itemId)