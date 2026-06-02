class Solution:
    def findRestaurant(self, list1: List[str], list2: List[str]) -> List[str]:
        if len(list1) < len(list2):
            return self.findRestaurant(list2, list1)
        
        leftmost = {}
        for i, w in enumerate(list2):
            if not w in leftmost:
                leftmost[w] = i
        
        resSum = inf
        resWords = []

        for i, w in enumerate(list1):
            if w in leftmost:
                if i + leftmost[w] < resSum:
                    resSum = i + leftmost[w]
                    resWords = [w]
                elif i + leftmost[w] == resSum:
                    resWords.append(w)
        
        return resWords