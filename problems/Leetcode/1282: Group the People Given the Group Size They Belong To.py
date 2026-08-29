# https://leetcode.com/problems/group-the-people-given-the-group-size-they-belong-to/description/?envType=daily-question&envId=2023-09-11
# Difficulty: Medium

# Problem
# There are n people that are split into some unknown number of groups. Each person is labeled with a unique ID from 0 to n - 1.

# You are given an integer array groupSizes, where groupSizes[i] is the size of the group that person i is in. For example, if groupSizes[1] = 3, then person 1 must be in a group of size 3.

# Return a list of groups such that each person i is in a group of size groupSizes[i].

# Each person should appear in exactly one group, and every person must be in a group. If there are multiple answers, return any of them. It is guaranteed that there will be at least one valid solution for the given input.

# Solution, O(groups) time, O(unique group sizes) space
# Iterate through, adding to the current group. If we reach the group size, add it to the result and reset.

class Solution:
    def groupThePeople(self, groupSizes: List[int]) -> List[List[int]]:
        groups = collections.defaultdict(list) # maps a group size to the current group that is being worked on
        result = []

        for person_id, group_size_required in enumerate(groupSizes):
            current_group_being_worked_on = groups[group_size_required]
            current_group_being_worked_on.append(person_id)
            if len(current_group_being_worked_on) == group_size_required:
                result.append(current_group_being_worked_on)
                groups[group_size_required] = []

        return result
