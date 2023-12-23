// https://leetcode.com/problems/swap-nodes-in-pairs/description/
// Difficulty: Medium
// tags: Linked List

// Problem
/*
Given a linked list, swap every two adjacent nodes and return its head. You must solve the problem without modifying the values in the list's nodes (i.e., only nodes themselves may be changed.)
*/

// Solution, O(n) time and O(1) space, iterative
/*
While we still have two elements, reverse them, then make the new group head (which I called `tail`) the third element.

Similar to 25: Reverse Nodes in k-group. But there, I validated we had enlugh elements by counting it each time, this is still n time though, since each element gets counted at most once.
*/

var swapPairs = function (head) {
  const dummy = new ListNode();
  dummy.next = head;

  let prev = dummy;
  let curr = head;

  // while we have at least two elements, we can reverse them, this is easiest if you draw it out
  while (curr && curr.next) {
    const twoAhead = curr.next.next;
    curr.next.next = curr;
    prev.next = curr.next;
    curr.next = twoAhead;
    prev = curr;
    curr = twoAhead;
  }
  /*
    P-> 1->2->3->4->

    P-> 1-> <-2 3->4->
    P->2->1->3->4->
             ^

    2->1->3->4
    ^t    ^two

    2->1->3->4->
          ^tail


    */

  return dummy.next;
};
