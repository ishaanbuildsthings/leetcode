class MinStack:
    def __init__(self):
        self.stack = []

    def push(self, val):
        curMin = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, curMin))

    def pop(self):
        self.stack.pop()

    def top(self):
        return self.stack[-1][0]

    def getMin(self):
        return self.stack[-1][1]