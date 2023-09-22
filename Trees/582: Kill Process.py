# https://leetcode.com/problems/kill-process/
# Difficulty: Medium
# Tags: trees, dfs

# Problem
# You have n processes forming a rooted tree structure. You are given two integer arrays pid and ppid, where pid[i] is the ID of the ith process and ppid[i] is the ID of the ith process's parent process.

# Each process has only one parent process but may have multiple children processes. Only one process has ppid[i] = 0, which means this process has no parent process (the root of the tree).

# When a process is killed, all of its children processes will also be killed.

# Given an integer kill representing the ID of a process you want to kill, return a list of the IDs of the processes that will be killed. You may return the answer in any order.

# Solution, O(n) time and space
# First create pointers for each node to its list of children. Then dfs on the target and kill nodes repeatedly.

class Solution:
    def killProcess(self, pid: List[int], ppid: List[int], kill: int) -> List[int]:
        children = defaultdict(list) # maps a node to its children
        for i, child in enumerate(pid):
            parent = ppid[i]
            children[parent].append(child)

        res = []
        def dfs(node):
            res.append(node)
            for child in children[node]:
                dfs(child)
        dfs(kill)
        return res
