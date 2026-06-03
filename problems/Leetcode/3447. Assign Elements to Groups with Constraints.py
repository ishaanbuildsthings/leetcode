def gens(n):
    result = {i:[] for i in range(1,n+1)}
    for i in range(1,n+1):
        for j in range(i,n+1,i):
            result[j].append(i)
    return result


gensz = gens(10**5 + 1000)
# print(gens(10))

facToNums = defaultdict(list)
for num in gensz:
    facs = gensz[num]
    for fac in facs:
        facToNums[fac].append(num)

# print(facToNums)

class Solution:
    def assignElements(self, groups: List[int], elements: List[int]) -> List[int]:
        numToIdxs = defaultdict(list)
        for i, val in enumerate(groups):
            numToIdxs[val].append(i)
        # print(numToIdxs)
        
        big = max(groups)
        
        seen = set()
        solvedNums = set()
        
        res = [None] * len(groups)
        for i in range(len(elements)):
            ele = elements[i]
            if ele in seen:
                continue
            mults = facToNums[ele]
            for mult in mults:
                if mult > big:
                    break
                if mult in solvedNums:
                    continue
                idxs = numToIdxs[mult]
                for idx in idxs:
                    if res[idx] is not None:
                        continue
                    res[idx] = i
                solvedNums.add(mult)
            seen.add(ele)
        
        for i in range(len(res)):
            if res[i] is None:
                res[i] = -1
        return res