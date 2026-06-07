class Logger:

    def __init__(self):
        self.latest = defaultdict(lambda: -inf)

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        if timestamp - self.latest[message] >= 10:
            self.latest[message] = timestamp
            return True
        return False


# Your Logger object will be instantiated and called as such:
# obj = Logger()
# param_1 = obj.shouldPrintMessage(timestamp,message)