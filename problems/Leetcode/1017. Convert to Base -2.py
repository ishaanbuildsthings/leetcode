class Solution:
    def baseNeg2(self, n: int) -> str:
        if n == 0:
            return '0'
        resArr = []
        while n:
            # what is the ones digit? it could be 0 or 1
            if n % -2:
                n -= 1
                resArr.append('1')
            else:
                resArr.append('0')
            # "shift right"
            n //= - 2
        return ''.join(resArr)[::-1]


# convert a number 273 to base 5
# think of 273 as an abstract quantity of things, not the digits "273"
# we can solve by smallest bit first, or largest bit first

# largest bit first:
# is 5^0 <= 273? yes
# is 5^1 <= 273? yes
# is 5^2 <= 273? yes
# is 5^3 <= 273? yes
# is 5^4? no

# so the 3rd bit is the largest, 125, and it goes in twice:
# 2 ? ? ? ?

# now we have 23 remaining, how many times does 25 go in? 0

# 2 0 ? ? ?

# 23 remaining, 5 goes in 4 times, and the last 3 go in once

# 2 0 4 3


# smallest bit first:
# we can immediately deduce the smallest bit by taking 273 % 5, which is 3
# no other bit can account for this since 1 is the minimum granularity

# ? ? ? ? 3

# now we want the 5s digit, how does it work?
# imagine we are converting 143 to base 10, first we got the ones digit as 3, now we have 140 left
# we want the tens digit, e.g. how many groups of 10 are needed and wont fit into 100
# we could just do 140 % 100 = 40 and know we get 4 groups of 10, this does work

# but the logic/code ends up being such that we could perform a right shift on our number
# so: 143 -> 143//10 -> 14
# and now we have moved the tens digit into the ones digit type of thing, we we take 14 % 10 = 4 to produce the next digit

# we could subtract 3 first from 143 to make it 140, then floor divide, or just floor divide
# for this specific question since the base is -2, floor division truncates the wrong way I think
# so we subtract 1 to fix it

# similarly to take 273 things and get the fives digit, we can right shift:
# 273 -> 273//5 -> 54, and then take 54%5 = 4 which is the second digit
