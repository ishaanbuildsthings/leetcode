class Solution:
    def maxProfit(self, workers: List[int], tasks: List[List[int]]) -> int:
        taskToProfit = defaultdict(list)
        for task, profit in tasks:
            taskToProfit[task].append(profit)
        for key in taskToProfit:
            taskToProfit[key].sort(reverse=True)
        c = Counter(workers)
        curr = 0
        biggestAdd = 0
        for key in c:
            gainHere = sum(taskToProfit[key][:c[key]])
            curr += gainHere
            if c[key] < len(taskToProfit[key]):
                biggestAdd = max(biggestAdd, taskToProfit[key][c[key]])
        for task, profit in tasks:
            if not c[task]:
                biggestAdd = max(biggestAdd, profit)
        return curr + biggestAdd