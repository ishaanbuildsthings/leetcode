// https://leetcode.com/problems/multiply-strings/editorial/
// Difficulty: Medium

// Problem
/*
Given two non-negative integers num1 and num2 represented as strings, return the product of num1 and num2, also represented as a string.

Note: You must not use any built-in BigInteger library or convert the inputs to integer directly.
*/

// Solution
/*
My initial approach was to multiply all pairs of numbers, take:

43
56
__
first pair = 18, carry the 1, add the last digit 8, to the row result = '8'
second pair = 24 + 1 carried, carry the 2, add the last digit, 5, to the row result = '58'
carry the 2, '258'

our row result size grows by 1 regardless of what we multiply, because we always use the last digit, for instance:
10
10
__
when we do 0*0, we carry a 0 and add a 0 to our row result, since all future iterations for the given bottom number should be offset by a factor of 10

this is weird though, the easier way to get the number of trailing 0s is to just see the positions of both indicies

I do n*m pair calculations, where n is the length of num1, and m is the length of num2. Within every n*m loop, I do rowResult = lastDigit + rowResult, which is an O(n+m) calculation, as the rowResult is at most n+m digits (99*99 is at most 4 digits, for instance). This is because strings are immutable and I have to create a copy. I am also using (n+m) therefore. So I'm doing n*m*(n+m), or n^2*m + n*m^2 time. Within each n loop, I'm also adding the result to the row result, which is another n+m operation, so n^2*m, overall it simplfies to n^2*m + n*m^2 or nm(n + m) time.

I also had to build a string add function for the rows, since the rows themselves are too big. The string add is still (max(n, m)) time though.

Where is all this complexity coming from? Doing the m+n operations inside the n*m loop is not good. We do n+m operations because we are doing immutable string operations. If we used an array, we could simply mutate it and not copy over values each time, consider:

99
99
__

[_, _, _, _]

First do 9*9, get 81, put the 1 in the array (backwards, we will reverse the array at the end, but this is not needed you could do it forwards), carry the 8. we know exactly where to place the numbers because we could calculate the total postfix 0s. Instead of carrying the 8 to the next computation, we can also just insert it immediately

[1, 8, _, _]

second 9*9, one trailing 0, get another 81. Insert the 1, carry the 8

[1, 9, 8, _]

Etc. This is n*m time, because we don't need to deal with costly trailing 0s that won't affect our results anyway, unlike the string operations where we duplicate things.
*/

// the suboptimal solution
var multiply = function (num1, num2) {
  if (num1 === "0" || num2 === "0") return "0";
  let result = "";
  // iterate over bottom numbers first
  for (
    let bottomNumberIndex = num2.length - 1;
    bottomNumberIndex >= 0;
    bottomNumberIndex--
  ) {
    const bottomNumber = Number(num2[bottomNumberIndex]);

    // get prefix 0s
    const numPrefixZeroes = num2.length - (bottomNumberIndex + 1);
    let rowResult = "";
    for (let i = 0; i < numPrefixZeroes; i++) {
      rowResult += "0";
    }

    let carry = 0;
    // iterate over top numbers
    for (
      let topNumberIndex = num1.length - 1;
      topNumberIndex >= 0;
      topNumberIndex--
    ) {
      const topNumber = Number(num1[topNumberIndex]);
      const multipliedPrimitiveWithCarry = bottomNumber * topNumber + carry;
      const lastDigit = String(multipliedPrimitiveWithCarry % 10);
      rowResult = lastDigit + rowResult;
      carry = Math.floor(multipliedPrimitiveWithCarry / 10);
      if (topNumberIndex === 0) {
        rowResult = String(carry) + rowResult;
      }
    }
    result = AddBigNums(result, rowResult);
    result = result.replace(/^0+/, "");
  }
  return result;
};

function AddBigNums(num1, num2) {
  const longestLength = Math.max(num1.length, num2.length);
  const num1Padded = num1.padStart(longestLength, "0");
  const num2Padded = num2.padStart(longestLength, "0");
  let result = "";
  let carry = 0;
  for (let i = num1Padded.length - 1; i >= 0; i--) {
    const num1Digit = Number(num1Padded[i]);
    const num2Digit = Number(num2Padded[i]);
    const digitSum = num1Digit + num2Digit + carry;
    carry = Math.floor(digitSum / 10);
    const lastDigit = digitSum % 10;
    result = lastDigit + result;
  }
  return result;
}
