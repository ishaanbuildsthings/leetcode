numStones, startingStones = map(int, input().split())
moveOptions = list(map(int, input().split()))

canForceWinIfMyTurn = [False] * (startingStones + 1)
for stones in range(1, startingStones + 1):
  for move in moveOptions:
    prev = stones - move
    if prev < 0:
      break
    if not canForceWinIfMyTurn[prev]:
      canForceWinIfMyTurn[stones] = True

print("First" if canForceWinIfMyTurn[startingStones] else "Second")


# Commented out because the paramaters were too large for the top down python, might work in C++
# from functools import lru_cache

# moveSet = set(moveOptions)

# @lru_cache
# def dp(stones):
#   if stones in moveSet:
#     return True
#   for sub in moveOptions:
#     if dp(stones - sub):
#       return True
#   return False

# print(dp(startingStones))