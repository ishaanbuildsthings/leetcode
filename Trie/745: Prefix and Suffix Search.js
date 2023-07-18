// https://leetcode.com/problems/prefix-and-suffix-search/description/
// Difficulty: Hard
// Tags: Trie

// Problem
/*
Design a special dictionary that searches the words in it by a prefix and a suffix.

Implement the WordFilter class:

WordFilter(string[] words) Initializes the object with the words in the dictionary.
f(string pref, string suff) Returns the index of the word in the dictionary, which has the prefix pref and the suffix suff. If there is more than one valid index, return the largest of them. If there is no such word in the dictionary, return -1.
*/

// Solution (read below for alternates and details)
/*
There are multiple ways to solve this problem. The initial code I wrote worked, but there are better solutions I thought of after.

The way my solution worked is, build a trie as normal, but for each node in the trie, store a hashmap of suffixes to the largest index for a valid word. So if our words are 'ab', our trie is root->a->b->, and each node has a hashmap of { b : 0, ab : 0 } as these are the suffixes

This works, but can be simplified, the trie doesn't really have a point. We can just store a hashmap of prefixes, where each prefix contains a hashmap of suffixes mapped to the answers.

That solution would be:
There are n (10^4) words, each of length 7. Say each word has 7 unique prefixes at most (though in practice it is less since letters are limited). This means there are 7 * 10^4 prefixes in the hashmap. Each prefix has at most 7*10^4 unqiue suffixes, but in practice it is amortized, since they can't all have that.

Another solution is to make a trie that stores pairs [prefixLetter, suffixLetter]. So if we search for 'abc', we first go to trienode that has [a, c], then go to trienode that has [b, null].

A final solution (as per the editorial) is:
Consider the word 'apple'. For each suffix of the word, we could insert that suffix, followed by '#', followed by the word, all into the trie.

For example, we will insert '#apple', 'e#apple', 'le#apple', 'ple#apple', 'pple#apple', 'apple#apple' into the trie. Then for a query like prefix = "ap", suffix = "le", we can find it by querying our trie for le#ap.

I also had some weird solution where we have "evil" trienode children, and the code did work, but allocated too much memory on the later test cases.
*/

class Node {
  constructor(val) {
    this.val = val;
    this.children = {}; // maps letters to node children
    this.suffixes = {}; // at this node, maps valid suffixes to the highest index they have
  }
}

var WordFilter = function (words) {
  // words = ['ab'];
  this.root = new Node();

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    // we will need to add every suffix to each trie node, first find those suffixes so we don't recompute
    const suffixes = [];
    for (let suffixLeft = 0; suffixLeft < word.length; suffixLeft++) {
      const suffix = word.slice(suffixLeft);
      suffixes.push(suffix);
    }

    let pointer = this.root;
    // add all suffixes to the root, updating the value as well
    for (const suffix of suffixes) {
      // if we don't have that suffix in the root, initialize it
      if (!(suffix in pointer.suffixes)) {
        pointer.suffixes[suffix] = i;
      } else {
        pointer.suffixes[suffix] = Math.max(pointer.suffixes[suffix], i);
      }
    }

    for (const char of word) {
      // if the char is a child, just move there
      if (char in pointer.children) {
        pointer = pointer.children[char];
      }

      // if the child isn't there, create it and move there
      else {
        const newNode = new Node(char);
        pointer.children[char] = newNode;
        pointer = newNode;
      }

      // add all suffixes
      for (const suffix of suffixes) {
        // if we don't have that suffix in the root, initialize it
        if (!(suffix in pointer.suffixes)) {
          pointer.suffixes[suffix] = i;
        } else {
          pointer.suffixes[suffix] = Math.max(pointer.suffixes[suffix], i);
        }
      }
    }
  }
};

WordFilter.prototype.f = function (pref, suff) {
  let pointer = this.root;
  // move along the prefix, returning false if there is no child
  for (const char of pref) {
    if (!(char in pointer.children)) {
      return -1;
    }
    pointer = pointer.children[char];
  }

  // check the suffix value
  // console.log(`the value is: ${pointer.suffixes[suff]}`)
  return pointer.suffixes[suff] === undefined ? -1 : pointer.suffixes[suff];
};

