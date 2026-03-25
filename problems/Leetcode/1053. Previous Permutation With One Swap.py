class Solution:
    def prevPermOpt1(self, arr: List[int]) -> List[int]:
        # a number on the left will drop
        # ideally we drop the rightmost one possible
        # so start from the right, evaluating left edges, can this number drop, i.e. a number on the right is smaller
        # we drop it with the biggest one
        poses = defaultdict(list) # number -> list of indices
        small = inf
        for i in range(len(arr) - 1, -1, -1):
            if small >= arr[i]:
                small = arr[i]
                poses[arr[i]].append(i)
                continue
            shouldExit = False
            # we found a smaller number on the right
            # we will swap it for the biggest one smaller than us
            for d in range(arr[i] - 1, 0, -1):
                if not poses[d]:
                    continue
                lastI = poses[d][-1]
                arr[i], arr[lastI] = arr[lastI], arr[i]
                shouldExit = True
                break
            if shouldExit:
                break
        return arr
            
            