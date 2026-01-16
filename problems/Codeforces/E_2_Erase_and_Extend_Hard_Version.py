# We will enumerate prefixes greedily
# Say we have some prefix "db" and are considering if "dbc" repeated is better
# That c will compare to the start of our prefix, d, so it is better
# If we were at "db" and considering "f", clearly "db" + "d" is better than "dbf" and we fail
# if the letter is equal, like "dbca" considering "d" (in the test "dbcadabc") we don't know which sequence is better yet
# We store "dbca" as the best still but accept the new "d" as an option and keep going
# If we keep going a lot, say our initial prefix |AB| CDEFGHHIJK like everything after C is being marked as equal
# We don't need to mod our "indexToConsider" back to the beginning, I think because it is guaranteed the CDEFGH... portion is just ABABAB repeated
n, k = map(int, input().split())
s = input()

bestPf = 0
indexToConsider = 0
for r in range(1, n):
    if s[r] > s[indexToConsider]:
        break
    if s[r] < s[indexToConsider]:
        bestPf = r
        indexToConsider = 0
        continue
    # if they are equal we will try it for now
    indexToConsider += 1


portion = s[:bestPf+1]
fulls = k // len(portion)
res = fulls * portion
remain = k - len(res)
res += s[:remain]
print(res)
    