// Extremely cursed solution with "evil" trie node suffix children, does not pass due to memory failure on later test cases, just leaving here since it was a fun idea

class Node {
  constructor(val) {
    this.val = val;
    this.prefixChildren = {}; // maps a letter to a child node, used for prefixes
    this.suffixChildren = {}; // maps a letter to a child node, used for suffixies
    this.highestIndex = -1; // indicates the largest index of a word that fits the parameters to get here, or -1 if no word fits those parameters
  }
}

/**
 * @param {string[]} words
 */
var WordFilter = function (words) {
  this.root = new Node();

  /*
    say we want to add the word 'dog' to our trie, what we do is:

    1) add dog normally to a trie
    2) add do->suffix g to the trie
    3) add d->suffix g to trie
    4) add d->suffix og to trie
    5) add suffix g to trie
    ...

    so what dfsAndAdd does, is it takes in the remaining word we need to add, the node we are at, and if we are at the point where we can only add suffix nodes, as well as the index from `words`, which is the data we store at each trie node

    */
  function dfsAndAdd(node, remainingWord, indexInWords, fullWord) {
    // base case, if we have no letters left to add, we see if our index is bigger
    let skipDfs = false;
    if (remainingWord === "") {
      skipDfs = true;
      const highestIndex = node.highestIndex;
      if (indexInWords > highestIndex) {
        node.highestIndex = indexInWords;
      }
      // return;
    }

    if (!skipDfs) {
      // if we are allowed to add to the prefix too, for instance 'dog', we can add a d node or move to it, then continue off of that node at 'og'
      const firstChar = remainingWord[0];
      // if we already have that node, just move there
      if (firstChar in node.prefixChildren) {
        const childNode = node.prefixChildren[firstChar];
        dfsAndAdd(childNode, remainingWord.slice(1), indexInWords, fullWord);
      }
      // otherwise create the node and move there
      else {
        const newNode = new Node(firstChar);
        node.prefixChildren[firstChar] = newNode;
        dfsAndAdd(newNode, remainingWord.slice(1), indexInWords, fullWord);
      }
    }

    // add to the suffix, which is always allowed, but onlySuffix becomes true
    // imagine we have 'cows', and we added c, now we want to add suffixes 'ows', 'ws', and 's'

    // add 'ows', 'ws', 's'
    for (let suffixLeft = 0; suffixLeft < fullWord.length; suffixLeft++) {
      let pointer = node;
      const suffixToAdd = fullWord.slice(suffixLeft);
      for (const char of suffixToAdd) {
        // if we have that letter in the suffix children, just move there
        if (char in pointer.suffixChildren) {
          pointer = pointer.suffixChildren[char];
        }

        // if we don't have that letter, create the node and move there
        else {
          const newNode = new Node(char);
          pointer.suffixChildren[char] = newNode;
          pointer = newNode;
        }
      }
      // once we reach the end of the suffix, update the value
      if (indexInWords > pointer.highestIndex) {
        pointer.highestIndex = indexInWords;
      }
    }
  }

  for (let i = 0; i < words.length; i++) {
    dfsAndAdd(this.root, words[i], i, words[i]);
  }

  console.log(JSON.stringify(this.root));
};

/**
 * @param {string} pref
 * @param {string} suff
 * @return {number}
 */
WordFilter.prototype.f = function (pref, suff) {
  let pointer = this.root;
  for (const char of pref) {
    // if that prefix doesn't exist, return -1
    if (!(char in pointer.prefixChildren)) {
      return -1;
    }
    pointer = pointer.prefixChildren[char];
  }

  for (const char of suff) {
    // if that suffix doesn't exist, return -1
    if (!(char in pointer.suffixChildren)) {
      return -1;
    }
    pointer = pointer.suffixChildren[char];
  }

  // return the index at the ending node
  return pointer.highestIndex;
};

/**
 * Your WordFilter object will be instantiated and called as such:
 * var obj = new WordFilter(words)
 * var param_1 = obj.f(pref,suff)
 */
