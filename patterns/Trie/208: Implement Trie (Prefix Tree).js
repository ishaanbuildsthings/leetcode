// https://leetcode.com/problems/implement-trie-prefix-tree/description/
// Difficulty: Medium

// Problem
/*
A trie (pronounced as "try") or prefix tree is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spellchecker.

Implement the Trie class:

Trie() Initializes the trie object.
void insert(String word) Inserts the string word into the trie.
boolean search(String word) Returns true if the string word is in the trie (i.e., was inserted before), and false otherwise.
boolean startsWith(String prefix) Returns true if there is a previously inserted string word that has the prefix prefix, and false otherwise.
*/

// Solution, O(1) creation of trie, O(n) insert, search, and startsWith. O(n) space where n is the total number of letters ever inserted. Standard trie implementation, each TrieNode has a mapping of letters to children nodes, and a boolean to indicate if it is the end of a word.

class TrieNode {
  constructor(val) {
    this.val = val;
    this.children = {}; // maps a letter to an existing child node, if that letter exists
    this.end = false; // indicates if this node marks the end of a word
  }
}

var Trie = function () {
  this.root = new TrieNode();
};

Trie.prototype.insert = function (word) {
  let pointer = this.root;
  for (const char of word) {
    // if we already have the child, move the pointer
    if (char in pointer.children) {
      const charNode = pointer.children[char];
      pointer = charNode;
    }
    // if we don't have the child, create it and move there
    else {
      const newChildNode = new TrieNode(char);
      pointer.children[char] = newChildNode;
      pointer = newChildNode;
    }
  }
  // make the end of the word be true
  pointer.end = true;
};

Trie.prototype.search = function (word) {
  let pointer = this.root;

  for (const char of word) {
    // if we have the child, move there
    if (char in pointer.children) {
      pointer = pointer.children[char];
    } else {
      return false;
    }
  }

  if (pointer.end === true) {
    return true;
  }

  return false;
};

Trie.prototype.startsWith = function (prefix) {
  let pointer = this.root;

  for (const char of prefix) {
    // if we have the child, move there
    if (char in pointer.children) {
      pointer = pointer.children[char];
    } else {
      return false;
    }
  }

  return true;
};

/**
 * Your Trie object will be instantiated and called as such:
 * var obj = new Trie()
 * obj.insert(word)
 * var param_2 = obj.search(word)
 * var param_3 = obj.startsWith(prefix)
 */
