class Solution:
    def memLeak(self, memory1: int, memory2: int) -> List[int]:
        for time in range(1, 10**9):
            if memory1 >= memory2:
                memory1 -= time
                if memory1 < 0:
                    return [time, memory1 + time, memory2]
            else:
                memory2 -= time
                if memory2 < 0:
                    return [time, memory1, memory2 + time]