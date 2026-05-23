# class Solution:
#     def maxProfit(self, n: int, present: List[int], future: List[int], hierarchy: List[List[int]], budget: int) -> int:
        
#         children = defaultdict(list)
#         for par, child in hierarchy:
#             children[par].append(child)
        
#         @cache
#         def dp(node, didParentBuy, mustBuyThis):
#             cost = present[node - 1] if not didParentBuy else present[node - 1] // 2
#             if mustBuyThis and cost > budget:
#                 return {}
#             gain = future[node - 1] - cost
#             if not children[node]:
#                 if mustBuyThis:
#                     out = {budget - cost : gain}
#                 else:
#                     out = {budget : 0}
#                 return out
            
#             out = {budget - cost : gain} if mustBuyThis else {budget : 0}

#             for child in children[node]:
#                 childBuy = dp(child, mustBuyThis, True)
#                 childNoBuy = dp(child, mustBuyThis, False)
#                 bestOptions = childBuy.copy()
#                 nout = {}
#                 for k, v in childNoBuy.items():
#                     if k not in bestOptions:
#                         bestOptions[k] = v
#                     else:
#                         bestOptions[k] = max(bestOptions[k], v)

#                 for budgetLeft, maxScore in bestOptions.items():
#                     spent = budget - budgetLeft
#                     for prevBudgetLeft, prevMaxScore in out.items():
#                         oldSpent = budget - prevBudgetLeft
#                         if spent + oldSpent > budget:
#                             continue
#                         newBudget = budget - (spent + oldSpent)
#                         newScore = maxScore + prevMaxScore
#                         if newBudget not in nout:
#                             nout[newBudget] = newScore
#                         else:
#                             nout[newBudget] = max(nout.get(newBudget, 0), newScore)
                
#                 out = nout
            
#             return out
        
#         ans1 = dp(1, False, False)
#         ans2 = dp(1, False, True)
#         return max(
#             max(ans1.values(),default=0),
#             max(ans2.values(),default=0)
#         )

                





fmax = lambda x, y: x if x > y else y

class Solution:
    def maxProfit(self, n: int, present: List[int], future: List[int], hierarchy: List[List[int]], budget: int) -> int:
        
        children = defaultdict(list)
        for p, c in hierarchy:
            children[p-1].append(c-1)
        
        # returns a max profit we can get for each exact budget, assuming if the parent did or did not buy
        @cache
        def dp(node, didParentBuy):
            costHere = present[node] if not didParentBuy else present[node] // 2
            profitHere = future[node] - costHere
            
            bestNoBuy = { 0 : 0 }

            # if we do not buy the current
            for child in children[node]:
                childBest = dp(child, False)
                bestBeforeChild = bestNoBuy.copy()
                bestAfterChild = bestNoBuy.copy() # we can at least use the child
                for key in childBest:
                    bestAfterChild[key] = fmax(bestAfterChild.get(key, -inf), childBest[key])

                for childExpense in childBest:
                    for previousExpense in bestBeforeChild:
                        newExpense = childExpense + previousExpense
                        if newExpense > budget:
                            continue
                        newScore = childBest[childExpense] + bestBeforeChild[previousExpense]
                        bestAfterChild[newExpense] = fmax(bestAfterChild.get(newExpense, -inf), newScore)
                bestNoBuy = bestAfterChild
            
            # if we buy the current
            bestIfBuy = {}
            if costHere <= budget:
                bestIfBuy[costHere] = profitHere

                for child in children[node]:
                    childBest = dp(child, True)
                    bestBeforeChild = bestIfBuy.copy()
                    bestAfterChild = bestIfBuy.copy() # we can at least use the child
                    for key in childBest:
                        totalExpense = key + costHere
                        if totalExpense > budget:
                            continue
                        bestAfterChild[totalExpense] = fmax(bestAfterChild.get(totalExpense, -inf), childBest.get(key, -inf) + profitHere)

                    for childExpense in childBest:
                        for previousExpense in bestBeforeChild:
                            newExpense = childExpense + previousExpense
                            if newExpense > budget:
                                continue
                            newScore = childBest[childExpense] + bestBeforeChild[previousExpense]
                            bestAfterChild[newExpense] = fmax(bestAfterChild.get(newExpense, -inf), newScore)
                    bestIfBuy = bestAfterChild
            
            result = {}
            for key in bestNoBuy:
                result[key] = fmax(bestNoBuy[key], bestIfBuy.get(key, -inf))
            for key in bestIfBuy:
                result[key] = fmax(bestIfBuy[key], bestNoBuy.get(key, -inf))
                
            return result
        
        dpRoot = dp(0, False)
        big = 0
        for v in dpRoot.values():
            big = fmax(big, v)
        return big


