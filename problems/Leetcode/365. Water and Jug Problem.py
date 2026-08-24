class Solution:
    def canMeasureWater(self, x: int, y: int, target: int) -> bool:
        seen = {(0, 0)}
        q = collections.deque()
        q.append((0, 0))
        while q:
            length = len(q)
            for _ in range(length):
                jug1, jug2 = q.popleft()

                # fill or empty one of them fully
                for jug in range(2):
                    for fill in range(2): # fill is 0, empty is 1
                        newTup = (
                            x if jug == 0 and fill == 0 else 0 if jug == 0 and fill == 1 else jug1,
                            y if jug == 1 and fill == 0 else 0 if jug == 1 and fill == 1 else jug2
                        )
                        if newTup[0] + newTup[1] == target:
                            return True
                        if newTup not in seen:
                            seen.add(newTup)
                            q.append(newTup)
                
                # transfer left to right
                empty = y - jug2
                newJug1 = jug1 - min(empty, jug1)
                newJug2 = jug2 + (jug1 - newJug1)
                newTup = (newJug1, newJug2)
                if newTup[0] + newTup[1] == target:
                    return True
                if newTup not in seen:
                    seen.add(newTup)
                    q.append(newTup)
                
                # transfer right to left
                empty = x - jug1
                newJug2 = jug2 - min(empty, jug2)
                newJug1 = jug1 + (jug2 - newJug2)
                newTup = (newJug1, newJug2)
                if newTup[0] + newTup[1] == target:
                    return True
                if newTup not in seen:
                    seen.add(newTup)
                    q.append(newTup)
        
        return False
                
            
