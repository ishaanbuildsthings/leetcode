class Node:
    def __init__(self):
        self.tot = 0
        self.cnt = 0

class Seg:
    def __init__(self, lengthCounts):
        self.lengthCounts = lengthCounts
        self.maxLength = len(lengthCounts) - 1
        self.tree = [None] * (4 * self.maxLength)
        self._build(0, self.maxLength, 1)
    
    def _build(self, tl, tr, nodeI):
        if tl == tr:
            self.tree[nodeI] = self._makeLeaf(tl, self.lengthCounts[tl])
            return
        tm = (tl + tr) // 2
        self._build(tl, tm, 2 * nodeI)
        self._build(tm + 1, tr, 2 * nodeI + 1)
        self._pull(nodeI)
    
    def _pull(self, nodeI):
        self.tree[nodeI] = self._agg(self.tree[2 * nodeI], self.tree[2 * nodeI + 1])
    
    def _agg(self, left, right):
        node = Node()
        node.tot = left.tot + right.tot
        node.cnt = left.cnt + right.cnt
        return node

    def _makeLeaf(self, length, count):
        node = Node()
        node.cnt = count
        node.tot = count * length
        return node

    def pointAdd(self, length, delta):
        self._pointAdd(length, delta, 0, self.maxLength, 1)
    
    def _pointAdd(self, length, delta, tl, tr, nodeI):
        if tl == tr:
            node = self.tree[nodeI]
            node.cnt += delta
            node.tot += (delta * length)
            return
        tm = (tl + tr) // 2
        if length <= tm:
            self._pointAdd(length, delta, tl, tm, 2 * nodeI)
        else:
            self._pointAdd(length, delta, tm + 1, tr, 2 * nodeI + 1)
        self._pull(nodeI)
    
    def rangeQuery(self, lengthLow, lengthHigh):
        return self._rangeQuery(lengthLow, lengthHigh, 0, self.maxLength, 1)
    
    def _rangeQuery(self, lengthLow, lengthHigh, tl, tr, nodeI):
        # fully inside
        if lengthLow <= tl and lengthHigh >= tr:
            return self.tree[nodeI]
        # oob
        if lengthHigh < tl or lengthLow > tr:
            node = Node()
            node.cnt = 0
            node.tot = 0
            return node
        # partial
        tm = (tl + tr) // 2
        left = self._rangeQuery(lengthLow, lengthHigh, tl, tm, 2 * nodeI)
        right = self._rangeQuery(lengthLow, lengthHigh, tm + 1, tr, 2 * nodeI + 1)
        return self._agg(left, right)

class Solution:
    def numberOfAlternatingGroups(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        n = len(colors)
        lengths = [0] * (n + 1)
        sl = SortedList() # holds starts of runs
        for i in range(n):
            if colors[(i - 1) % n] == colors[i]:
                sl.add(i)
        for i in range(len(sl)):
            start = sl[i]
            nextStart = sl[(i + 1) % len(sl)]
            length = (nextStart - start - 1) % n + 1
            lengths[length] += 1

        st = Seg(lengths)

        res = []

        for query in queries:
            if len(query) == 2:
                _, size = query
                if not sl:
                    res.append(n)
                    continue
                node = st.rangeQuery(size, n)
                surplus = node.tot - (node.cnt * size)
                answer = node.cnt + surplus
                res.append(answer)

            else:
                _, index, color = query
                if colors[index] == color:
                    continue

                colors[index] = color

                for position in (index, (index + 1) % n):
                    if position not in sl:
                        if not sl:
                            st.pointAdd(n, 1)
                            sl.add(position)
                            continue

                        # find biggest number < position, "start"
                        pos = sl.bisect_right(position)
                        start = sl[pos - 1]
                        nextStart = sl[pos % len(sl)]

                        width = (nextStart - start - 1) % n + 1
                        leftWidth = (position - start - 1) % n + 1
                        rightWidth = width - leftWidth

                        st.pointAdd(width, -1)
                        st.pointAdd(leftWidth, 1)
                        st.pointAdd(rightWidth, 1)

                        sl.add(position)

                    else:
                        sl.remove(position)
                        if not sl:
                            st.pointAdd(n, -1)
                        else:
                            pos = sl.bisect_right(position)
                            start = sl[pos - 1]
                            nextStart = sl[pos % len(sl)]

                            leftWidth = (position - start - 1) % n + 1
                            rightWidth = (nextStart - position - 1) % n + 1

                            st.pointAdd(leftWidth, -1)
                            st.pointAdd(rightWidth, -1)
                            st.pointAdd(leftWidth + rightWidth, 1)

        return res