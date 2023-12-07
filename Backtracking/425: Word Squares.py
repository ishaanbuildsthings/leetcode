# https://leetcode.com/problems/word-squares/description/
# difficulty: hard
# tags: backtracking, trie, prefix

# Problem
# Given an array of unique strings words, return all the word squares you can build from words. The same word from words can be used multiple times. You can return the answer in any order.

# A sequence of strings forms a valid word square if the kth row and column read the same string, where 0 <= k < max(numRows, numColumns).

# For example, the word sequence ["ball","area","lead","lady"] forms a word square because each word reads the same both horizontally and vertically.

# Solution
# Instead of actually using a trie, I just stored all possible prefixes. I placed letter by letter, instead of word by word. You also don't need prefixToValidNext, you can just scan through all 26 letters each time.

ABC = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def wordSquares(self, words: List[str]) -> List[List[str]]:
      N = len(words[0])

      prefixToValidNext = defaultdict(set)
      for word in words:
        prefixToValidNext[''].add(word[0])
        for prefixLength in range(1, N + 1):
          left = word[:prefixLength]
          rightChar = word[prefixLength] if prefixLength < len(word) else ''
          prefixToValidNext[left].add(rightChar)

      res = []

      board = [[''] * N for _ in range(N)]

      def comparePrefixes(word1, word2):
        bottleneck = min(len(word1), len(word2))
        return word1[:bottleneck] == word2[:bottleneck]

      def recurse(row, col):
        # base case
        if row == N:
          newResult = []
          for horizontal in board:
            newResult.append(''.join(horizontal))
          res.append(newResult)
          return

        pf = ''.join(board[row])

        for char in prefixToValidNext[pf]:

          # construct vertical word
          verticalWord = ''
          for r in range(row):
            verticalWord += board[r][col]
          verticalWord += char

          # construct horizontal word
          horizontalWord = ''
          for c in range(N):
            if board[col][c] == '':
              break
            horizontalWord += board[col][c]
          if col == row:
            horizontalWord += char

          # construct row word
          rowWord = pf + char

          if not len(prefixToValidNext[verticalWord]) or not len(prefixToValidNext[horizontalWord]) or not len(prefixToValidNext[rowWord]) or not comparePrefixes(horizontalWord, verticalWord):
            continue

          board[row][col] = char

          if col == N - 1:
            newRow = row + 1
            newCol = 0
          else:
            newRow = row
            newCol = col + 1

          recurse(newRow, newCol)

          board[row][col] = ''

      recurse(0, 0)

      return res

        # w o r d
        # w o r d
        # w o o d
        # w o

        # for word in words:
        #   badFound = False
        #   for c in range(4):
        #     pass

        # A A A A
        # A A

