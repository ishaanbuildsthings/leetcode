class UF:
    def __init__(self, nodes):
        self.par = { node : node for node in nodes }
    
    def find(self, node):
        par = self.par[node]
        if par == node:
            return par
        newPar = self.par[par]
        self.par[node] = newPar
        return self.find(newPar)

    def union(self, a, b):
        aPar = self.find(a)
        bPar = self.find(b)
        if aPar == bPar:
            return False
        self.par[aPar] = bPar

    def isUnioned(self, a, b):
        return self.find(a) == self.find(b)
    

class Solution:
    def areSentencesSimilarTwo(self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2):
            return False

        allWords = list(set(sentence1 + sentence2 + [pair[0] for pair in similarPairs] + [pair[1] for pair in similarPairs]))
        uf = UF(allWords)

        for a, b in similarPairs:
            uf.union(a, b)

        return all(
            uf.isUnioned(sentence1[i], sentence2[i]) for i in range(len(sentence1))
        )
        
