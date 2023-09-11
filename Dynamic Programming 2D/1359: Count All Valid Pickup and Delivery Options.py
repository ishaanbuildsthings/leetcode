# https://leetcode.com/problems/count-all-valid-pickup-and-delivery-options/description/?envType=daily-question&envId=2023-09-10
# Difficulty: Hard
# Tags: Dynamic Programming 2d

# Problem
# Given n orders, each order consist in pickup and delivery services.

# Count all valid pickup/delivery possible sequences such that delivery(i) is always after of pickup(i).

# Since the answer may be too large, return it modulo 10^9 + 7.

# Solution 1, O(n) time, O(1) space
# Since we have 2n things to arrange, that is 2n! arrangements. But only the ones where p1<d1, p2<d2, ... work. So we can divide by 2^n. 2n! / 2^n is the answer. I didn't implmenet it though because of the mod math.

# Solution 2, O(n^2) time and space
# We have to place 2n things. For each thing, we can either take a new pickup, or satisfy a previous pickup. So our dp is the index we are at, and the amount of excess pickups we have. We don't have to track the specific pickups, we just know we can satiate any prior excess pickup.

MOD = (10**9) + 7
class Solution:
    def countOrders(self, n: int) -> int:
        # memo[i][surplus p] tells us the answer to that subproblem
        memo = [[-1 for _ in range(n + 1)] for _ in range(n * 2)]

        def dp(i, surplus_p):
            # base case
            if i == n * 2:
                if surplus_p == 0:
                    return 1
                return 0

            if memo[i][surplus_p] != -1:
                return memo[i][surplus_p]

            deliveries_processed = (i - surplus_p) / 2
            pickups_processed = i - deliveries_processed
            new_pickups = n - pickups_processed

            # d+p = i
            # p = d + surplus
            # d+d+surplus = i

            result_for_this = 0
            # we can take any of new pickup, then get a subproblem
            if new_pickups > 0:
                result_for_this = (new_pickups * dp(i + 1, surplus_p + 1)) % MOD
            # we can take a delivery for a surplus we have already done
            if surplus_p > 0:
                result_for_this += (surplus_p * dp(i + 1, surplus_p - 1)) % MOD

            memo[i][surplus_p] = result_for_this
            return result_for_this

        return int(dp(0, 0)) % MOD