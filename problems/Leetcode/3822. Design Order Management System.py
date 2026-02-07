class OrderManagementSystem:

    def __init__(self):
        self.typeAndPriceToIds = defaultdict(list) # maps (type, price) -> list of ids
        self.orderToPrice = {}
        self.orderToType = {}
        self.orderToI = {} # position in the typeAndPriceToIds map

    def addOrder(self, orderId: int, orderType: str, price: int) -> None:
        self.typeAndPriceToIds[(orderType, price)].append(orderId)
        self.orderToPrice[orderId] = price
        self.orderToType[orderId] = orderType
        self.orderToI[orderId] = len(self.typeAndPriceToIds[(orderType, price)]) - 1

    def modifyOrder(self, orderId: int, newPrice: int) -> None:
        oldPrice = self.orderToPrice[orderId]
        oldI = self.orderToI[orderId]
        oldType = self.orderToType[orderId]

        self.orderToPrice[orderId] = newPrice
        bucket = self.typeAndPriceToIds[(oldType, oldPrice)]
        lastId = bucket[-1]
        bucket[oldI] = lastId
        self.orderToI[lastId] = oldI
        bucket.pop()
        self.typeAndPriceToIds[(oldType, newPrice)].append(orderId)
        self.orderToI[orderId] = len(self.typeAndPriceToIds[(oldType, newPrice)]) - 1

    def cancelOrder(self, orderId: int) -> None:
        oldPrice = self.orderToPrice[orderId]
        oldI = self.orderToI[orderId]
        oldType = self.orderToType[orderId]
        del self.orderToPrice[orderId]
        del self.orderToI[orderId]
        del self.orderToType[orderId]

        bucket = self.typeAndPriceToIds[(oldType, oldPrice)]
        lastId = bucket[-1]
        bucket[oldI] = lastId
        self.orderToI[lastId] = oldI
        bucket.pop()
        
    def getOrdersAtPrice(self, orderType: str, price: int) -> List[int]:
        return self.typeAndPriceToIds[(orderType, price)]
        


# Your OrderManagementSystem object will be instantiated and called as such:
# obj = OrderManagementSystem()
# obj.addOrder(orderId,orderType,price)
# obj.modifyOrder(orderId,newPrice)
# obj.cancelOrder(orderId)
# param_4 = obj.getOrdersAtPrice(orderType,price)