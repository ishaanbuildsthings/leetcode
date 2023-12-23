// https://leetcode.com/problems/partition-list/description/
// Difficulty: Medium
// Tags: Linked Lists

// Problem
/*
Given the head of a linked list and a value x, partition it such that all nodes less than x come before nodes greater than or equal to x.

You should preserve the original relative order of the nodes in each of the two partitions.
*/

// Solution, O(n) time and O(1) space
/*
Create two dummy heads. Iterate through, wiring in the appropriate nodes. Prevent a bad connection / cycle at the very end.
*/

var partition = function (head, x) {
  const lower = new ListNode(); // contains < x
  let lowerTail = lower;
  const higher = new ListNode(); // contains >= head
  let higherTail = higher;
  let pointer = head;
  while (pointer) {
    if (pointer.val < x) {
      lowerTail.next = pointer;
      lowerTail = lowerTail.next;
    } else {
      higherTail.next = pointer;
      higherTail = higherTail.next;
    }
    pointer = pointer.next;
  }
  lowerTail.next = higher.next;
  higherTail.next = null; // prevent bad connection
  return lower.next;
};
