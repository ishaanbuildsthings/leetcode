class Task:
    def __init__(self, dueDate, tags, description):
        self.date = dueDate
        self.tags = tags
        self.description = description

class TodoList:

    def __init__(self):
        self.nextId = 1
        self.userToTasks = defaultdict(list) # maps userId -> [taskId1, taskId2, ...]
        self.tasks = {} # maps taskId -> Task

    def addTask(self, userId: int, taskDescription: str, dueDate: int, tags: List[str]) -> int:
        ntask = Task(dueDate, tags, taskDescription)
        self.tasks[self.nextId] = ntask
        self.userToTasks[userId].append(self.nextId)
        self.nextId += 1
        return self.nextId - 1

    def getAllTasks(self, userId):
        res = []
        for taskId in self.userToTasks[userId]:
            task = self.tasks[taskId]
            res.append((task.date, task.description))
        res.sort()
        return [desc for _, desc in res]

    def getTasksForTag(self, userId: int, tag: str) -> List[str]:
        res = []
        for taskId in self.userToTasks[userId]:
            task = self.tasks[taskId]
            if tag in task.tags:
                res.append((task.date, task.description))
        res.sort()
        return [desc for _, desc in res]
        

    def completeTask(self, userId: int, taskId: int) -> None:
        if taskId not in self.tasks:
            return
        if taskId not in self.userToTasks[userId]:
            return
        del self.tasks[taskId]
        bucket = self.userToTasks[userId]
        bucket.pop(bucket.index(taskId))
        


# Your TodoList object will be instantiated and called as such:
# obj = TodoList()
# param_1 = obj.addTask(userId,taskDescription,dueDate,tags)
# param_2 = obj.getAllTasks(userId)
# param_3 = obj.getTasksForTag(userId,tag)
# obj.completeTask(userId,taskId)