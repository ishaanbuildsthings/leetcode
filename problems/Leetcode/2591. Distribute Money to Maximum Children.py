class Solution:
    def distMoney(self, money: int, children: int) -> int:
        if money < children:
            return -1
        money -= children

        # if every child can have at least 8
        if money >= children * 7:
            if money == children * 7:
                return children
            return children - 1
        
        # we can fill 8s for everyone except one child
        eights = money // 7
        if not eights:
            return 0

        money -= 7 * eights

        if eights == children - 1 and money == 3:
            return eights - 1
        
        return eights