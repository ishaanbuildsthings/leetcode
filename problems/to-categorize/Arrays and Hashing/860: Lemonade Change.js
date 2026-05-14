// https://leetcode.com/problems/lemonade-change/description/
// Difficulty: Easy

// Problem
/*
At a lemonade stand, each lemonade costs $5. Customers are standing in a queue to buy from you and order one at a time (in the order specified by bills). Each customer will only buy one lemonade and pay with either a $5, $10, or $20 bill. You must provide the correct change to each customer so that the net transaction is that the customer pays $5.

Note that you do not have any change in hand at first.

Given an integer array bills where bills[i] is the bill the ith customer pays, return true if you can provide every customer with the correct change, or false otherwise.
*/

// Solution, O(n) time, O(1) space
/*
Keep storage for our bills. A 5 always pays for itself, add a 5 to our storage. A 10 needs a 5 in change, add a 10 to storage. A 20 needs either a 10+5, or a 5+5+5, greedily take the 10+5 first if possible, since only a 10 can be used as change for a 20.
*/
var lemonadeChange = function (bills) {
  // maps how many bills we have, 20 not needed since that can never be given as change
  const storage = {
    5: 0,
    10: 0,
  };

  for (let i = 0; i < bills.length; i++) {
    // a 5 always pays properly
    if (bills[i] === 5) {
      storage[5]++;
    }

    // a 10 needs 5 in change
    else if (bills[i] === 10) {
      if (storage[5] === 0) {
        return false;
      } else {
        storage[5]--;
        storage[10]++;
      }
    }

    // a 20 can take 10+5, or 5+5+5, always try to get rid of the 10 first greedily, since it can only be used as change for people who pay with a 20
    else if (bills[i] === 20) {
      if (storage[10] >= 1 && storage[5] >= 1) {
        storage[10]--;
        storage[5]--;
      } else if (storage[5] >= 3) {
        storage[5] -= 3;
      } else {
        return false;
      }
    }
  }

  return true;
};
