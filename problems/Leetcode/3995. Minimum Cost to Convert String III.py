# 1297

class Solution:
    def minCost(self, source: str, target: str, rules: list[list[str]], costs: list[int]) -> int:
        # for every rule check if pattern matches source and replacement matches target


        def findMatchIndices(pattern, replacement):
            r = len(replacement)
            resR = set()

            for i in range(len(target) - len(replacement) + 1):
                if target[i:i+r] == replacement:
                    resR.add(i)

            # print(f'{resR=}')


            answer = []


            # find matching sources
            for i in range(len(source) - len(pattern) + 1):
                if i not in resR:
                    continue
                failFound = False
                for j in range(len(pattern)):
                    pj = pattern[j]
                    if pj == '*':
                        continue
                    if source[i + j] != pj:
                        failFound = True
                        break
                if failFound:
                    continue
                answer.append(i)

            return answer
                
                
        # for every starting index i know valid positions, sizes, and costs

        startingIdxs = [[] for _ in range(len(source))]

        # startingIdxs[i] tells us a list of (size, cost)

        for i in range(len(rules)):
            pattern, replacement = rules[i]
            cost = costs[i]
            cost += pattern.count('*')
            # print(f'{cost=}')
            answer = findMatchIndices(pattern, replacement)
            # print(f'{answer=}')
            for idx in answer:
                startingIdxs[idx].append((len(pattern), cost))

        # print(f'{startingIdxs=}')


        @cache
        def dp(i):
            if i == len(source):
                return 0
            res = inf
            for sz, cost in startingIdxs[i]:
                ni = i + sz
                ncost = cost + dp(ni)
                res = min(res, ncost)
            if source[i] == target[i]:
                ifSkip = dp(i + 1)
                res = min(res, ifSkip)
            return res

        answer = dp(0)
        dp.cache_clear()
        return answer if answer != inf else -1
                
            

            