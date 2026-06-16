# https://leetcode.com/problems/subdomain-visit-count/
# difficulty: medium

# Problem
# A website domain "discuss.leetcode.com" consists of various subdomains. At the top level, we have "com", at the next level, we have "leetcode.com" and at the lowest level, "discuss.leetcode.com". When we visit a domain like "discuss.leetcode.com", we will also visit the parent domains "leetcode.com" and "com" implicitly.

# A count-paired domain is a domain that has one of the two formats "rep d1.d2.d3" or "rep d1.d2" where rep is the number of visits to the domain and d1.d2.d3 is the domain itself.

# For example, "9001 discuss.leetcode.com" is a count-paired domain that indicates that discuss.leetcode.com was visited 9001 times.
# Given an array of count-paired domains cpdomains, return an array of the count-paired domains of each subdomain in the input. You may return the answer in any order.

# Solution
class Solution:
    def subdomainVisits(self, cpdomains: List[str]) -> List[str]:
        counts = defaultdict(int)
        for cpdomain in cpdomains:
            number, domain = cpdomain.split(' ')
            number = int(number)
            for i in range(len(domain) - 1, -1, -1):
                if domain[i] == '.':
                    subdomain = domain[i + 1:]
                    counts[subdomain] += number
            counts[domain] += number

        return [
            str(counts[key]) + ' ' + key for key in counts
        ]

    # iterate over n domains in cpdomains
    # for each domain string, it is up to length m, and split into up to ~m/2 pieces
    # each piece takes m time to create the substring and also increment the count for it
    # n * m * m time
    # store up to m^2 unique subdomains in counts so m^2 space