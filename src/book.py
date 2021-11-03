from quote import Order
from level import Level
from side import BookSide


class OrderBook:
    """Class to represent an Order Book

    Attributes
    ----------
    bid : BookSide
        Side of the order book containing bid price levels
    ask : Bookside
        Side of the order book containing ask price levels

    Methods
    -------
    add_order(order: Order) -> None:
        Adds an order to the order book.

    process_limit_order(order: Order) -> None:
        Adds a limit order to the book.

    process_market_order(order: Order) -> None:
        Finds and executes available trades.

    trade_limit_order(limit_order: Order, level: Level) -> Order:
        Finds a proper counterparty and, if one exists,
        executes the trade and updates the orders.

    trade_at_level(market_order: Order, level: Level) -> Order:
        Matches as many booked orders in the level as possible
        with the given market order.

    print_match(price: float, qty: int) -> None:
        Displays the results of a successful match.

    reallocate_order(order: Order, origin_level: Level) -> None:
        Reinserts a modified order in the order book.
    """
    def __init__(self) -> None:
        """ Constructs a new Order Book """
        self.bid = BookSide(True)
        self.ask = BookSide(False)

    def add_order(self, order: Order) -> None:
        """Adds an order to the order book.

        Args:
            order (Order): order to be booked
        """
        if order.is_limit:
            self.process_limit_order(order)
        else:
            self.process_market_order(order)

    def process_limit_order(self, order: Order) -> None:
        """Adds a limit order to the book.

        Args:
            order (Order): limit order being processed

        This method will only trade the limit order if there's a "good offer",
        that is, if the order is a buy at price `x` and there is a sell at `y`,
        with `x >= y`, then it is advantageous for both parties to trade,
        and the one with more shares to trade just need to change
        its price to meet its goal volume. The opposite case is analogous,
        a sell order at `x` meeting a buy at `y`, with `x <= y`, will
        trigger a trade. However, if there aren't any good offers,
        the order will be simply booked.
        """
        counterparty_side: BookSide = self.ask if order.is_buy else self.bid
        order_side: BookSide = self.bid if order.is_buy else self.ask
        if counterparty_side.total_qty == 0:
            order_side.register_order(order)
            return
        if order.is_buy:
            counterparty_level = self.ask.min_level()
        else:
            counterparty_level = self.bid.max_level()
        while order.qty > 0:
            if counterparty_level is None:
                order_side.register_order(order)
                return
            elif order.is_buy and (order.price < counterparty_level.price):
                order_side.register_order(order)
                return
            elif (
                not order.is_buy
                and
                (order.price > counterparty_level.price)
            ):
                order_side.register_order(order)
                return
            order = self.trade_limit_order(order, counterparty_level)
            counterparty_level = counterparty_side.next_level(
                counterparty_level
            )

    def process_market_order(self, order: Order) -> None:
        """Finds and executes available trades.

        If there aren't any counterparties, it discards the order.

        Args:
            order (Order): market order being processed
        """
        counterparty_side: BookSide = self.ask if order.is_buy else self.bid
        if order.is_buy:
            counterparty_level = self.ask.min_level()
        else:
            counterparty_level = self.bid.max_level()
        if counterparty_level is not None:
            while order.qty > 0:
                order = self.trade_at_level(order, counterparty_level)
                counterparty_level = counterparty_side.next_level(
                    counterparty_level
                )
                if counterparty_level is None:
                    break
        else:
            print("Booking failed: no orders to match")

    def trade_limit_order(self, limit_order: Order, level: Level) -> Order:
        """Finds a proper counterparty and, if one exists,
        executes the trade and updates the orders.

        Args:
            limit_order (Order): order to be traded
            level (Level): price level at which is intended to trade

        Returns:
            Order: `limit_order` after trading

        This method is only called if the bid (buy price) is higher than
        the ask (sell price).

        If the price of the order has a counterparty level, then
        the limit order can be treated as a market order.

        But if that's not the case, then it is only possible to trade
        at different prices if both the total volume and the quantity
        of the orders are different.

        In any case, the only order updated is the one with more shares -
        if a buy, the price increases, if a sell, it decreases
        (this way it is closer to the best offer); also the quantity is
        reduced by the amount of the counterparty - and the other is discarded.
        """
        if limit_order.price == level.price:
            return self.trade_at_level(limit_order, level)
        counterparty: Order = level.head
        while (
            (counterparty.total() == limit_order.total())
            or
            (counterparty.qty == limit_order.qty)
        ):
            counterparty = counterparty.next
            if counterparty is None:
                return limit_order

        new_qty = abs(counterparty.qty - limit_order.qty)
        new_total = abs(counterparty.total() - limit_order.total())
        if counterparty.total() > limit_order.total():
            counterparty.price = new_total / new_qty
            counterparty.qty = counterparty.qty - limit_order.qty
            self.reallocate_order(counterparty, level)
            self.print_match(limit_order.price, limit_order.qty)
            limit_order.qty = 0
        else:
            limit_order.price = new_total / new_qty
            limit_order.qty = new_qty
            self.print_match(counterparty.price, counterparty.qty)
            counterparty_side = self.bid if counterparty.is_buy else self.ask
            counterparty_side.total_qty -= limit_order.qty
            level.remove_order(counterparty)
            if level.head is None:
                counterparty_side.remove_level(level)
        return limit_order

    def trade_at_level(self, market_order: Order, level: Level) -> Order:
        """Matches as many booked orders in the level as possible
        with the given market order.

        Args:
            market_order (Order): order searching for matches
            level (Level): best price level available

        Returns:
            Order: `market_order` after trading at this level
        """
        qty_traded = 0
        counterparty: Order = level.head
        while (counterparty is not None) and (market_order.qty > 0):
            if counterparty.qty <= market_order.qty:
                level.dequeue_order()
                qty_traded += counterparty.qty
                market_order.qty -= counterparty.qty
            else:
                counterparty.qty -= market_order.qty
                level.total_qty -= market_order.qty
                qty_traded += market_order.qty
                market_order.qty = 0
            counterparty = counterparty.next
        if level.is_bid:
            self.bid.total_qty -= qty_traded
            if level.total_qty == 0:
                self.bid.remove_level(level)
        else:
            self.ask.total_qty -= qty_traded
            if level.total_qty == 0:
                self.ask.remove_level(level)
        self.print_match(level.price, qty_traded)
        return market_order

    def print_match(self, price: float, qty: int) -> None:
        """Displays the results of a successful match.

        Args:
            price (float): price at which the trade was executed
            qty (int): amount of shares traded
        """
        print(f"Trade, price: {price}, qty: {qty}")

    def reallocate_order(self, order: Order, origin_level: Level) -> None:
        """Reinserts a modified order in the order book.

        Args:
            order (Order): limit order modified through trading
            origin_level (Level): original price level of the order
        """
        origin_level.remove_order(order)
        if order.is_buy:
            self.bid.register_order(order, True)
        else:
            self.ask.register_order(order, True)
