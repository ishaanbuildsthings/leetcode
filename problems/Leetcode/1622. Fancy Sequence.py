calls = 0
class Fancy:
    def __init__(self):
        global calls
        calls += 1
        if calls < 100:
            self.N = 10**4
        else:
            self.N = int((10**5) // 2.3)
        self.tree = [0] * 4 * self.N
        self.lazyAdd = [0] * 4 * self.N
        self.lazyMult = [1] * 4 * self.N # 1 is our baseline value
        self._buildRecurse(1, 0, self.N - 1)
        self.nextIdx = 0
    
    def _buildRecurse(self, i, tl, tr):
        self.tree[i] = 0
        if tl == tr:
            return
        
        tm = (tr + tl) // 2 
        self._buildRecurse(2*i, tl, tm)
        self._buildRecurse(2*i + 1, tm + 1, tr)
        
    # takes a nodes old lazys and new lazys and updates its lazys, remember there may be multiple old pending lazies
    def _composeLazies(self, i, oldLazyAdd, oldLazyMult, newLazyAdd, newLazyMult):
      self.lazyAdd[i] *= newLazyMult
      self.lazyMult[i] *= newLazyMult
      self.lazyAdd[i] += newLazyAdd
        

    def _queryIndex(self, i, tl, tr, index):
        # as we descend down we apply and push our lazies and zero out
        self._pushLazy(i, tl, tr)

        if tl == tr:
          return self.tree[i]
        
        tm = (tr + tl) // 2
        if index <= tm:
            return self._queryIndex(2*i, tl, tm, index)
        return self._queryIndex(2*i + 1, tm + 1, tr, index)

    def append(self, val: int):
        self._modifyRange(1, 0, self.N - 1, self.nextIdx, self.nextIdx, val, 1)
        self.nextIdx += 1

    # zeroes out a pending update and pushes it down
    def _pushLazy(self, i, tl, tr):
        # speed optimization, since we only care about ST nodes of length 1, I don't solve for the non-leaf ST nodes
        if tl == tr:
          # first, multiply the base
          self.tree[i] *= self.lazyMult[i]
          # then add
          self.tree[i] += self.lazyAdd[i]

          # maybe reduce too large numbers for a speedup
          self.tree[i] %= (10**9 + 7)

        # compose updates below us
        if tl != tr:
            self._composeLazies(2*i, self.lazyAdd[2*i], self.lazyMult[2*i], self.lazyAdd[i], self.lazyMult[i])
            self._composeLazies(2*i + 1, self.lazyAdd[2*i + 1], self.lazyMult[2*i + 1], self.lazyAdd[i], self.lazyMult[i])
        
        # zero out
        self.lazyAdd[i] = 0
        self.lazyMult[i] = 1 # identity / "zeroed" value

    def _modifyRange(self, i, tl, tr, l, r, newAdd, newMult):
            
      # if we have no intersection, we stop, we could push lazies if needed
      if tl > r or tr < l:
          return
      
      # as we descend, we zero out our lazy (if no lazy, push does nothing)
      self._pushLazy(i, tl, tr)
        
      # if we are fully contained, our range assignment applies to this segment, so we compose
      if tl >= l and tr <= r:
        self._composeLazies(i, self.lazyAdd[i], self.lazyMult[i], newAdd, newMult)
        return

      # recurse on children
      tm = (tr + tl) // 2
      self._modifyRange(2*i, tl, tm, l, r, newAdd, newMult)
      self._modifyRange(2*i + 1, tm + 1, tr, l, r, newAdd, newMult)
        

    def addAll(self, inc: int):
        self._modifyRange(1, 0, self.N - 1, 0, self.nextIdx - 1, inc, 1)
        

    def multAll(self, m: int):
        self._modifyRange(1, 0, self.N - 1, 0, self.nextIdx - 1, 0, m)

    def getIndex(self, idx: int):
      if idx >= self.nextIdx:
        return -1
      return self._queryIndex(1, 0, self.N - 1, idx)