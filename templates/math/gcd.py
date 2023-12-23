# MY TEMPLATE
# Get's the GCD of a, b in log min(a, b) time.
def gcd(a, b):
  while b != 0:
    a, b = b, a % b
  return a