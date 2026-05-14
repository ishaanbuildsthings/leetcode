// https://leetcode.com/problems/replace-words/description/
// difficulty: medium
// tags: trie

// Problem
/*
In English, we have a concept called root, which can be followed by some other word to form another longer word - let's call this word successor. For example, when the root "an" is followed by the successor word "other", we can form a new word "another".

Given a dictionary consisting of many roots and a sentence consisting of words separated by spaces, replace all the successors in the sentence with the root forming it. If a successor can be replaced by more than one root, replace it with the root that has the shortest length.

Return the sentence after the replacement.
*/

// Solution, O(# dictionary words * average length of words + sentence + #words in sentence*avg sentence word length) time, O(#dictionary words * average length of words + sentence) space
/*
First, create a trie for all the dictionary words, which takes # dictionary words * avg length of words time and space. Then we spend O(sentence) time splitting up the sentence. For each word in the sentence O(sentence) time we do a trie lookup O(word length) time to see the first word that prefix matches. We could just store all the dictionary words in a set though and do lookups. At the end spend O(sentence) space generating the result.
*/

class TrieNode {
  constructor(val) {
    this.val = val;
    this.endOfWord = false;
    this.children = {}; // maps a letter to the relevant trienode
  }
}

class Trie {
  constructor() {
    this.root = new TrieNode();
  }

  insert(word) {
    let pointer = this.root;
    for (const char of word) {
      if (char in pointer.children) {
        pointer = pointer.children[char];
      } else {
        pointer.children[char] = new TrieNode(char);
        pointer = pointer.children[char];
      }
    }
    pointer.endOfWord = true;
  }

  searchShortestPrefix(word) {
    let pointer = this.root;
    const accumulatedLetters = [];
    for (const char of word) {
      // if the char wasn't found, there is no prefix word
      if (!(char in pointer.children)) {
        return false;
      }
      pointer = pointer.children[char];
      accumulatedLetters.push(char);
      if (pointer.endOfWord) {
        return accumulatedLetters.join("");
      }
    }

    return false;
  }
}

var replaceWords = function (dictionary, sentence) {
  const words = sentence.split(" ");

  const resultArr = [];

  const trie = new Trie();
  for (const word of dictionary) {
    trie.insert(word);
  }

  for (const word of words) {
    const shortestPrefix = trie.searchShortestPrefix(word);
    if (shortestPrefix === false) {
      resultArr.push(word);
    } else {
      resultArr.push(shortestPrefix);
    }
  }

  return resultArr.join(" ");
};
