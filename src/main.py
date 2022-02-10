from quote import Order
from book import OrderBook


def start_trading() -> None:
    """
    Runs the matching engine designed in `OrderBook` -
    receiving orders by inputs at the terminal -
    and stops running once the quote string is 'stop'
    """
    book = OrderBook()
    quote: str = input()
    while quote != "stop":
        book.add_order(Order(quote))
        quote = input()


if __name__ == "__main__":
    start_trading()
