class Solution:
    def countTasks(self, tasks: List[int], shifts: List[int]) -> List[int]:

        n = len(tasks)
        res = [0] * len(shifts)

        taskI = 0
        extraDone = 0


        pf = []
        curr = 0
        for v in tasks:
            curr += v
            pf.append(curr)

        def query(l, r):
            return pf[r] - (pf[l - 1] if l else 0)

        for i in range(len(shifts)):
            # print('----------')
            shift = shifts[i]

            # what is the max amount of tasks I can complete


            task = tasks[taskI]

            remain = task - extraDone # how much we have left at this task


            LEFT = taskI
            RIGHT = len(tasks) - 1
            resI = None # rightmost I can COMPLETE

            while LEFT <= RIGHT:
                m = (LEFT+RIGHT)//2
                total = query(taskI, m)
                total -= task
                total += remain

                if total <= shift:
                    resI = m
                    LEFT = m + 1
                else:
                    RIGHT = m - 1

            # print(f'resI: {resI}')
            if resI is None:
                extraDone += shift
                unfinishedRight = len(tasks) - taskI
                res[i] = unfinishedRight
                # print(f'extra done: {extraDone}')
                continue

            spend = query(taskI, resI)
            spend -= task
            spend += remain
            excess = shift - spend
            # print(f'excess: {excess}')

            # we can complete from taskI...resI
            unfinished = len(tasks) - resI - 1
            # print(f'unfinished: {unfinished}')
            res[i] = unfinished
            taskI = resI + 1
            if taskI >= len(tasks):
                taskI = 0
                extraDone = 0
            else:
                extraDone = excess

            # print(f'new task i: {task}')
            
            # print(f'extraDone: {extraDone}')


        return res

            
            
            