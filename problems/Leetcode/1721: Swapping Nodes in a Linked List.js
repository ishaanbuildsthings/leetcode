// https://leetcode.com/problems/swapping-nodes-in-a-linked-list/description/
// Difficulty: Medium
// Tags: Linked List, slow and fast pointers

// Problem
/*
Simplfied: Swap the values of the kth and kth from end nodes in a linked list.

Detailed:
You are given the head of a linked list, and an integer k.

Return the head of the linked list after swapping the values of the kth node from the beginning and the kth node from the end (the list is 1-indexed).
*/

// Solution O(n) time, one pass, O(1) space
/*
Initialize a fast pointer to start at the kth element. Once it is there, create a slow pointer at the start, move them together until the fast one reaches the end, then slow will point at the kth from end. Swap the values. This works because the k distance is the same from both sides.
*/

var swapNodes = function (head, k) {
  let slow = head;
  let fast = head;
  // set the fast pointer to start at the kth element
  for (let i = 0; i < k - 1; i++) {
    fast = fast.next;
  }

  let kthElement = fast;

  // iterate both pointers together to get the kth from end
  while (fast && fast.next) {
    slow = slow.next;
    fast = fast.next;
  }

  // now, slow points to the kth element from the end

  const temp = kthElement.val;
  kthElement.val = slow.val;
  slow.val = temp;

  return head;
};
