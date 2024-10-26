// https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up/submissions/
// difficulty: medium

// Problem
/*
You are given an integer array cards where cards[i] represents the value of the ith card. A pair of cards are matching if the cards have the same value.

Return the minimum number of consecutive cards you have to pick up to have a pair of matching cards among the picked cards. If it is impossible to have matching cards, return -1.
*/

// Solution, O(n) time and space
/*
Just iterate through each card, maintaining a hashmap of the previous positions for each unique card type. Check the distance, update result, and the latest position.
*/

var minimumCardPickup = function (cards) {
  const positions = {}; // maps a number to its latest position as we traverse

  let result = Infinity;

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    if (!(card in positions)) {
      positions[card] = i;
    } else {
      const lastPosition = positions[card];
      const totalCardsPickedUp = i - lastPosition + 1;
      result = Math.min(result, totalCardsPickedUp);
      positions[card] = i;
    }
  }

  return result === Infinity ? -1 : result;
};
