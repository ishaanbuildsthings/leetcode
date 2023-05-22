// https://leetcode.com/problems/maximum-twin-sum-of-a-linked-list/description/
// Difficulty: Medium
// tags: linked list, slow and fast pointers

// Problem
/*
Simplified: We have an even lengthed linked list, say 5-4-3-1, we need to return the max twin sum. The twin sums are 5+1 and 4+3, so we return 7.
 */

// Solution, O(n) time and O(1) space. Reverse the second half of the linked list, iterate down, find the max, then un-reverse it.

var pairSum = function (head) {
  let slow = head;
  let fast = head;
  let saveTail;
  while (fast && fast.next) {
    if (fast.next.next === null) {
      saveTail = slow;
    }
    slow = slow.next;
    fast = fast.next.next;
  }
  // slow points to the middle, erring right

  let prev = null;
  while (slow) {
    const temp = slow.next;
    slow.next = prev;
    prev = slow;
    slow = temp;
  }
  // now prev points to the head of the reversed list
  let rightHead = prev;
  let leftHead = head;

  let maxTwinSum = 0;
  while (leftHead && rightHead) {
    const sum = leftHead.val + rightHead.val;
    maxTwinSum = Math.max(maxTwinSum, sum);
    leftHead = leftHead.next;
    rightHead = rightHead.next;
  }

  // undo the reversal
  rightHead = prev;
  prev = null;
  while (rightHead) {
    const temp = rightHead.next;
    rightHead.next = prev;
    prev = rightHead;
    rightHead = temp;
  }

  saveTail.next = prev;

  return maxTwinSum;
};
