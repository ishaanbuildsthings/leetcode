class BusBooking:

    def __init__(self, n: int):
        self.booked = set()
        self.n = n
        self.time = 0 # sum of the times
        self.times = {} # maps seat to time it took to book it

    def isAisle(self, s):
        return s[0] == 'B' or s[0] == 'C'

    def partner(self, s):
        row = s[0]
        col = s[1:]
        if row == 'A':
            return 'B' + col
        if row == 'B':
            return 'A' + col
        if row == 'C':
            return 'D' + col
        return 'C' + col

    def toggle(self, seat: str) -> None:
        # print('----')
        # print(f'toggling seat: {seat}')
        isBooked = seat in self.booked
        seatIsWindow = not self.isAisle(seat)
        seatPartner = self.partner(seat)
        partnerIsBooked = seatPartner in self.booked
        # print(f'partner: {seatPartner}, {partnerIsBooked}, {isBooked=}, {seatIsWindow=}')
        timeGain = 1
        # we are now booking this
        if not isBooked:
            self.booked.add(seat)

            if seatIsWindow:
                if partnerIsBooked:
                    timeGain = 3

            self.times[seat] = timeGain
            self.time += timeGain
        # unbooking this
        else:
            oldTimeToBook = self.times[seat]
            self.time -= oldTimeToBook
            del self.times[seat]
            self.booked.remove(seat)

    
    def getTotalTime(self) -> int:
        return self.time
        

    def getMinTime(self) -> int:
        return len(self.booked)
        


# Your BusBooking object will be instantiated and called as such:
# obj = BusBooking(n)
# obj.toggle(seat)
# param_2 = obj.getTotalTime()
# param_3 = obj.getMinTime()