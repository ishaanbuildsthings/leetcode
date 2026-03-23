class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        parent = {}
        rank = {}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(a, b):
            a, b = find(a), find(b)
            if a == b:
                return
            if rank[a] < rank[b]:
                a, b = b, a
            parent[b] = a
            if rank[a] == rank[b]:
                rank[a] += 1

        emailToName = {}
        allEmails = []

        for account in accounts:
            name = account[0]
            for i in range(1, len(account)):
                email = account[i]
                if email not in parent:
                    parent[email] = email
                    rank[email] = 0
                    allEmails.append(email)
                emailToName[email] = name

        for account in accounts:
            for i in range(1, len(account) - 1):
                union(account[i], account[i + 1])

        groups = defaultdict(list)
        for e in allEmails:
            groups[find(e)].append(e)

        result = []
        for rep, bucket in groups.items():
            name = emailToName[bucket[0]]
            newEntry = [name]
            for email in sorted(bucket):
                newEntry.append(email)
            result.append(newEntry)

        return result