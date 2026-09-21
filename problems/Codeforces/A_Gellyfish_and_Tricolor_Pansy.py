# Problem: A. Gellyfish and Tricolor Pansy
# Contest: Codeforces - Codeforces Round 1028 (Div. 2)
# URL: https://codeforces.com/contest/2116/problem/0
# Memory Limit: 256 MB
# Time Limit: 1000 ms
# 
# Powered by CP Editor (https://cpeditor.org)

t = int(input())
for _ in range(t):
    playerA_hp, playerB_hp, knightA_hp, knightB_hp = map(int, input().split())
    aHealth = min(playerA_hp, knightA_hp)
    bHealth = min(playerB_hp, knightB_hp)
    if aHealth >= bHealth:
    	print("Gellyfish")
    else:
    	print("Flower")
    # print(playerA_hp)