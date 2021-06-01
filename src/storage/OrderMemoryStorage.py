from src.logger import logger


class OrderStorage:
    orders = list()
    history = list()
    total_profit = 0

    @staticmethod
    def get_history():
        return OrderStorage.history

    @staticmethod
    def store_order(order):
        OrderStorage.orders.append(order)

        log = ''
        if order['date']:
            log += str(order['date']) + ' | '

        log += 'New ' + order['direction'].lower() + ' order – amount: ' \
               + str(order['amount']) + ', price: ' + str(order['price'])

        if order['direction'].lower() == 'sell':
            last_buy_order = OrderStorage.get_last_buy_order()[0]
            profit = round((order['amount'] * order['price']) - (last_buy_order['amount'] * last_buy_order['price']), 3)

            OrderStorage.total_profit += profit

            log += ', profit: ' + str(profit)
            log += ', total profit: ' + str(round(OrderStorage.total_profit, 3))

        logger.info(log)

        return order

    @staticmethod
    def get_last_buy_order():
        return [el for el in OrderStorage.orders if el['direction'].lower() == 'buy']

    @staticmethod
    def move_orders_to_history():
        for el in OrderStorage.orders:
            OrderStorage.history.append(el)

        OrderStorage.orders.clear()


shared_order_storage = OrderStorage
