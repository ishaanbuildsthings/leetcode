// https://leetcode.com/problems/online-stock-span/description/
// Difficulty: Medium
// tags: stack, monotonic stack

// Problem
/*
Design an algorithm that collects daily price quotes for some stock and returns the span of that stock's price for the current day.

The span of the stock's price in one day is the maximum number of consecutive days (starting from that day and going backward) for which the stock price was less than or equal to the price of that day.

For example, if the prices of the stock in the last four days is [7,2,1,2] and the price of the stock today is 2, then the span of today is 4 because starting from today, the price of the stock was less than or equal 2 for 4 consecutive days.
Also, if the prices of the stock in the last four days is [7,34,1,2] and the price of the stock today is 8, then the span of today is 3 because starting from today, the price of the stock was less than or equal 8 for 3 consecutive days.
Implement the StockSpanner class:

Input
["StockSpanner", "next", "next", "next", "next", "next", "next", "next"]
[[], [100], [80], [60], [70], [60], [75], [85]]
Output
[null, 1, 1, 1, 2, 1, 4, 6]

Explanation
StockSpanner stockSpanner = new StockSpanner();
stockSpanner.next(100); // return 1
stockSpanner.next(80);  // return 1
stockSpanner.next(60);  // return 1
stockSpanner.next(70);  // return 2
stockSpanner.next(60);  // return 1
stockSpanner.next(75);  // return 4, because the last 4 prices (including today's price of 75) were less than or equal to today's price.
stockSpanner.next(85);  // return 6
*/

// Solution, O(n) time and O(n) space
/*
Initialize a stack that stores tuples of [price, index], where index is the furthest left element the price can beat. Maintain a strictly decreasing (not monotonic) stack. Whenever we violate that rule, pop from the stack and update the index.
*/

var StockSpanner = function () {
  this.stack = []; // strictly decreasing, whenever we see a larger or equal price we keep popping, keeping the leftmost index we were greater than, so contains tuples [price, indexWeBeat]. we need to keep the index, consider prices: [50, 20, 30], when the 30 pops the 20, we have [50, 30], but if a 40 comes, it needs to know there was a 20 it could also beat. If we maintained an entire array of all the prices we had ever seen, we could just store indices, and lookup prices inside the loop, but on average storing the tuples should be better (since  just storing indicies and a full list of prices would be as much info as the tuples anyway, and extra info)
};

/**
 * @param {number} price
 * @return {number}
 */
StockSpanner.prototype.next = function (price) {
  if (this.stack.length === 0) {
    this.stack.push([price, 1]); // the first ever price beats one price (itself)
    return 1;
  }

  let counter = 1; // the new stock will always beat itself
  while (
    this.stack.length > 0 &&
    price >= this.stack[this.stack.length - 1][0]
  ) {
    const tupleOld = this.stack[this.stack.length - 1];
    const beatenOld = tupleOld[1]; // how many prices the previous stock beat, including itself
    counter += beatenOld; // the new stock will beat however many the previous one did
    this.stack.pop();
  }
  this.stack.push([price, counter]);
  return counter;
};

/**
 * Your StockSpanner object will be instantiated and called as such:
 * var obj = new StockSpanner()
 * var param_1 = obj.next(price)
 */
