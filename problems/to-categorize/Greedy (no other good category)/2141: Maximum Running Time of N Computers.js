// https://leetcode.com/problems/maximum-running-time-of-n-computers/
// Difficulty: Hard
// Tags: greedy

// Problem
/*
You have n computers. You are given the integer n and a 0-indexed integer array batteries where the ith battery can run a computer for batteries[i] minutes. You are interested in running all n computers simultaneously using the given batteries.

Initially, you can insert at most one battery into each computer. After that and at any integer time moment, you can remove a battery from a computer and insert another battery any number of times. The inserted battery can be a totally new battery or a battery from another computer. You may assume that the removing and inserting processes take no time.

Note that the batteries cannot be recharged.

Return the maximum number of minutes you can run all the n computers simultaneously.
*/

// Solution, O(n log n) time, O(sort) space
/*
We can pick the largest n batteries. Then, for every remaining battery, we use that on the bottleneck battery. Since that battery is smaller, we can definitely divvy it up among the other batteries in time. We compute the extra runtime to bring all the bottleneck batteries to the next tier.

Honestly this is a pretty hard question, I felt like the solution handwaived some things and I needed to draw out a lot of stuff to show it works.
*/

var maxRunTime = function (n, batteries) {
  batteries.sort((a, b) => a - b);
  let extra = 0;
  for (let i = 0; i < batteries.length - n; i++) {
    extra += batteries[i];
  }

  // iterate over all the top batteries in use, seeing if we can increase everything to the next level
  for (let i = batteries.length - n; i < batteries.length - 1; i++) {
    const surplusForNext = batteries[i + 1] - batteries[i];
    const previousBatteriesToRaise = i - (batteries.length - n) + 1; // +1 for the current battery
    const totalExtraNeeded = surplusForNext * previousBatteriesToRaise;
    // if we don't have enough of that power, then we are limited by the amount we can increase all the previous batteries to
    if (totalExtraNeeded > extra) {
      const extraPowerPerPriorBattery = Math.floor(
        extra / previousBatteriesToRaise
      );
      return batteries[i] + extraPowerPerPriorBattery;
    }
    extra -= totalExtraNeeded;
  }

  return Math.floor(extra / n) + batteries[batteries.length - 1];
};
