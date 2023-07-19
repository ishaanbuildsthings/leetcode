// https://leetcode.com/problems/maximum-good-people-based-on-statements/description/
// Difficulty: Hard
// Tags: backtracking, bitmasking

// Problem
/*
There are two types of persons:

The good person: The person who always tells the truth.
The bad person: The person who might tell the truth and might lie.
You are given a 0-indexed 2D integer array statements of size n x n that represents the statements made by n people about each other. More specifically, statements[i][j] could be one of the following:

0 which represents a statement made by person i that person j is a bad person.
1 which represents a statement made by person i that person j is a good person.
2 represents that no statement is made by person i about person j.
Additionally, no person ever makes a statement about themselves. Formally, we have that statements[i][i] = 2 for all 0 <= i < n.

Return the maximum number of people who can be good based on the statements made by the n people.
*/

// Solution, O(n^2 * 2^n) time, O(n) space for the recursive callstack, each callstack stores a mask too, which we can technically consider n space, since we are using the bits, so maybe n^2 space. also n^2*2^n can be optimized to n*2^n if we don't use bitmask
/*
This was my first double beats 100%!

I am dumb and did not realize we don't need to memoize anything, since there is nothing we can memoize. Each state is unique. So I wrote it as a dp at first but realized we can't memoize anything, so it's basically backtracking. As a consequence, my solution became way more convoluted than it needs to be. Instead of using a bitmask, I could have just used an array of people to track who is currently deemed bad or good. Because I used a bitmask, I also do n bit shifts in an inner loop, hence bigger time complexity. Though in practice it is probably faster still.

Essentially just brute force backtrack. If we say a person is good, validate all statements they have made about prior people, and all prior good people's statements about this person. If we say a person is bad, validate all prior good people's statements about this person. We don't have to worry about a case where person 0 says a future person is bad, and person 1 says they are good, because when we get to that future person, we valid the prior people's statements.
*/
var maximumGood = function (statements) {
  // dp(i, mask) tells us the solution to the maximum amount of people that can be good out of the remaining [i:] people, given a prior mask of `mask`, where a 1 indicates a previous person is good, and a 0 indicates they are bad
  // I am dumb and tried dp at first but realized there is nothing to memoize, so this is just backtracking. all states depend entirely on prior states, and no states are repeated

  function dp(i, mask) {
    // base case, if there are no people left to consider, there are no people that can be good
    if (i === statements[0].length) {
      return 0;
    }

    let maxForThis = -Infinity;

    // if the current person is bad, we need to validate all prior states, made by good people, about this person, if a statement is wrong, we entered an invalid state so we return -Infinity, since we could have never reached this arragement

    let invalidLogicFound = false;
    // instead of calculating a bit to start shifting at, i just iterate through all 16 each time, since we are just looking for the presence of prior-assumed people who are good, the people we haven't considered yet are 0s by default
    for (let bitsShifted = 0; bitsShifted < 16; bitsShifted++) {
      const bit = (mask >> bitsShifted) & 1;
      // find all previous people we have assigned good, and validate their logic about the current person
      if (bit === 1) {
        const totalPeople = statements[0].length;
        const personNumber = totalPeople - bitsShifted - 1;
        // validate the statement the given previous person made about us
        const statement = statements[personNumber][i];

        // if a previous good person said we were good, but we are assuming we are bad, this is not possible
        if (statement === 1) {
          invalidLogicFound = true;
          break;
        }
      }
    }

    // if no invalid logic was found, i.e. all prior good peoples statements about this person line up, then one option is to assume this person is bad, and move forwards
    if (!invalidLogicFound) {
      maxForThis = dp(i + 1, mask); // mask stays the same, a 0
    }

    // if we assume the current person is good, we need to validate all statements they have made about people exist in the mask, and that all prior good people say this person is good
    let invalidLogicFoundIfGood = false;
    for (let personAbout = 0; personAbout <= i - 1; personAbout++) {
      const statement = statements[i][personAbout];
      const wasPersonGoodOrBad =
        1 & (mask >> (statements[0].length - 1 - personAbout));
      if (statement === 0 && wasPersonGoodOrBad === 1) {
        invalidLogicFoundIfGood = true;
        break;
      }
      if (statement === 1 && wasPersonGoodOrBad === 0) {
        invalidLogicFoundIfGood = true;
        break;
      }
    }

    // validate all prior good people say this person is good, if case is just some optimization
    if (!invalidLogicFoundIfGood) {
      for (let bitsShifted = 0; bitsShifted < 16; bitsShifted++) {
        const bit = (mask >> bitsShifted) & 1;
        // i that prior person was good, we need to check their statement about the current person
        if (bit === 1) {
          const totalPeople = statements[0].length;
          const personNumber = totalPeople - bitsShifted - 1;
          const statement = statements[personNumber][i];

          // if a prior good person says we are bad, but we assume good, there is invalid logic
          if (statement === 0) {
            invalidLogicFoundIfGood = true;
            break;
          }
        }
      }
    }

    // if we assume the new person is good, and all their statements about prior people line up, we can also consider this
    if (!invalidLogicFoundIfGood) {
      const newMask = mask | (1 << (statements[0].length - i - 1));
      maxForThis = Math.max(maxForThis, 1 + dp(i + 1, newMask));
    }

    return maxForThis;
  }

  return dp(0, 0);
};
