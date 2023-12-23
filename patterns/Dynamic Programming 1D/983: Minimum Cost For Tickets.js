// https://leetcode.com/problems/minimum-cost-for-tickets/description/
// Difficulty: Medium
// Tags: dynamic programming 1d

// Problem
/*
You have planned some train traveling one year in advance. The days of the year in which you will travel are given as an integer array days. Each day is an integer from 1 to 365.

Train tickets are sold in three different ways:

a 1-day pass is sold for costs[0] dollars,
a 7-day pass is sold for costs[1] dollars, and
a 30-day pass is sold for costs[2] dollars.
The passes allow that many days of consecutive travel.

For example, if we get a 7-day pass on day 2, then we can travel for 7 days: 2, 3, 4, 5, 6, 7, and 8.
Return the minimum number of dollars you need to travel every day in the given list of days.
*/

// Solution, O(n) time, O(n) space
/*
For each day, we can try three tickets, and we are left with some subproblem for the array [i:]. So we build a dp table. The recurrence relation requires test only 3 ticket types, and doing a fixed amount of iterations, so it is O(1) for each state.
*/

var mincostTickets = function (days, costs) {
  // memo[l] determines the minimum const for [l:] of the days array
  const memo = new Array(days.length).fill(-1);

  function dp(l) {
    if (l === days.length) {
      return 0;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    // we can either buy a 1, 7, or 30 day ticket
    let minCost = Infinity;

    // try a 1 day ticket
    const costWithOneDayTicket = dp(l + 1) + costs[0];

    // try a 7 day ticket
    let i = l;
    let initialDay = days[l];
    // iterate as long as the current day is within the 7 day ticket range
    while (days[i] < initialDay + 7) {
      i++;
    }
    /* here, i is the first day we don't have a ticket for */
    const costFromDp = dp(i);
    const costWith7DayTicket = costFromDp + costs[1];

    // try a 30 day ticket
    i = l;
    initialDay = days[l];
    while (days[i] < initialDay + 30) {
      i++;
    }
    const costWith30DayTicket = dp(i) + costs[2];

    minCost = Math.min(
      costWithOneDayTicket,
      costWith7DayTicket,
      costWith30DayTicket
    );

    memo[l] = minCost;

    return minCost;
  }

  return dp(0);
};
