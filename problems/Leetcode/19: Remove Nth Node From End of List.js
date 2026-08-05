//https://leetcode.com/problems/remove-nth-node-from-end-of-list/description/
// Difficulty: Medium
// tags: linked list

// Problem
/*
Given the head of a linked list, remove the nth node from the end of the list and return its head.
*/

// Solution
// O(n) time and O(1) space.
// Iterate over the linked list, count the length. Iterate over it again, and remove the element, by finding the pointer before the element we need to remove. If we are removing the head, handle that as an edge case, since there is no pointer before it.
// Solution 2 - we could also use two pointers spaced n apart, and then increment them both until the second one is null. Then, remove the first one.

var removeNthFromEnd = function (head, n) {
  let length = 0;
  let headForCounting = head;
  // determine the length
  while (headForCounting) {
    length++;
    headForCounting = headForCounting.next;
  }

  const indexOfElementToRemove = length - n;
  const indexBefore = indexOfElementToRemove - 1; // get the previous pointer
  // if we need to remove the head, remove the reference to that pointer
  if (indexBefore === -1) {
    head = head.next;
    return head;
  }

  let index = 0;
  let headForRemoval = head;
  while (index !== indexBefore) {
    headForRemoval = headForRemoval.next;
    index++;
  }
  headForRemoval.next = headForRemoval.next.next;

  return head;
};
