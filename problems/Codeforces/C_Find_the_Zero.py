import sys
input = sys.stdin.readline

def ask(query):
    print(f"? {query}", flush=True)
    response = int(input())
    if response == -1:
        exit()
    return response

def answer(val):
    print(f"! {val}", flush=True)

def solve():
    n = int(input())
    N = 2 * n
    for i in range(1, N - 1, 2):
        response = ask(f'{i} {i+1}')
        if response == 1:
            answer(i)
            return
    if ask(f'1 {N - 1}') == 1:
        answer(1)
        return
    if ask(f'2 {N - 1}') == 1:
        answer(2)
        return
    answer(N)
        
    # if we do [1, 2] [1, 2] [1, 2] [1, 2]

    # it is guaranteed none are equal meaning each pair has one 0 and one number

    # maybe we do it for half the pairs

    # now it could be all 1...N or split {num, 0} or anything in between

    # now we make the first two pairs fully {1, 2} {3, 4}

    # we need 6 queries, then (n)-2 queries for the remainder

    # we need (n)+4 queries

    # N is the number of pairs

    # if we look at N/2 pairs worst case they had all 1...N in it


    # compare every number against the first number for N queries
    # if the first number is 0, all the numbers are 1 to N
    # if its a number, at least one of those was a 0, at most all of them were 0s



    # look at the first N numbers
    # so in n/2 queries we query half the pairs
    # each pair could have a 0, so at most n/2 0s
    # each pair could have two numbers so at minimum zero 0s



    # query the first half of pairs

    # if there were no 0s in it we are going to win on the second half of all 0s 1 2 3 4 5 6 0 0 0 0 0 0

    # if there was one 0:
    # 1 0 2 3 4 5 | 6 0 0 0 0 0 we must win


     # 1 0 2 0 3 4 | 5 0 6 0 (0 0)
     # last pair could be 0s meaning we win, or it could be (num, 0)

     # DONT GUESS LAST PAIR

     # either
     # 1 0 2 0 3 4 | 5 0 6 0 (0 0)
     # 1 0 2 0 3 0 | 4 0 5 0 (6 0)

     # in case 1, we do 3<>0 3<>0, if both fail, we know the last pair is 0,0
     # in case 2 we do 3<>6 3<>0 we nneed to guess one of the last two hmm

     # !!!!!!!!
     # or maybe
     # we do 3<>0 4<>0 in case 1, we guess the other 0
     # we do 3<>6 0<>6, we guess the other 0
     # we do 0<>6 0<>0 we win
     # !!!!!!!!
     # ^WORKING IDEA



     # for n+2 queries we do all pairs of N
     # then we know everything is (X, 0) (Y, 0)
     # do X<>Y X<>0, if both failed it means we hold X, so guess the other option

     # but in (X, Y) (0, 0) case if both failed then the other thing could be 0s


    # if it was like 1 0 2 0 3 0 | 4 0 5 0 6 0
    # 



t = int(input())
for _ in range(t):
    solve()