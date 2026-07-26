class Solution:
    def minCost(self, m: int, n: int, penalty: List[List[int]]) -> int:
        height = m
        width = n

        minD = defaultdict(lambda : inf)
        

        heap = [(1, 0, 0, 1)] # stores (minCost, r, c, action parity)
        minD[0, 0, 1] = 1

        while heap:
            minCost, r, c, actionParity = heapq.heappop(heap)
            # print(f'{minCost=} {r=} {c=} {actionParity=}')
            if minCost != minD[r, c, actionParity]:
                continue

            for rd, cd, dir in [[1,0,'d'],[-1,0,'u'],[0,1,'r'],[0,-1,'l']]:
                nr = r + rd
                nc = c + cd
                if nr == height or nr < 0 or nc == width or nc < 0:
                    continue
                violates = False
                if actionParity == 1:
                    if dir in 'lu':
                        violates = True
                else:
                    if dir in 'rd':
                        violates = True

                cost = (nr + 1) * (nc + 1)
                # print(f'plain cost is: {cost}')
                if violates:
                    cost += penalty[r][c]
                    # print(f'after violating plain cost is now: {cost}')


                ncost = cost + minCost
                # print(f'after original min cost, ncost is finally: {ncost}')
                # print(f'if we move: {dir} new cost is: {ncost}, {violates=}')
                if minD[nr, nc, actionParity ^ 1] <= ncost:
                    continue
                heapq.heappush(heap, (ncost, nr, nc, actionParity ^ 1))
                minD[nr, nc, actionParity ^ 1] = ncost

            # we can also wait
            ncost = minCost + penalty[r][c]
            # print(f'if we wait new cost is: {ncost}')
            if minD[r, c, actionParity ^ 1] > ncost:
                minD[r, c, actionParity ^ 1] = ncost
                heapq.heappush(heap, (ncost, r, c, actionParity ^ 1))

                
                
            
                
                




        return min(minD[height - 1, width - 1, 0], minD[height - 1, width - 1, 1])
            
            
            