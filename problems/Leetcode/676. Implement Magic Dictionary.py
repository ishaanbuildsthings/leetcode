class MagicDictionary:

    def __init__(self):
        self.c = Counter()
    def buildDict(self, dictionary: List[str]) -> None:
        for word in dictionary:
            for i in range(len(word)):
                self.c[word[:i] + '*' + word[i + 1:]] += 1
        self.seen = set(dictionary)

    def search(self, searchWord: str) -> bool:
        for i in range(len(searchWord)):
            searchTerm = searchWord[:i] + '*' + searchWord[i + 1:]
            if not searchWord in self.seen and self.c[searchTerm]:
                return True
            if self.c[searchTerm] > 1:
                return True
        return False
        


# Your MagicDictionary object will be instantiated and called as such:
# obj = MagicDictionary()
# obj.buildDict(dictionary)
# param_2 = obj.search(searchWord)