// https://leetcode.com/problems/ipo/description/
// Difficulty: Hard
// tags: greedy, heap

// ________ MAX HEAP ABOVE ON LEETCODE ________

// Problem
/*
Detailed:
Suppose LeetCode will start its IPO soon. In order to sell a good price of its shares to Venture Capital, LeetCode would like to work on some projects to increase its capital before the IPO. Since it has limited resources, it can only finish at most k distinct projects before the IPO. Help LeetCode design the best way to maximize its total capital after finishing at most k distinct projects.

You are given n projects where the ith project has a pure profit profits[i] and a minimum capital of capital[i] is needed to start it.

Initially, you have w capital. When you finish a project, you will obtain its pure profit and the profit will be added to your total capital.

Pick a list of at most k distinct projects from given projects to maximize your final capital, and return the final maximized capital.

The answer is guaranteed to fit in a 32-bit signed integer.

var findMaximizedCapital = function (k, w, profits, capital) {
  /*
    we will maintain a max heap of true profits for only projects we can afford. when we take on a project, the amount of money we have grows, and we can afford new projects, so we add those projects to the heap (we add the value of the true profit they give)
    */

  const zipped = capital.map((startingCapitalNeeded, i) => [
    startingCapitalNeeded,
    profits[i],
  ]);

  // sort by starting capital needed, as we will only add projects to the heap once we can afford to take them on
  zipped.sort((a, b) => a[0] - b[0]);

  const maxHeap = new MaxHeap();

  let currentCapital = w;

  // populate the heap with the initial true profits for what we can afford, could be faster with a true heapify
  let p = 0; // tracks the first project we cannot afford
  // iterates as long as we can afford a project, or stops if we can afford every project
  while (p < profits.length && zipped[p][0] <= currentCapital) {
    const tuple = zipped[p];
    const [startingCapitalNeeded, profit] = tuple;
    maxHeap.insert(profit);
    p++;
  }

  // take on k projects
  for (let i = 0; i < k; i++) {
    // if we run out of projects we can afford, we just return how much we made
    if (maxHeap.size() === 0) {
      return currentCapital;
    }
    // console.log(`taking on the ${i + 1}th project`)
    const mostProfitableProject = maxHeap.remove();
    currentCapital += mostProfitableProject;
    // add new projects we can afford, or if we can afford every project, then stop
    while (p < profits.length && zipped[p][0] <= currentCapital) {
      const tuple = zipped[p];
      const [startingCapitalNeeded, profit] = tuple;
      maxHeap.insert(profit);
      p++;
    }
  }

  return currentCapital;
};
