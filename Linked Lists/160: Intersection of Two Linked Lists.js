// https://leetcode.com/problems/intersection-of-two-linked-lists/description/
// Difficulty: Easy
// tags: Linked Lists

// Problem
/*
Given the heads of two singly linked-lists headA and headB, return the node at which the two lists intersect. If the two linked lists have no intersection at all, return null.
*/

// Solution
// O(n + m) time to iterate over both linked lists. O(1) space. Iterate over the linked lists and figure out their lengths. Whichever one is longer, say 7 vs 4, increment it until the pointers are positioned at the same area. Then, increment both pointers by 1 until they are equal. Return the node or null if they are never equal.
// We could also overwrite nodes to have negative values, since that wasn't allowed in the constraints, and then as soon as we see a -1 we return that node.

var getIntersectionNode = function (headA, headB) {
  let lengthA = 0;
  // new pointer used to count
  let a = headA;
  while (a) {
    lengthA++;
    a = a.next;
  }
  let lengthB = 0;
  // new pointer used to count
  let b = headB;
  while (b) {
    lengthB++;
    b = b.next;
  }

  if (lengthB > lengthA) {
    for (let i = 0; i < lengthB - lengthA; i++) {
      headB = headB.next;
    }
  } else if (lengthA > lengthB) {
    for (let i = 0; i < lengthA - lengthB; i++) {
      headA = headA.next;
    }
  }

  while (headA && headB) {
    if (headA === headB) {
      return headA;
    }
    headA = headA.next;
    headB = headB.next;
  }

  return null;
};
