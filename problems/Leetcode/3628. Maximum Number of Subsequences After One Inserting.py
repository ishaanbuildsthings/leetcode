class Solution:
    def numOfSubsequences(self, s: str) -> int:
        # s = 'LTCT'
        pl = {}
        plc = {}
        plct = {}
        st = {}
        sct = {}
        slct = {}

        l = 0
        lc = 0
        lct = 0
        for i, c in enumerate(s):
            if c not in 'LCT':
                pl[i] = l
                plc[i] = lc
                plct[i] = lct
                continue
            if c == "L":
                l += 1
            elif c == 'C':
                lc += l
            elif c == 'T':
                lct += lc
            pl[i] = l
            plc[i] = lc
            plct[i] = lct


        t = ct = lct = 0
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c not in 'LCT':
                st[i] = t
                sct[i] = ct
                slct[i] = lct
                continue
            if c == 'T':
                t += 1
            if c == 'C':
                ct += t
            if c == 'L':
                lct += ct
            st[i] = t
            sct[i] = ct
            slct[i] = lct

        res = plct[len(s) - 1]

        # on the left of our insertion
        for i in range(1, len(s)):
            all = plct[len(s) - 1] # ALL LCT
            l = pl.get(i-1,0)
            lc = plc.get(i-1,0)
            t = st.get(i,0)
            ct = sct.get(i,0)
            res = max(res, all + max(lc, ct, l * t))
        # or we can get all post + ct
        allPost = slct[0]
        ct = sct[0]
        res = max(res, allPost + ct)

        # or we can get all pre + all lc
        allPre = plct[len(s) - 1]
        lc = plc[len(s) - 1]
        res = max(res, allPre + lc)

        return res
            
            

        