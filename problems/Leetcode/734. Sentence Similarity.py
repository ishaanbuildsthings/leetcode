class Solution:
    def areSentencesSimilar(self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2):
            return False

        adjMap = defaultdict(set) # always maps the lower alphabetical one to the higher, save a bit of space
        for w1, w2 in similarPairs:
            adjMap[min(w1, w2)].add(max(w1, w2))
        
        return all(
            sentence1[i] == sentence2[i] or 
            max(sentence1[i], sentence2[i]) in adjMap[min(sentence1[i], sentence2[i])] for i in range(len(sentence1))
        )