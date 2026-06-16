# https://leetcode.com/problems/number-of-recent-calls/description/
# difficulty: easy

# tags: queue, sliding window (sort of)

# Solution, O(1) time average for ping, O(n) space
# Could do 3000n time as well or maybe use a SortedList / seg tree

class RecentCounter:

    def __init__(self):
        self.window = collections.deque()

    def ping(self, t: int) -> int:
        self.window.append(t)
        while self.window and t - self.window[0] > 3000:
            self.window.popleft()
        return len(self.window)


# Your RecentCounter object will be instantiated and called as such:
# obj = RecentCounter()
# param_1 = obj.ping(t)