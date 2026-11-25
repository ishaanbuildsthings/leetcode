class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:

        heap = [] # holds (-frq, taskType)
        pending = deque() # holds (timeFreedAt, taskType)
        c = Counter(tasks)

        for taskType, frq in c.items():
            heapq.heappush(heap, (-frq, taskType))

        time = 0

        while heap or pending:
            while pending and pending[0][0] <= time:
                poppedTime, poppedTaskType = pending.popleft()
                heapq.heappush(heap, (-c[poppedTaskType], poppedTaskType))

            if not heap:
                time = pending[0][0] # idle until next task frees up
                continue

            negFrq, poppedTaskType = heapq.heappop(heap)
            c[poppedTaskType] -= 1
            if c[poppedTaskType] > 0:
                pending.append((time + n + 1, poppedTaskType))
            time += 1

        return time