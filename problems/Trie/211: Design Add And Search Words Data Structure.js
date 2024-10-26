// https://leetcode.com/problems/design-add-and-search-words-data-structure/description/
// Difficulty: Medium
// Tags: trie, dfs

// Problem
/*
Design a data structure that supports adding new words and finding if a string matches any previously added string.

Implement the WordDictionary class:

WordDictionary() Initializes the object.
void addWord(word) Adds word to the data structure, it can be matched later.
bool search(word) Returns true if there is any string in the data structure that matches word or false otherwise. word may contain dots '.' where dots can be matched with any letter.
*/

// Solution
/*
To add a word, we just add it to the trie. To search, we need a recursive function. We have some remaining letters to search, and a node we are at. If we are at a normal letter, we descend to that node (or return false if there is no child). If we are at a dot, if any of the children work, we return true.
*/

class TrieNode {
  constructor(val) {
    this.val = val;
    this.children = {}; // maps letters to corresponding child TrieNodes
    this.end = false; // indicates if this is the end of a word
  }
}

var WordDictionary = function () {
  this.root = new TrieNode();
};

WordDictionary.prototype.addWord = function (word) {
  let pointer = this.root;
  for (const char of word) {
    // if we have the child, descend
    if (char in pointer.children) {
      const childNode = pointer.children[char];
      pointer = childNode;
    }
    // otherwise create one and move there
    else {
      const newChildNode = new TrieNode(char);
      pointer.children[char] = newChildNode;
      pointer = newChildNode;
    }
  }

  // mark the end of the word
  pointer.end = true;
};

/**
 * @param {string} word
 * @return {boolean}
 */
WordDictionary.prototype.search = function (word) {
  // returns true if a word can be found for the substring [i:], starting at the passed in node
  function search(node, i) {
    // console.log(`search called on node: ${node.val} i: ${i}, full node: ${JSON.stringify(node)}`)
    // console.log(`node children: ${JSON.stringify(node.children)}`)
    // base case, we have no letters left to consider and our current node is the end of a word
    if (i === word.length) {
      return node.end;
    }

    // if the ith char is a letter, we recurse there, or return false if there isn't a node
    if (word[i] !== ".") {
      if (!(word[i] in node.children)) {
        return false;
      }

      return search(node.children[word[i]], i + 1);
    }

    // if the ith char is a '.', we should try any children, and if any are valid, we return true
    for (const letterKey in node.children) {
      if (search(node.children[letterKey], i + 1)) {
        return true;
      }
    }

    return false;
  }

  let pointer = this.root;
  return search(pointer, 0);
};
