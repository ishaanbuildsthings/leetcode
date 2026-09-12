// https://leetcode.com/problems/apply-discount-to-prices/
// Difficulty: Medium

// Problem
/*
A sentence is a string of single-space separated words where each word can contain digits, lowercase letters, and the dollar sign '$'. A word represents a price if it is a sequence of digits preceded by a dollar sign.

For example, "$100", "$23", and "$6" represent prices while "100", "$", and "$1e5" do not.
You are given a string sentence representing a sentence and an integer discount. For each word representing a price, apply a discount of discount% on the price and update the word in the sentence. All updated prices should be represented with exactly two decimal places.

Return a string representing the modified sentence.

Note that all prices will contain at most 10 digits.
*/

// Solution, O(chars) time, O(1) space (since a price is at most 10 chars)
/*
Just process each price as needed. Probably some more efficient operations that use pointers instead of lots of substring ops.
*/

var discountPrices = function (sentence, discount) {
  function isPrice(substring) {
    // edge case
    if (substring === "$") {
      return false;
    }

    if (substring[0] !== "$") {
      return false;
    }
    for (let i = 1; i < substring.length; i++) {
      if (isNaN(Number(substring[i]))) {
        return false;
      }
    }
    return true;
  }

  function getDiscountedPrice(price) {
    const priceNum = Number(price.slice(1));
    const discountedPrice = (priceNum * ((100 - discount) / 100)).toFixed(2);
    const priceStr = "$" + String(discountedPrice);
    return priceStr;
  }

  const words = sentence.split(" ");

  const resultArr = [];

  for (const word of words) {
    if (!isPrice(word)) {
      resultArr.push(word);
    } else {
      resultArr.push(getDiscountedPrice(word));
    }
  }

  return resultArr.join(" ");
};
