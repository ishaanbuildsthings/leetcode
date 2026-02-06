class RideSharingSystem:

    def __init__(self):
        self.d = deque()
        self.r = deque()
        self.del2 = set()
        self.inQ = set()

    def addRider(self, riderId: int) -> None:
        self.r.append(riderId)
        self.inQ.add(riderId)

    def addDriver(self, driverId: int) -> None:
        self.d.append(driverId)

    def matchDriverWithRider(self) -> List[int]:
        if not self.d:
            return [-1, -1]
        while self.r:
            if self.r[0] in self.del2:
                self.del2.remove(self.r[0])
                self.inQ.discard(self.r[0])
                self.r.popleft()
                continue
            else:
                poppedR = self.r.popleft()
                self.inQ.discard(poppedR)
                poppedD = self.d.popleft()
                return [poppedD, poppedR]
        return [-1, -1]

    def cancelRider(self, riderId: int) -> None:
        if not riderId in self.inQ:
            return
        self.del2.add(riderId)


# Your RideSharingSystem object will be instantiated and called as such:
# obj = RideSharingSystem()
# obj.addRider(riderId)
# obj.addDriver(driverId)
# param_3 = obj.matchDriverWithRider()
# obj.cancelRider(riderId)