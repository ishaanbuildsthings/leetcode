from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import bisect
import collections
from collections import defaultdict, Counter
import sortedcontainers
import heapq
from heapq import nlargest, nsmallest
from functools import cache
import itertools

# example format
# """Input: s = "1001", k = 3
# Output: 4"""
testcases = [
"""Input: source = "abcd", target = "acbe", original = ["a","b","c","c","e","d"], changed = ["b","c","b","e","b","e"], cost = [2,5,5,1,2,20]
Output: 28""",
"""Input: source = "abcdefgh", target = "acdeeghh", original = ["bcd","fgh","thh"], changed = ["cde","thh","ghh"], cost = [1,3,5]
Output: 9""",
"""Input: source = "abcdefgh", target = "addddddd", original = ["bcd","defgh"], changed = ["ddd","ddddd"], cost = [100,1578]
Output: -1""",
]

class Solution:
    def minimumCost(self, source: str, target: str, original: List[str], changed: List[str], cost: List[int]) -> int:

        def charCode(char):
            return ord(char) - ord('a') + 1

        MOD = 10**11 + 7

        # HASHING THE STRINGS SO WE CAN QUERY THEM IN THE DP EASILY
        sourceHashes = {} # maps 'l,r' to the hashkey for the source
        for i in range(len(source)):
            hash = 0
            for j in range(i, len(source)):
                newChar = source[j]
                hash *= 26
                hash += charCode(newChar)
                hash %= MOD
                sourceHashes[(i, j)] = hash
        # print(f'source hashes: {sourceHashes}')
        targetHashes = {}
        for i in range(len(target)):
            hash = 0
            for j in range(i, len(target)):
                newChar = target[j]
                hash *= 26
                hash += charCode(newChar)
                hash %= MOD
                targetHashes[(i, j)] = hash
        # print(f'target hashes: {targetHashes}')


        # HASHING THE WORDS THEMSELVES SO WE CAN DO DJIKSTRAS FROM A HASH TO A HASH
        originalHashes = [] # hashed versions of the words
        for word in original:
            hash = 0
            for char in word:
                hash *= 26
                hash += charCode(char)
                hash %= MOD
            originalHashes.append(hash)
        changedHashes = []
        for word in changed:
            hash = 0
            for char in word:
                hash *= 26
                hash += charCode(char)
                hash %= MOD
            changedHashes.append(hash)
        # print(f'original hashes: {originalHashes}')
        # print(f'changed hashes: {changedHashes}')


        # OLD EDGE MAP THAT GOES FROM ORIGINAL WORDS TO CHANGED WORDS
        # edgeMap = collections.defaultdict(lambda: defaultdict(lambda: float('inf'))) # edgeMap[fromletter][toletter] = cost
        # for i in range(len(original)):
        #     edgeMap[original[i]][changed[i]] = min(edgeMap[original[i]][changed[i]], cost[i])
        # # print(f'edge map is: {edgeMap}')

        # NEW EDGE MAP THAT GOES FROM ORIGINAL HASHES TO CHANGED HASHES
        edgeMap = collections.defaultdict(lambda: defaultdict(lambda: float('inf'))) # edgeMap[fromhash][tohash] = cost
        for i in range(len(original)):
            edgeMap[originalHashes[i]][changedHashes[i]] = min(edgeMap[originalHashes[i]][changedHashes[i]], cost[i])
        # print(f'edge map on hashes is: {edgeMap}')

        @cache
        def dijkstra(start, end):
            # print(f'djikstra called on start hash: {start} end hash: {end}')
            shortest = defaultdict(lambda: float('inf'))
            heap = [(0, start)] # distance, node letter

            while heap:
                cost, char = heapq.heappop(heap)
                if cost >= shortest[char]:
                    continue
                shortest[char] = cost
                for adj in edgeMap[char]:
                    newCost = cost + edgeMap[char][adj]
                    # pruning
                    if shortest[adj] <= newCost:
                        continue

                    heapq.heappush(heap, [newCost, adj])

            res = shortest[end]
            # print(f'returning: {res}')
            return res

        memo = [-1] * len(source)
        # @cache
        def dp(i):
            # base case
            if i == len(source):
                return 0

            if memo[i] != -1:
                return memo[i]

            resThis = float('inf')
            # we can skip this letter
            if source[i] == target[i]:
                resThis = dp(i + 1)

            # the region we change is i:r
            for r in range(i, len(source)):
                currHash = sourceHashes[(i, r)]
                desiredHash = targetHashes[(i, r)]
                # print(f'in dp')
                # print(f'curr hash: {currHash} for i={i} r={r}')
                # print(f'desired hash: {desiredHash} for i={i} r={r}')
                # if currHash != desiredHash:
                #     continue
                # currString = source[i:r+1]
                # desiredOutput = target[i:r+1]
                # djikstraCost = dijkstra(currString, desiredOutput)
                djikstraCost = dijkstra(currHash, desiredHash)
                resAdj = djikstraCost + dp(r + 1)
                resThis = min(resThis, resAdj)
            memo[i] = resThis
            return resThis


        res = dp(0)
        if res == float('inf'):
            return -1
        return res