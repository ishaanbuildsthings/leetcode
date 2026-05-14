// https://leetcode.com/problems/number-of-people-aware-of-a-secret/description/
// Difficulty: Medium

// Problem
/*
On day 1, one person discovers a secret.

You are given an integer delay, which means that each person will share the secret with a new person every day, starting from delay days after discovering the secret. You are also given an integer forget, which means that each person will forget the secret forget days after discovering it. A person cannot share the secret on the same day they forgot it, or on any day afterwards.

Given an integer n, return the number of people who know the secret at the end of day n. Since the answer may be very large, return it modulo 109 + 7.
*/

// Solution
/*
I did this problem ~1 week ago and don't remember my complexity / don't want to analyze it now. I think it might be n^2 and is pretty slow, but there were some optimizations to be made potentially. Either way it works, I just simulated the problem.
*/

const MOD = 10 ** 9 + 7;

var peopleAwareOfSecret = function (n, delay, forget) {
  const people = { 1: 1 }; // holds a mapping of [day they learned secret : number of those people]

  for (let day = 2; day <= n; day++) {
    for (const key in people) {
      // if people forgot the secret, they cannot share it, and no longer know it
      if (day - Number(key) >= forget) {
        delete people[key];
      }

      // if people still know the secret, they may share it with others on that day
      else {
        if (day - Number(key) - delay >= 0) {
          const peopleWhoKnewSecret = people[key] % MOD;
          if (!(day in people)) {
            people[day] = peopleWhoKnewSecret;
          } else {
            people[day] += peopleWhoKnewSecret;
          }
        }
      }
    }
  }

  let result = 0;
  for (const key in people) {
    result += people[key];
    result = result % MOD;
  }
  return result;
};
