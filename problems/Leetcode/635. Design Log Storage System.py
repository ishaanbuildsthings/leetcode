class LogSystem:

    def __init__(self):
        self.times = [] # holds (time, id)

    def put(self, id: int, timestamp: str) -> None:
        self.times.append((timestamp, id))

    def retrieve(self, start: str, end: str, granularity: str) -> List[int]:

        def makePf(string):
            pf = (string[:4] if granularity == 'Year' else
            string[:7] if granularity == 'Month' else 
            string[:10] if granularity == 'Day' else 
            string[:13] if granularity == 'Hour' else 
            string[:16] if granularity == 'Minute' else
            string)
            return pf

        startPf = makePf(start)
        endPf = makePf(end)
        res = []
        for timestamp, id in self.times:
            pf = makePf(timestamp)
            if pf >= startPf and pf <= endPf:
                res.append(id)
        
        return res



# Your LogSystem object will be instantiated and called as such:
# obj = LogSystem()
# obj.put(id,timestamp)
# param_2 = obj.retrieve(start,end,granularity)