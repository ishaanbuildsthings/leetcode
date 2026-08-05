class Solution:
    def remainingMethods(self, n: int, k: int, invocations: List[List[int]]) -> List[int]:
        invoke = defaultdict(list)
        for invoker, invoked in invocations:
            invoke[invoker].append(invoked)
        
        sus = {k}
        
        path = {k}
        def findSus(node):
            path.add(node)
            sus.add(node)
            for child in invoke[node]:
                if child in path:
                    continue
                findSus(child)
        findSus(k)
        
        # print(f'sus: {sus}')
        
        invokedBy = defaultdict(list)
        for invoker, invoked in invocations:
            invokedBy[invoked].append(invoker)
        
        # can remove all sus
        for item in sus:
            for invoker in invokedBy[item]:
                if invoker not in sus:
                    return list(range(n))
        
        res = []
        for node in range(n):
            if node in sus:
                continue
            res.append(node)
        return res
        