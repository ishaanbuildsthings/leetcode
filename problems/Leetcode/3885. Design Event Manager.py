from sortedcontainers import SortedList
class EventManager:

    def __init__(self, events: list[list[int]]):
        self.sl = SortedList()
        # holds (-prio, id)
        for i, p in events:
            self.sl.add((-p,i))
        self.mp = {} # maps event id -> prio
        for i, p in events:
            self.mp[i] = p
        

    def updatePriority(self, eventId: int, newPriority: int) -> None:
        oldP = self.mp[eventId]
        self.mp[eventId] = newPriority
        self.sl.remove((-oldP,eventId))
        self.sl.add((-newPriority,eventId))

    def pollHighest(self) -> int:
        if not self.sl:
            return -1
        popped = self.sl.pop(0)
        p, i = popped
        p *= -1
        del self.mp[i]
        return i
        


# Your EventManager object will be instantiated and called as such:
# obj = EventManager(events)
# obj.updatePriority(eventId,newPriority)
# param_2 = obj.pollHighest()