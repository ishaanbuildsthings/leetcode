import random
import math
import collections

# from MaxAndAppearancesSegmentTree import MaxAndAppearancesSegmentTree
from MaxSegmentTree import MaxSegmentTree
# from MinAndAppearancesSegmentTree import MinAndAppearancesSegmentTree
from MinSegmentTree import MinSegmentTree
from GcdLcmSegmentTree import GcdLcmSegmentTree
from CountAndKthIndexSegmentTree import CountAndKthIndexSegmentTree

# TODO, replace recursive traversals with iterative ones?

N = 50000
TEST_CASES = 4000
LOWER_RANDOM_RANGE = -1000
UPPER_RANDOM_RANGE = 1000
CHANCE_OF_UPDATE_BETWEEN_TESTS = 0.5

def testSegmentTree(bruteForceAlg, segmentTreeConstructor, callback, updateCallback):
  randomNumbers = [random.randint(LOWER_RANDOM_RANGE, UPPER_RANDOM_RANGE) for _ in range(N)]
  segmentTree = segmentTreeConstructor(randomNumbers)
  testCasesPassed = 0
  for _ in range(TEST_CASES):

    if random.random() > CHANCE_OF_UPDATE_BETWEEN_TESTS:
      randomIndex = random.randint(0, N - 1)
      randomVal = random.randint(LOWER_RANDOM_RANGE, UPPER_RANDOM_RANGE)
      randomNumbers[randomIndex] = randomVal
      updateCallback(segmentTree, randomIndex, randomVal)

    l = random.randint(0, N - 1)
    r = random.randint(l, N - 1)
    bruteForce = bruteForceAlg(randomNumbers, l, r)
    segmentTreeResult = callback(segmentTree, l, r)

    # uncomment to view all results
    # print("Brute force: ", bruteForce)
    # print("Segment tree: ", segmentTreeResult)

    if bruteForce != segmentTreeResult:
      print("Brute force: ", bruteForce)
      print("Segment tree: ", segmentTreeResult)
      print("l: ", l)
      print("r: ", r)
    else:
      testCasesPassed += 1
  print(f'test cases passed: {testCasesPassed}/{TEST_CASES}')

# max segment tree
def bruteForceMax(arr, l, r):
  return max(arr[l:r + 1])


def bruteForceMaxAndAppearances(arr, l, r):
  counts = collections.Counter(arr[l:r + 1])
  maxVal = max(counts.keys())
  return (maxVal, counts[maxVal])

# max and appearances segment tree
def testMaxAndAppearancesSegmentTree():
  testSegmentTree(bruteForceMaxAndAppearances, MaxAndAppearancesSegmentTree, lambda segmentTree, l, r: segmentTree.queryMaxAndFreq(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))


def testMaxSegmentTree():
  testSegmentTree(bruteForceMax, MaxSegmentTree, lambda segmentTree, l, r: segmentTree.queryMax(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))

# min segment tree
def bruteForceMin(arr, l, r):
  return min(arr[l:r + 1])

def testMinSegmentTree():
  testSegmentTree(bruteForceMin, MinSegmentTree, lambda segmentTree, l, r: segmentTree.queryMin(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))

# min and appearances segment tree
def bruteForceMinAndAppearances(arr, l, r):
  counts = collections.Counter(arr[l:r + 1])
  minVal = min(counts.keys())
  return (minVal, counts[minVal])

def testMinAndAppearancesSegmentTree():
  testSegmentTree(bruteForceMinAndAppearances, MinAndAppearancesSegmentTree, lambda segmentTree, l, r: segmentTree.queryMinAndFreq(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))

# gcd and lcm segment tree
def bruteForceGcd(arr, l, r):
  result = abs(arr[l]) # edge case if l==r
  for i in range(l + 1, r + 1):
    result = math.gcd(result, arr[i])
  return result

def bruteForceLcm(arr, l, r):
    runningLcm = arr[l]
    for i in range(l + 1, r + 1):
        gcd = math.gcd(runningLcm, arr[i])
        if gcd == 0:
          return 0
        runningLcm = (runningLcm * arr[i]) // gcd
    return abs(runningLcm)

def testGcdSegmentTree():
  testSegmentTree(bruteForceGcd, GcdLcmSegmentTree, lambda segmentTree, l, r: segmentTree.queryGcd(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))

def testLcmSegmentTree():
  testSegmentTree(bruteForceLcm, GcdLcmSegmentTree, lambda segmentTree, l, r: segmentTree.queryLcm(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))


# xor segment tree
def bruteForceXor(arr, l, r):
  result = 0
  for i in range(l, r + 1):
    result ^= arr[i]
  return result

def testXorSegmentTree():
  testSegmentTree(bruteForceXor, XorSegmentTree, lambda segmentTree, l, r: segmentTree.queryXor(l, r), lambda segmentTree, posToBeUpdated, newVal: segmentTree.update(posToBeUpdated, newVal))

# testing
# testMaxAndAppearancesSegmentTree()
# testMaxSegmentTree()
# testMinAndAppearancesSegmentTree()
# testMinSegmentTree()
testGcdSegmentTree()
# testLcmSegmentTree()
