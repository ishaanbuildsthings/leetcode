# hashmap:

seen = {}
if 5 in seen: # checks if something is in the hashmap
  print("yes")


# array:
nums = [1, 2, 3]
for num in nums:
  print(num) # prints 1, 2, 3

for i, num in enumerate(nums):
  print(i, num) # prints 0 1, 1 2, 2 3

# math
x = 15
x //= 10 # floor divide by 10, so we get 1
rounded_up = math.ceil(1.5) # rounds up to 2, may be included by default, or maybe need to import math, not sure, it works on leetcode

# prefix sum
import itertools
prefixSum = list(itertools.accumulate(nums, initial=0))

# get key for something with a max value in a hashmap:
max_key = max(hashmap, key=hashmap.get)