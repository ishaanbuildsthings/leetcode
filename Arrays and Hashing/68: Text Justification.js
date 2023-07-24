// https://leetcode.com/problems/text-justification/description/
// difficulty: Hard

// Problem
/*
Given an array of strings words and a width maxWidth, format the text such that each line has exactly maxWidth characters and is fully (left and right) justified.

You should pack your words in a greedy approach; that is, pack as many words as you can in each line. Pad extra spaces ' ' when necessary so that each line has exactly maxWidth characters.

Extra spaces between words should be distributed as evenly as possible. If the number of spaces on a line does not divide evenly between words, the empty slots on the left will be assigned more spaces than the slots on the right.

For the last line of text, it should be left-justified, and no extra space is inserted between words.

Note:

A word is defined as a character sequence consisting of non-space characters only.
Each word's length is guaranteed to be greater than 0 and not exceed maxWidth.
The input array words contains at least one word.
*/

// Solution, O(num words * max width) time, O(max width) space
/*
Greedily collect words, tracking spaces, until we cannot fit a word. Then, justify the line, and add it.

At any given point, our running words array contains at most maxWidth chars.

When we justifying, we stringBuild by adding up to maxWidth total spacing for a line.

Overall, we iterate through every word, and for every line (which I guess worst case is every word) we add up to maxWidth total spacing. So num words * maxWidth time, and maxWidth space.

The code could probably be a bit cleaner or more optimized, I just implemented what worked.
*/

var fullJustify = function (words, maxWidth) {
  const result = [];
  let runningChars = 0; // represents how many chars we have collected so far
  let runningWords = []; // we will determine the number of spacings using this
  for (let i = 0; i < words.length; i++) {
    let previousSpacings;
    if (runningWords.length <= 1) {
      previousSpacings = 0;
    } else {
      previousSpacings = runningWords.length - 1;
    }

    const previousMinSize = runningChars + previousSpacings;
    let sizeIfTakeWord;
    if (runningWords.length === 0) {
      sizeIfTakeWord = words[i].length;
    } else {
      sizeIfTakeWord = previousMinSize + words[i].length + 1; // if we had at least 1 prior word, taking this word also adds a space
    }
    if (sizeIfTakeWord <= maxWidth) {
      runningWords.push(words[i]);
      runningChars += words[i].length;
      continue;
    }
    /* here, taking the word would cause a size overflow */

    const totalSpaces = maxWidth - runningChars; // the actual number of space units
    const minSpacing = Math.floor(totalSpaces / previousSpacings);
    const totalSpacesMinOnly = previousSpacings * minSpacing;
    let extraSpaces = totalSpaces - totalSpacesMinOnly;

    if (runningWords.length === 1) {
      const linePadded = runningWords[0].padEnd(maxWidth, " ");
      result.push(linePadded);
    } else {
      const stringBuild = [];
      for (let j = 0; j < runningWords.length; j++) {
        stringBuild.push(runningWords[j]);
        if (extraSpaces > 0) {
          stringBuild.push(" ");
          extraSpaces--;
        }
        // add spacing between words
        if (j !== runningWords.length - 1) {
          for (let k = 0; k < minSpacing; k++) {
            stringBuild.push(" ");
          }
        }
      }
      const stringLine = stringBuild.join("");
      result.push(stringLine);
    }

    runningWords = [words[i]]; // reset the words and chars
    runningChars = words[i].length;
  }

  // add the very last set
  let lastLine = runningWords.join(" ");
  const lastLinePadded = lastLine.padEnd(maxWidth, " ");
  result.push(lastLinePadded);

  return result;
};
