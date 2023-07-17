// https://leetcode.com/problems/alien-dictionary/description/
// Difficulty: Hard
// Tags: graphs, topological sort, disconected, directed

// Problem
/*
There is a new alien language that uses the English alphabet. However, the order among the letters is unknown to you.

You are given a list of strings words from the alien language's dictionary, where the strings in words are
sorted lexicographically
 by the rules of this new language.

Return a string of the unique letters in the new alien language sorted in lexicographically increasing order by the new language's rules. If there is no solution, return "". If there are multiple solutions, return any of them.
*/

// Solution
/*
If we have two words, say: 'ab', 'ac', we can derive information that b comes before c. Or 'z', 'x', we know z comes before x. So iterate through each word, finding the first time they differ in a letter, and update our adjacency list. There are some edge cases / quirks, so I diligently added all letters we see to the adj list. The graph can be disconnected, for instance 'ab', 'ac', 'x', 'y'.

Then, we do a dfs on every letter in the adj list. We recurse out to the "leaves" first. What I should have done is reversed the direction for the links. So if a comes before b, I should have had b point to a. That way when I recurse out from b, I know to add `a` to my result first. I already built the list backwards, so I decided to just reverse my end result.

DFS out until we cannot, then add a letter to our result. If we ever find a path collision, return null (as a flag to indicate to return '' at the top).

I also mark nodes as seen, to skip processing them. For instance if 'a' comes before 'c', and 'b' comes before c, I know c is seen. So when we solve for b, we don't need to traverse down 'c' again, all its dependencies have been resolved. And more importantly, it would obfuscate the result by adding multiple letters to it.
*/

var alienOrder = function (words) {
  const adjList = {}; // maps a letter to a set of letters that come after it

  // edge case, as normally we iterate through n-1 words comparing them to the next word. if we only have one word, just return a string that has all its letters, any order works since we gleam no information
  if (words.length === 1) {
    const wordSet = new Set();
    for (const char of words[0]) {
      wordSet.add(char);
    }
    return Array.from(wordSet).join("");
  }

  // for each word, compare it to the next word
  for (let wordNum = 0; wordNum < words.length - 1; wordNum++) {
    const word = words[wordNum];
    const nextWord = words[wordNum + 1];

    // edge case, normally we compare letter by letter, up to the shortest word. but if a word is the next word with extra letters, like 'abc', 'ab', we have an invalid list
    if (word.length > nextWord.length && word.startsWith(nextWord)) {
      return "";
    }

    // was running into lots of edge cases, so this just very cleanly makes sure all letters are added to the graph. for instance 'z', 'z' normally wouldn't be added
    for (const char of word) {
      if (!(char in adjList)) {
        adjList[char] = new Set();
      }
    }
    for (const char of nextWord) {
      if (!(char in adjList)) {
        adjList[char] = new Set();
      }
    }

    const shortestLength = Math.min(word.length, nextWord.length);

    // compare each character
    for (let charNum = 0; charNum < shortestLength; charNum++) {
      const char1 = word[charNum];
      const char2 = nextWord[charNum];

      // if the characters aren't equal, we gain knowledge about a letter that comes before another, used continue statement to prevent nesting
      if (char1 === char2) {
        continue;
      }

      if (char1 in adjList) {
        adjList[char1].add(char2);
      }

      break; // after we found a mismatch, we have no other letters we can gain knowledge on
    }
  }

  const seen = new Set(); // helps avoid reprocessing as our graph can be disconnected (for instance 'a', 'b',  'bc', 'bd'), so we need to check every letter to see if we can find a cycle
  const path = new Set(); // will help us detect if there is a cycle meaning there is no solution

  const sortedLetters = [];

  // this function returns null if a cycle is found, otherwise, it adds letters to sortedLetters, adding the terminal letters first
  function dfs(node) {
    seen.add(node);
    path.add(node);

    const neighbors = adjList[node];

    for (const neighbor of neighbors) {
      // if we found a cycle we have to bubble up null
      if (path.has(neighbor)) {
        return null;
      }

      if (seen.has(neighbor)) {
        continue;
      }

      // if the neighbor has a cycle return null, simultaneously call dfs on the neighbor to populate the sortedLetters
      if (dfs(neighbor) === null) {
        return null;
      }
    }

    path.delete(node);
    sortedLetters.push(node);
  }

  for (const letter in adjList) {
    // don't reprocess nodes that were solved from prior chains
    if (seen.has(letter)) {
      continue;
    }

    const resultForNode = dfs(letter);
    if (resultForNode === null) {
      return "";
    }
  }

  return sortedLetters.reverse().join("");
};
