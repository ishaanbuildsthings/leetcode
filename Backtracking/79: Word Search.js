// https://leetcode.com/problems/word-search/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Given an m x n grid of characters board and a string word, return true if word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.

Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
Output: true
*/

// Solution
/*
We just need to backtrack across all root cells. We terminate when we are at an invalid prefix. I used a trie like structure since I did word search II before this, but in reality we can just use an index counter and iterate over the word to know what letter we are looking for.
*/

class Node {
  constructor(val) {
    this.val = val;
    this.next = null;
  }
}

class LinkedList {
  constructor() {
    this.root = new Node();
  }

  insert(word) {
    let pointer = this.root;
    for (const char of word) {
      const newNode = new Node(char);
      pointer.next = newNode;
      pointer = newNode;
    }
  }

  searchPrefix(prefix) {
    let pointer = this.root;
    for (const char of prefix) {
      if (pointer.next && pointer.next.val === char) {
        pointer = pointer.next;
      } else {
        return false;
      }
    }
    return true;
  }

  searchWord(word) {
    let pointer = this.root;
    for (const char of word) {
      if (pointer.next && pointer.next.val === char) {
        pointer = pointer.next;
      } else {
        return false;
      }
    }
    return pointer.next === null; // if we reached the end of the search and `next` is null we also reached the end of the word
  }
}

var exist = function (board, word) {
  const linkedList = new LinkedList();
  linkedList.insert(word);

  const width = board[0].length;
  const height = board.length;
  const visited = new Array(height)
    .fill()
    .map(() => new Array(width).fill(false));

  function backtrack(row, col, currentWord) {
    const newWord = currentWord + board[row][col];

    // if our current cycle is bad, terminate
    if (!linkedList.searchPrefix(newWord)) {
      return false;
    }

    // if we got the word, return true
    if (linkedList.searchWord(newWord)) {
      return true;
    }

    visited[row][col] = true;

    // recurse right
    if (col + 1 < width && !visited[row][col + 1]) {
      if (backtrack(row, col + 1, newWord)) {
        return true;
      }
    }

    // recurse left
    if (col - 1 >= 0 && !visited[row][col - 1]) {
      if (backtrack(row, col - 1, newWord)) {
        return true;
      }
    }

    // recurse up
    if (row - 1 >= 0 && !visited[row - 1][col]) {
      if (backtrack(row - 1, col, newWord)) {
        return true;
      }
    }

    // recursd down
    if (row + 1 < height && !visited[row + 1][col]) {
      if (backtrack(row + 1, col, newWord)) {
        return true;
      }
    }

    visited[row][col] = false;

    return false;
  }

  for (let row = 0; row < height; row++) {
    for (let col = 0; col < width; col++) {
      if (backtrack(row, col, "")) {
        return true;
      }
    }
  }

  return false;
};
