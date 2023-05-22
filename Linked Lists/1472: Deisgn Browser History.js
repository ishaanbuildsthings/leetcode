// https://leetcode.com/problems/design-browser-history/description/
// Difficulty: Medium

// Problem
/*
Simplified: Deisgn browser history, visiting a url adds an element, we can go back steps, and forward, but every time we visit an element our forward history is cleared
*/

// Solution
// Time: O(1) to make the browser history, O(1) to visit, O(n) to go back or forwards n steps. Space: O(n) to store the browser history.
/*
One thing to notice is if we visit three urls, LC-G-FB, then we go back, we can't lose that we went to FB, so we can't really use a stack. We could use a stack with a pointer and do some clever techniques, but we would still end up storing too much unncessary information. A better solution is to use a doubly linked list, since we can clear out any portion to the right in O(1) time. We don't need a left dummy or right dummy, we just need a pointer to indicate where we are, and move around as urls are visited. We reset the next pointer whenever we visit a site.
*/

class Node {
  constructor(val) {
    this.val = val; // url
    this.next = null;
    this.prev = null;
  }
}

var BrowserHistory = function (homepage) {
  this.pointer = new Node(homepage);
};

BrowserHistory.prototype.visit = function (url) {
  this.pointer.next = new Node(url);
  this.pointer.next.prev = this.pointer;
  this.pointer = this.pointer.next;
};

BrowserHistory.prototype.back = function (steps) {
  let stepsTaken = 0;
  while (this.pointer.prev && stepsTaken < steps) {
    this.pointer = this.pointer.prev;
    stepsTaken++;
  }
  return this.pointer.val;
};

BrowserHistory.prototype.forward = function (steps) {
  let stepsTaken = 0;
  while (this.pointer.next && stepsTaken < steps) {
    this.pointer = this.pointer.next;
    stepsTaken++;
  }
  return this.pointer.val;
};
