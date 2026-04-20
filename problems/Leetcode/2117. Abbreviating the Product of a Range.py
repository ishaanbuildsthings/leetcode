class Solution:
    def abbreviateProduct(self, left: int, right: int) -> str:
        twos = 0
        fives = 0
        for num in range(left, right + 1):
            while num % 2 == 0:
                num //= 2
                twos += 1
            while num % 5 == 0:
                num //= 5
                fives += 1
        trailingZeroes = min(twos, fives)

        lastDigits = 1
        for num in range(left, right + 1):
            lastDigits *= num
            while lastDigits % 10 == 0:
                lastDigits //= 10
            lastDigits %= 10**10 # # just keep last 10 digits
        lastDigits = str(lastDigits)[-5:]
        if len(lastDigits) < 5: # e.g. if we end in 8192, we actually end in 08192, assuming we have >10 digits total
            lastDigits = '0' * (5 - len(lastDigits)) + lastDigits
        print(f'{lastDigits=}')

        # any positive number P can be written in scientific notation P = m * 10^k
        # m is the mantissa and satisfies 1 <= m < 10
        # EXAMPLE:
        # P = 7,219,856,259,000
        # P = 7.219856259 * 10^12
        # m = 7.219856259, k=12

        # the leading digits of P come from P

        # take log_10 of both sides

        # log_10(P) = log_10(m * 10^k)
        # log_10(P) = log_10(m) + log_10(10^k)
        # log_10(P) = log_10(m) + k
        # since 1 <= M < 10, we know log_10(m) is in the range [0, 1)
        # and K is an integer

        # log_10(P) will then be some integer portion + fractional portion, remember log_10(P) is kind of like the # of digits of P
        # log_10(m) will be the fractional portion, and K will be the integer

        # we want to solve for M
        # log_10(m) = fractional part
        # m = 10^(fractional part)
        
        # now we compute log_10(P)
        
        mantissa = 1
        for num in range(left, right + 1):
            mantissa *= num
            while mantissa >= 10**18:
                mantissa //= 10

        firstFive = str(mantissa)[:5]

        # if the total # of digits after removing trailing zeroes is < 10, we fully combine the two parts, otherwise they overlap and we must cut some off
        # note we can't strip the digits as we go and check if we ever are >= 10^10, because we could temporarily overflow then strip back down, so I take out the 2s and 5s first
        prodWithoutTrailingZeroes = 1
        is11OrMore = False
        for num in range(left, right + 1):
            while num % 2 == 0:
                num //= 2
            while num % 5 == 0:
                num //= 5
            prodWithoutTrailingZeroes *= num
            if prodWithoutTrailingZeroes >= 10**10:
                is11OrMore = True
                break
        
        twosToAdd = twos - trailingZeroes
        fivesToAdd = fives - trailingZeroes
        for _ in range(twosToAdd):
            prodWithoutTrailingZeroes *= 2
            if prodWithoutTrailingZeroes >= 10**10:
                is11OrMore = True
                break
        for _ in range(fivesToAdd):
            prodWithoutTrailingZeroes *= 5
            if prodWithoutTrailingZeroes >= 10**10:
                is11OrMore = True
                break

        # if we are <= 10 digits, just compute it manually
        if not is11OrMore:
            prodWithoutTrailingZeroes = 1
            for num in range(left, right + 1):
                prodWithoutTrailingZeroes *= num
                while prodWithoutTrailingZeroes % 10 == 0:
                    prodWithoutTrailingZeroes //= 10
            return str(prodWithoutTrailingZeroes) + 'e' + str(trailingZeroes)
        
        # firstFive = ''.join([x for x in str(m) if x != '.'][:5])
        return firstFive + '...' + lastDigits + 'e' + str(trailingZeroes)







