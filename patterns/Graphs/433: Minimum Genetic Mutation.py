# https://leetcode.com/problems/minimum-genetic-mutation/description/
# difficulty: medium
# tags: graph, bfs

# Problem
# A gene string can be represented by an 8-character long string, with choices from 'A', 'C', 'G', and 'T'.

# Suppose we need to investigate a mutation from a gene string startGene to a gene string endGene where one mutation is defined as one single character changed in the gene string.

# For example, "AACCGGTT" --> "AACCGGTA" is one mutation.
# There is also a gene bank bank that records all the valid gene mutations. A gene must be in bank to make it a valid gene string.

# Given the two gene strings startGene and endGene and the gene bank bank, return the minimum number of mutations needed to mutate from startGene to endGene. If there is no such a mutation, return -1.

# Note that the starting point is assumed to be valid, so it might not be included in the bank.

# Solution
# Get edges between all two genes, do BFS from start to end

class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        # fast prune
        if not endGene in bank:
            return -1


        def canMutate(gene1, gene2):
            return sum(
                1 if gene1[i] != gene2[i] else
                0
                for i in range(len(gene1))
            ) == 1

        edgeMap = defaultdict(list) # stores edges from one gene to another
        for i in range(len(bank) - 1):
            for j in range(i + 1, len(bank)):
                if canMutate(bank[i], bank[j]):
                    edgeMap[bank[i]].append(bank[j])
                    edgeMap[bank[j]].append(bank[i])
        for gene in bank:
            if canMutate(startGene, gene):
                edgeMap[startGene].append(gene)
                edgeMap[gene].append(startGene)

        res = 1
        seen = set()
        seen.add(startGene)
        q = collections.deque()
        q.append(startGene)
        while q:
            length = len(q)
            for _ in range(length):
                gene = q.popleft()
                for adj in edgeMap[gene]:
                    if adj == endGene:
                        return res
                    if adj in seen:
                        continue
                    q.append(adj)
                    seen.add(adj)
            res += 1
        return -1




