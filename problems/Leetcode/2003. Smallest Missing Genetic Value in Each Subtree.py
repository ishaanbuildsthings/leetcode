from sortedcontainers import SortedList

class Solution:
    def smallestMissingValueSubtree(self, parents: List[int], nums: List[int]) -> List[int]:
        
        # This is just a blackbox function that given a bbst, finds the smallest missing number in it in O(log^2 N) time, could get logN with O(1) find kth like a C++ pbds
        def getSmallestMissingValue(sortedList):
            left, right = 0, len(sortedList)
            while left < right:
                mid = (left + right) // 2
                if sortedList[mid] == mid + 1:
                    left = mid + 1
                else:
                    right = mid
            return left + 1
        
        # The answer we output, will contain the answer for every subtree
        res = [None] * len(nums)

        # Generating a nice tree interface from the bad `parents` input
        # children[node] is just a list of child nodes
        children = defaultdict(list)
        for node, parent in enumerate(parents):
            children[parent].append(node)
                
        def dfs(node):
            if not children[node]:
                sl = SortedList()
                sl.add(nums[node])
                res[node] = getSmallestMissingValue(sl)
                return sl
            childs = [dfs(child) for child in children[node]]
            childs.sort(key=lambda x: -len(x))
            heavy = childs[0]
            for i in range(1, len(childs)):
                light = childs[i]
                for v in light:
                    heavy.add(v)
            heavy.add(nums[node])
            res[node] = getSmallestMissingValue(heavy)
            return heavy
        
        dfs(0)

        return res