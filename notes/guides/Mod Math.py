"""
We have some number X and its remainder, r, mod M.
This means there is some integer q such that X = q*M + r.

We wish to append a number to the end of X. Say X is 315 and we want to make it 3152. We want to compute the new remainder quickly.

My claim is we can do (r*10 + d) % M. d is the new digit.

newX = 10*X + d.

Substitute q*M + r into that:

newX = 10*(q*M + r) + d.
newX = 10*q*M + 10*r + d.

Take this mod M. We can take the individual pieces mod M due to addition mod math.

10*q*M has a remainder 0 mod M because it is divisible.

So the remainder is (10*r + d) % M.
"""