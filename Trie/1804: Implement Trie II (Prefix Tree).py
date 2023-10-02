# https://leetcode.com/problems/implement-trie-ii-prefix-tree/
# difficulty: medium
# tags: trie

# # problem
# A trie (pronounced as "try") or prefix tree is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spellchecker.

# Implement the Trie class:

# Trie() Initializes the trie object.
# void insert(String word) Inserts the string word into the trie.
# int countWordsEqualTo(String word) Returns the number of instances of the string word in the trie.
# int countWordsStartingWith(String prefix) Returns the number of strings in the trie that have the string prefix as a prefix.
# void erase(String word) Erases the string word from the trie.

# Solution
# O(total letters inserted) space to hold the trie
# O(length of word) insert time, erase time, and count words equal to, O(n) count words starting with time. Can make that one O(length) too if we store prefixOf counters but I was lazy

class TrieNode:
    def __init__(self, val):
        self.val = val
        self.children = {} # maps a letter to trie node children
        self.isEnd = 0 # the number of times a word ends here

class Trie:

    def __init__(self):
        self.root = TrieNode(None)

    def insert(self, word: str) -> None:
        pointer = self.root
        for char in word:
            # if we have a child, move there
            if char in pointer.children:
                pointer = pointer.children[char]
            # otherwise, create and move there
            else:
                newChild = TrieNode(char)
                pointer.children[char] = newChild
                pointer = newChild
        pointer.isEnd += 1


    def countWordsEqualTo(self, word: str) -> int:
        pointer = self.root
        for char in word:
            # if we have a child, move there
            if char in pointer.children:
                pointer = pointer.children[char]
            # if we don't, return 0
            else:
                return 0
        # once we get to the end, get the word count
        return pointer.isEnd

    def countWordsStartingWith(self, prefix: str) -> int:
        # first navigate to that prefix, or return 0 if we can't even get there
        pointer = self.root
        for char in prefix:
            # if we have a child, move there
            if char in pointer.children:
                pointer = pointer.children[char]
            # if we don't, return 0
            else:
                return 0
        # now that we are there, we run an exhaustive dfs
        res = 0
        def dfs(node):
            nonlocal res
            res += node.isEnd
            for char in node.children:
                dfs(node.children[char])
        dfs(pointer)
        return res

    def erase(self, word: str) -> None:
        pointer = self.root
        for char in word:
            # if we have a child, move there
            if char in pointer.children:
                pointer = pointer.children[char]
            # if we don't, return
            else:
                return
        # once we get to the end, remove a word
        pointer.isEnd -= 1


# Your Trie object will be instantiated and called as such:
# obj = Trie()
# obj.insert(word)
# param_2 = obj.countWordsEqualTo(word)
# param_3 = obj.countWordsStartingWith(prefix)
# obj.erase(word)