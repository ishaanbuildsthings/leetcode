# https://leetcode.com/problems/frequency-tracker/
# Difficulty: Medium

# Problem
# Design a data structure that keeps track of the values in it and answers some queries regarding their frequencies.

# Implement the FrequencyTracker class.

# FrequencyTracker(): Initializes the FrequencyTracker object with an empty array initially.
# void add(int number): Adds number to the data structure.
# void deleteOne(int number): Deletes one occurrence of number from the data structure. The data structure may not contain number, and in this case nothing is deleted.
# bool hasFrequency(int frequency): Returns true if there is a number in the data structure that occurs frequency number of times, otherwise, it returns false.

# Solution, O(1) for add, init, delete, has frequency, O(n) space
# Just track the frequencies and numbers with two hashmaps.