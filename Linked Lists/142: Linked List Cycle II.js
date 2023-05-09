// https://leetcode.com/problems/linked-list-cycle-ii/description/
// Difficulty: Medium
// tags: linked list, slow and fast pointers

// Problem
/*
Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return null.

There is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the next pointer. Internally, pos is used to denote the index of the node that tail's next pointer is connected to (0-indexed). It is -1 if there is no cycle. Note that pos is not passed as a parameter.
*/

// Solution
// O(n) time and O(1) space. Use a slow and fast pointer until they collide. Then, create another slow pointer at the beginning. Increment that, and the collided slow pointer until they meet.

/* proof:
 let p = distance from beginning the the head of the cycle
 let c = distance from the head of the cycle to the collision point
 let loop = length of the cycle
 therefore, loop - c = distance from the collision point to the head of the cycle

 we are trying to prove that p = loop - c
 fast pointer traveled: p + n*loops + c
 slow pointer traveled: p + c
 fast pointer traveled 2x as much as slow pointer: 2(p + c) = p + n*loops + c
 2p + 2c = p + n*loops + c
 p + c = n*loops
 p = n*loops - c!
 */

const detectCycle = function (head) {
  let slowPointer = head;
  let fastPointer = head;
  // if fastPointer itself is null from the previous loop we need to short circuit to not check null.next
  while (fastPointer && fastPointer.next) {
    slowPointer = slowPointer.next;
    fastPointer = fastPointer.next.next;
    if (slowPointer === fastPointer) {
      break;
    }
  }
  // if fast pointer is nothing, the list ended
  if (!fastPointer) {
    return null;
  }
  // if fast pointer is pointing to nothing, the list ended
  if (!fastPointer.next) {
    return null;
  }

  let slowPointerBeginning = head;
  while (slowPointerBeginning !== slowPointer) {
    slowPointerBeginning = slowPointerBeginning.next;
    slowPointer = slowPointer.next;
  }

  return slowPointerBeginning;
};
