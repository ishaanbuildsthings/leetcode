// https://leetcode.com/problems/word-search-ii/description/
// Difficulty: Hard
// tags: trie, backtracking

// Problem
/*
Simplified:
Input: board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]], words = ["oath","pea","eat","rain"]
Output: ["eat","oath"]

Detailed:
Given an m x n board of characters and a list of strings words, return all words on the board.

Each word must be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once in a word.
*/

// Solution, no complexities yet, but generally the efficient solution
/*
Create a trie with all the words in `words`. Then, run a root backtrack across all cells in the grid. We can recurse to a neighbor if we haven't yet visited that cell. Once we recurse, check if we have a valid prefix, if so, keep going. Add things to the result as we find words.

Some notes and optimizations:
1) Using an array to track the letters we are at is not good, because we don't delay our join until the end. Rather, we join every iteration, so direct string addition is better.

2) It is better to enter the bad node and terminate, than to peek ahead to see if it is valid, and if it is, call that node. Since if it is valid we end up doing string addition twice.

3) We can backtrack within the trie nodes as well to prevent O(n) searchPrefix lookups. We can do this by making our DFS function take in the trienode as well, and then instead of O(n) lookups in the trie, we just check if the current cell exists as a child of the node we received.

4) We can also prune from the tree as we find words, so we stop iterating out as not needed.
*/

class TrieNode {
  constructor(val) {
    this.val = val;
    this.children = {}; // maps letters to TrieNode children
    this.end = false;
  }
}

class Trie {
  constructor() {
    this.root = new TrieNode();
  }

  insert(word) {
    let pointer = this.root;
    for (const char of word) {
      // if we already have that child, descend
      if (char in pointer.children) {
        const childNode = pointer.children[char];
        pointer = childNode;
      }
      // if we don't have that child, make it
      else {
        const newChild = new TrieNode(char);
        pointer.children[char] = newChild;
        pointer = newChild;
      }
    }

    pointer.end = true; // mark the end of the word
  }

  searchPrefix(prefix) {
    let pointer = this.root;

    for (const char of prefix) {
      // if we have that child, descend
      if (char in pointer.children) {
        const childNode = pointer.children[char];
        pointer = childNode;
      }
      // if we don't have that child, the prefix is not found
      else {
        return false;
      }
    }

    return true;
  }

  isWord(word) {
    let pointer = this.root;

    for (const char of word) {
      // if we have that child, descend
      if (char in pointer.children) {
        const childNode = pointer.children[char];
        pointer = childNode;
      }
      // if we don't have that child, the word is not found
      else {
        return false;
      }
    }

    return pointer.end; // return if we ended at a word
  }
}

var findWords = function (board, words) {
  const trie = new Trie();

  for (const word of words) {
    trie.insert(word);
  }

  const width = board[0].length;
  const height = board.length;
  const visited = new Array(height)
    .fill()
    .map(() => new Array(width).fill(false));

  const result = new Set();

  // starts at a coordinate, and recurses out to valid neighbors, until no sufficient neighbors can be searched, whenever a word is found it is added to the result
  function backtrack(row, col, currentLetters) {
    // add the letter we just reached to the current letters
    const currentWord = currentLetters + board[row][col];

    // if we don't form a valid prefix, terminate
    if (!trie.searchPrefix(currentWord)) {
      return;
    }

    // add the cell we just reached to the visited grid
    visited[row][col] = true;

    // check if the current cell forms a valid word
    if (trie.isWord(currentWord)) {
      result.add(currentWord);
    }

    // recurse to the right
    if (col + 1 < width && !visited[row][col + 1]) {
      // if the right word would form a valid prefix we should search it
      backtrack(row, col + 1, currentWord);
    }

    // recurse to the left
    if (col - 1 >= 0 && !visited[row][col - 1]) {
      // if the right word would form a valid prefix we should search it
      backtrack(row, col - 1, currentWord);
    }

    // recurse up
    if (row - 1 >= 0 && !visited[row - 1][col]) {
      // if the right word would form a valid prefix we should search it
      backtrack(row - 1, col, currentWord);
    }

    // recurse down
    if (row + 1 < height && !visited[row + 1][col]) {
      backtrack(row + 1, col, currentWord);
    }

    // after we are done recursing off of some cell, remove the items
    visited[row][col] = false;
  }

  for (let row = 0; row < height; row++) {
    for (let col = 0; col < width; col++) {
      backtrack(row, col, "");
    }
  }

  return Array.from(result);
};
