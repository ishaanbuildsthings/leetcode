// https://leetcode.com/problems/remove-duplicates-from-sorted-list/description/
// Difficulty: Easy

// Problem
/*
Given the head of a sorted linked list, delete all duplicates such that each element appears only once. Return the linked list sorted as well.
 */

// Solution, O(n) time and O(1) space
/*
Iterate over the linked list. At each node, iterate until we find a different-valued node (or null). Skip over all of those by rewiring the .next and then start iterating from that node onwards.
*/
var deleteDuplicates = function (head) {
  let tail = head;
  while (tail) {
    let r = tail;
    while (r && r.val === tail.val) {
      r = r.next;
    }
    tail.next = r;
    tail = r;
  }

  return head;
};
