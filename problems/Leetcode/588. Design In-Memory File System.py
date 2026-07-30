class TrieNode:
    def __init__(self):
        self.children = {} # maps value to child trie node
        self.content = '' # if not empty this is a file

class FileSystem:

    def __init__(self):
        self.rt = TrieNode()

    def ls(self, path: str) -> List[str]:
        dir = self.mkdir(path)
        if dir.content:
            return [path.split('/')[-1]]
        return sorted(dir.children)
        

    def mkdir(self, path: str) -> None:
        items = [x for x in path.split('/') if x]
        curr = self.rt
        for item in items:
            if item not in curr.children:
                curr.children[item] = TrieNode()
            curr = curr.children[item]
        return curr
        

    def addContentToFile(self, filePath: str, content: str) -> None:
        dir = self.mkdir(filePath)
        dir.content += content
        
    def readContentFromFile(self, filePath: str) -> str:
        dir = self.mkdir(filePath)
        return dir.content
        


# Your FileSystem object will be instantiated and called as such:
# obj = FileSystem()
# param_1 = obj.ls(path)
# obj.mkdir(path)
# obj.addContentToFile(filePath,content)
# param_4 = obj.readContentFromFile(filePath)