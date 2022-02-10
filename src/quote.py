from datetime import datetime


class Quote:
    """Helper class to process a quote string

    Attributes
    ----------
    is_limit : bool
        Indicates the type of the order: limit (`True`) or market (`False`)
    is_buy : bool
        Indicates if the order is buy (`True`) or sell (`False`)
    price : float
        If the order is of type limit, it stores the price set,
        otherwise, `None`
    qty : int
        Ammunt of shares to be traded
    timestamp : datetime
        Timestamp of the instant the order was given,
        so that it can be uniquely identified
    """

    def __init__(self, quote: str) -> None:
        """Constructs a quote from a expected string sintax

        Args:
            quote (str)
        """
        quote_items = quote.lower().split()
        self.is_limit = True if (quote_items[0] == "limit") else False
        self.is_buy = True if (quote_items[1] == "buy") else False
        self.price = float(quote_items[2]) if self.is_limit else None
        self.qty = int(quote_items[-1])
        self.timestamp = datetime.now()


class Order(Quote):  # doubly linked list node
    """Class to represent an order

    The data is the same of a Quote,
    with the addition of the references to other orders

    Attributes
    ----------
    next : Order
        Points to the next order in queue
    prev : Order
        Points to the previous order in queue

    Methods
    -------
    total -> float:
        Returns the total volume (`.qty * .price`) of the order -
        if it is of limit type, otherwise, `None`

    Inherited Attributes
    ----------
    is_limit : bool
        Indicates the type of the order: limit (`True`) or market (`False`)
    is_buy : bool
        Indicates if the order is buy (`True`) or sell (`False`)
    price : float
        If the order is of type limit, it stores the price set,
        otherwise, `None`
    qty : int
        Ammunt of shares to be traded
    timestamp : datetime
        Timestamp of the instant the order was given,
        so that it can be uniquely identified
    """

    def __init__(self, quote: str) -> None:
        """Constructs a new order based on a given quote

        Args:
            quote (str): string describing the order
        """
        super().__init__(quote)
        self.next: Order = None
        self.prev: Order = None

    def total(self) -> float:
        """Gives the volume of the order

        Returns:
            float: qty * price
            None: if it is a market order
        """
        if self.is_limit:
            return self.qty * self.price
        else:
            return None
