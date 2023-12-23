# https://leetcode.com/problems/candy/description/?envType=daily-question&envId=2023-09-13
# Difficulty: Hard

# Problem
# There are n children standing in a line. Each child is assigned a rating value given in the integer array ratings.

# You are giving candies to these children subjected to the following requirements:

# Each child must have at least one candy.
# Children with a higher rating get more candies than their neighbors.
# Return the minimum number of candies you need to have to distribute the candies to the children.

# Solution, O(n log n) time and O(n) pace.
# We can just simulate it. Start with the smallest rating (found via sorting). Insert the candy there. As we move up rating, we can check if our neighbors have lower rating and know how many candies to add based on that.

class Solution:
    def candy(self, ratings: List[int]) -> int:
        positions = defaultdict(list) # maps a rating to a list of indices it occurs at
        for i, rating in enumerate(ratings):
            positions[rating].append(i)

        # by default, put 1 candy at each position, we used a default dict so if we key outside the boundaries we get 0 candies
        candyArr = defaultdict(int)
        for i in range(len(ratings)):
            candyArr[i] = 1

        for ratingKey in sorted(positions.keys()):
            for index in positions[ratingKey]:
                # set boundary ratings to be 0
                leftRating = ratings[index - 1] if 0 <= index - 1 else 0
                rightRating = ratings[index + 1] if index + 1 < len(ratings) else 0
                # if we are <= both boundaries, we can just put 1 candy
                if rightRating >= ratings[index] <= leftRating:
                    candyArr[index] = 1
                # if we are bigger than only the right boundary, we must put more candies than the right has
                elif ratings[index] > rightRating and ratings[index] <= leftRating:
                    candyArr[index] = candyArr[index + 1] + 1
                # if we are higher rating than only the left, we use more candies than that
                elif ratings[index] > leftRating and ratings[index] <= rightRating:
                    candyArr[index] = candyArr[index - 1] + 1
                # if we are bigger than both, we use 1 more candy than the biggest
                else:
                    newCandies = max(candyArr[index - 1], candyArr[index + 1]) + 1
                    candyArr[index] = newCandies

        return sum(candyArr.values())