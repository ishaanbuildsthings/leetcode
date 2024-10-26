// https://leetcode.com/problems/stickers-to-spell-word/description/
// Difficulty: Hard
// tags: dynamic programming 1d, top down recursion

// Problem
/*
We are given n different types of stickers. Each sticker has a lowercase English word on it.

You would like to spell out the given string target by cutting individual letters from your collection of stickers and rearranging them. You can use each sticker more than once if you want, and you have infinite quantities of each sticker.

Return the minimum number of stickers that you need to spell out target. If the task is impossible, return -1.

Note: In all test cases, all words were chosen randomly from the 1000 most common US English words, and target was chosen as a concatenation of two random words.

Input: stickers = ["with","example","science"], target = "thehat"
Output: 3
Explanation:
We can use 2 "with" stickers, and 1 "example" sticker.
After cutting and rearrange the letters of those stickers, we can form the target "thehat".
Also, this is the minimum number of stickers necessary to form the target string.
*/

// Solution, 16^t * n * k time, where k=length of a sticker, n = number of stickers, t = target length. In practice, 16^t is a loose upper bound, it is much less. t*t + n*k + 16^t space.
/*
We can memoize results of [letters we have : minimum number of stickers we need], where letters we have is a mapping of how many letters for the target we have (capped at the number we need). For instance if we took the sticker 'aaabc' and the target is 'abx', we have { a : 1, b : 1, x : 0 }.

The base case is if we have everything, we return 0.

Otherwise, we try picking any sticker, as long as it gives us relevant letters, and see the result. I did an optimization where I only picked stickers that give us the first missing letter, which is easier to code. I am not sure if I would have gotten TLE by picking any sticker that gives us any relevant letter. The greedy works because eventually we will need a sticker supplying that first missing letter.

Each state takes n*k time to solve, where n is the number of stickers and k is the number of unique letters in that sticker. There is an upper bound of 16^t total states, as we have up to 16 possible counts for any letter in target. But it is actually less than this, for instance if we have 16 letters, we can only have 2 states for each. If we have 1 letter, we can have 16 states. The serializations could be considered constant time bounded since there are finite letters, but also that is odd to say since we consider the number of unique letters in a sticker as a parameter, so we could include the serialization for each state too but that is still t time so nothing changes.

For space, we have a recursive callstack depth of at most t, assuming we gained 1 letter from each sticker. Each state also holds a serialization of size t. We also hold up to n mappings of k size each. We also hold up to 16^t mappings to a number.
*/

var minStickers = function (stickers, target) {
  // maps a serialized count of how many letters we have (only for letters we need), to a solution
  const memo = {};

  // maps each sticker to a set of unique letters it has, so we can easily lookup if a sticker will help give us a certain letter
  const stickerLetters = {};
  for (const sticker of stickers) {
    const uniqueLetters = new Set();
    for (const char of sticker) {
      uniqueLetters.add(char);
    }
    stickerLetters[sticker] = uniqueLetters;
  }

  // maintains how many of each letter we currently have, only for letter types we need
  const counts = {};
  for (const char of target) {
    counts[char] = 0;
  }

  // tracks how many of each letter we need
  const needed = {};
  for (const char of target) {
    if (char in needed) {
      needed[char]++;
    } else {
      needed[char] = 1;
    }
  }

  // contains a mapping of stickers to frequency mappings of their letters, only for letters we need
  const stickersToCounts = {};
  for (const sticker of stickers) {
    const letterCounts = {};
    for (const char of sticker) {
      // if we don't need that letter, don't consider it in the frequency mapping
      if (!(char in needed)) {
        continue;
      }
      if (char in letterCounts) {
        letterCounts[char]++;
      } else {
        letterCounts[char] = 1;
      }
    }
    stickersToCounts[sticker] = letterCounts;
  }

  // tells us how many stickers we need to spell out the target
  function dp(currentCount) {
    const serialized = JSON.stringify(currentCount);

    if (serialized in memo) {
      return memo[serialized];
    }

    // base case, we have enough of every letter
    let missingLetterBool = false;
    let missingChar;
    for (const char in currentCount) {
      if (needed[char] > currentCount[char]) {
        missingLetterBool = true;
        missingChar = char;
        break;
      }
    }
    if (!missingLetterBool) {
      return 0;
    }
    /* here, missingChar is set to the first letter we don't have enough of */

    let minStickersNeeded = Infinity;

    // for every sticker, we can use it if it gives us the missing letter, an optimization, as oposed to considering any sticker that gives us any letter we need, which works but is slower. the greedy solution works because eventually we will need a sticker that gives us the letter we are missing, so we might as well just consider all of those paths
    for (const sticker of stickers) {
      const uniqueLetters = stickerLetters[sticker];
      if (!uniqueLetters.has(missingChar)) {
        continue;
      }
      /* here, every sticker has at least the missing letter */
      const stickerCounts = stickersToCounts[sticker];

      const copy = JSON.parse(JSON.stringify(currentCount));

      // add all the letters we get from that sticker
      for (const char in stickerCounts) {
        const numberOfThatCharInSticker = stickerCounts[char];
        copy[char] += numberOfThatCharInSticker;
        // this helps us prune the states, so we either have enough of a letter and don't care about excess, or we have some count that is not enough
        if (copy[char] > needed[char]) {
          copy[char] = needed[char];
        }
      }

      const resultIfWeTakeThisSticker = 1 + dp(copy);
      minStickersNeeded = Math.min(
        minStickersNeeded,
        resultIfWeTakeThisSticker
      );
    }

    memo[serialized] = minStickersNeeded;
    return minStickersNeeded;
  }

  const minimumCount = dp(counts);
  if (minimumCount === Infinity) {
    return -1;
  }
  return minimumCount;
};
