class Solution:
    def kthSmallest(self, mat: list[list[int]], k: int) -> int:
        height = len(mat)
        width = len(mat[0])

        smallest = [0]
        for r in range(height - 1, -1, -1):
            vals = mat[r]
            nsmallest = []
            heap = [] # holds (val, colIndex, pointer)
            for c in range(width):
                heapq.heappush(heap, (vals[c] + smallest[0], c, 0))
            for i in range(k):
                if not heap:
                    break
                smallV, colIndex, pointer = heapq.heappop(heap)
                nsmallest.append(smallV)
                if pointer != len(smallest) - 1:
                    heapq.heappush(heap, (vals[colIndex] + smallest[pointer + 1], colIndex, pointer + 1))
            smallest = nsmallest

        return smallest[-1]