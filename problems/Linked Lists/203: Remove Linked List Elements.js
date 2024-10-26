// https://leetcode.com/problems/remove-linked-list-elements/description/
// Difficulty: Easy

// Problem
/*
Given the head of a linked list and an integer val, remove all the nodes of the linked list that has Node.val == val, and return the new head.
*/

// Solution, O(n) time and O(1) space
/*
Create a dummy node that points to the beginning, which makes it easy to remove elements to beginning. Start iterating from the dummy. If our next node has the value we want to remove, iterate until we find a good node, then wire that in. Do this while we have valid nodes to iterate through (the inner while loop gets amortized).
*/

var removeElements = function (head, val) {
  const dummy = new ListNode();
  dummy.next = head;

  let tail = dummy;
  while (tail && tail.next) {
    if (tail.next.val === val) {
      let findGoodVal = tail.next;
      while (findGoodVal && findGoodVal.val === val) {
        findGoodVal = findGoodVal.next;
      }
      tail.next = findGoodVal;
    }
    tail = tail.next;
  }

  return dummy.next;
};
