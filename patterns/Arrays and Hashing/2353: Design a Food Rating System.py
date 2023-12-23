# https://leetcode.com/problems/design-a-food-rating-system/?envType=daily-question&envId=2023-12-17
# difficulty: medium
# tags: avl

# Problem
# Design a food rating system that can do the following:

# Modify the rating of a food item listed in the system.
# Return the highest-rated food item for a type of cuisine in the system.
# Implement the FoodRatings class:

# FoodRatings(String[] foods, String[] cuisines, int[] ratings) Initializes the system. The food items are described by foods, cuisines and ratings, all of which have a length of n.
# foods[i] is the name of the ith food,
# cuisines[i] is the type of cuisine of the ith food, and
# ratings[i] is the initial rating of the ith food.
# void changeRating(String food, int newRating) Changes the rating of the food item with the name food.
# String highestRated(String cuisine) Returns the name of the food item that has the highest rating for the given type of cuisine. If there is a tie, return the item with the lexicographically smaller name.
# Note that a string x is lexicographically smaller than string y if x comes before y in dictionary order, that is, either x is a prefix of y, or if i is the first position such that x[i] != y[i], then x[i] comes before y[i] in alphabetic order.

# Solution
# I used a few hashmaps and an AVL to sort the ratings while allowing editing of them.

import sortedcontainers

class FoodRatings:

    def __init__(self, foods: List[str], cuisines: List[str], ratings: List[int]):
        self.cuisineToRatings = defaultdict(
            lambda: sortedcontainers.SortedList(
                key=lambda x: (x[0], tuple(-ord(char) for char in x[1]))
                )
            )

        for i in range(len(foods)):
            cuisine = cuisines[i]
            rating = ratings[i]
            food = foods[i]
            self.cuisineToRatings[cuisine].add((rating, food))

        self.foodToCuisine = {
            foods[i] : cuisines[i]
            for i in range(len(foods))
        }

        self.foodToRatings = {
            foods[i] : ratings[i]
            for i in range(len(foods))
        }

    def changeRating(self, food: str, newRating: int) -> None:
        cuisine = self.foodToCuisine[food]
        oldRating = self.foodToRatings[food]
        # update rating
        self.foodToRatings[food] = newRating
        self.cuisineToRatings[cuisine].remove((oldRating, food))
        self.cuisineToRatings[cuisine].add((newRating, food))

    def highestRated(self, cuisine: str) -> str:
        return self.cuisineToRatings[cuisine][-1][1]


# Your FoodRatings object will be instantiated and called as such:
# obj = FoodRatings(foods, cuisines, ratings)
# obj.changeRating(food,newRating)
# param_2 = obj.highestRated(cuisine)

