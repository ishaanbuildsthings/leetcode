# # Bottom up pull DP n*k
# n, k = map(int, input().split())
# moves = set(list(map(int, input().split())))

# winnable = [False] * (n + 1)
# for sticks in range(1, n + 1):
#     if sticks in moves:
#         winnable[sticks] = True
#         continue
#     for remove in moves:
#         nsticks = sticks - remove
#         if nsticks <= 0:
#             continue
#         if not winnable[nsticks]:
#             winnable[sticks] = True
#             break

# arr2 = ['W' if x else 'L' for x in winnable[1:]]
# print(''.join(arr2))

n, k = map(int, input().split())
moves = set(list(map(int, input().split())))


remove = 0 # bitset
for v in moves:
    remove |= (1 << v)
winnable = remove # bitset

result = [True if winnable & (1 << 1) else False] # initialize for sticks = 1

for sticks in range(2, n + 1):
    # 2 is true if any of the 1s 


