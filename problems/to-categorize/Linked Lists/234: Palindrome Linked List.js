// https://leetcode.com/problems/palindrome-linked-list/description/
// Difficulty: Easy
// slow and fast pointers
// tags: palindrome

// Problem
/*
Given the head of a singly linked list, return true if it is a palindrome or false otherwise.
*/

// Solution, O(n) time and O(1) space
/*
Find the midpoint of the linked list. Reverse the second half, iterate over both halves and compare the values. If the pointers collide after checking values, we have an odd lengthed palindrome. If the end pointer reaches null (it would always reach null before the beginning one, for even-lengthed palindromes), then we have a palindrome. If the values are ever different, we don't have a palindrome. We store the result in a variable since we need to know what to return, and then we reverse the second half again to restore the linked list. We don't need to worry about severing off the connection from the first half to the second half, for instance:
1->2->3->4->

when we reverse from 3, we get:
1->2->3<-4
      V

Then when we un-reverse it, we get:
1->2->3->4->

2 can point to 3 during all the reversing, and in fact helps because we can check if the beginning and end pointer ever collide (which they do in odd lengthed palindromes)

*/

var isPalindrome = function (head) {
  // find the midpoint
  let slow = head;
  let fast = head;
  while (fast && fast.next) {
    fast = fast.next.next;
    slow = slow.next;
  }
  // now slow will err right for even lengths, or be the middle for odd lengths

  // reverse from the midpoint
  let prev = null;
  while (slow) {
    const temp = slow.next;
    slow.next = prev;
    prev = slow;
    slow = temp;
  }
  // now prev points to the end

  // save the ending for later when we need to repair the linked list
  let endOfReversed = prev;

  // iterate the beginning and end until a condition is met
  let beginning = head;
  let end = prev;

  // decide what to return, but we cannot return it yet since we need to repair the list
  let result;

  while (beginning && end) {
    // compare the values
    if (beginning.val === end.val) {
      // increment
      beginning = beginning.next;
      end = end.next;
    }
    // if the values were different, we don't have a palindrome
    else {
      result = false;
      break;
    }

    // if after incrementing and verifying the values, the pointers land on the same value, we have an odd lengthed palindrom
    if (beginning === end) {
      result = true;
      break;
    }
  }

  // if the loop ends, we either broke because we had an odd lengthed palindrome, because we found a mismatched value, or because we iterated across an even-lengthed palindrome and the end pointer reached null (since end is always slightly shorter to reach null, for even-lengthed palindromes)
  if (!end) {
    result = true;
  }

  prev = null;
  while (endOfReversed) {
    const temp = endOfReversed.next;
    endOfReversed.next = prev;
    prev = endOfReversed;
    endOfReversed = temp;
  }

  return result;

  // 1->1->2->1->
  // 1->1->2<-1
  //       V

  /*
reverse the linked list starting at slow

    1->2->3->
       ^
       slow is pointing here

    reversing 2->3-> gives <-2<-3

    but 1 points to 2, so we have 1->2<-3
                                     V

    iterate starting from the beginning and end, if they ever equal each other we have a palindrome


    1->2->3->4->
          ^
          slow is pointing here

    reversing from 3 gives:
    <-3<-4

    but 2 points to 3, so we have:

    1->2->3<-4
          V

    if beginning.next ever equals end, we have an even length palindrome

*/
};

// Solution 2, O(n) time and O(n) space, add previous pointers to each node, iterate, then compare. Remove the previous pointers. It's O(n) space since we are adding prev pointers. We could also then just add values into an array and use two pointers on the array, since that is also O(n).

var isPalindrome = function (head) {
  let tail = head;
  let prev = null;
  while (tail && tail.next) {
    tail.prev = prev;
    prev = tail;
    tail = tail.next;
  }
  tail.prev = prev;

  let left = head;
  while (left !== tail && left !== tail.next) {
    if (left.val === tail.val) {
      left = left.next;
      tail = tail.prev;
    } else {
      return false;
    }
  }
  return true;
};
