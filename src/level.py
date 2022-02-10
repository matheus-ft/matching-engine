from quote import Order


class Level:  # queue capsule and bst node
    """
    Class to represent a price level in the OrderBook.

    Attributes
    ----------
    price : float
        Price of all the limit orders stored in queue
    is_bid : bool
        Indicates if the level contains buy (`True`) or sell (`False`) orders
    total_qty : int
        Total amount of shares to be traded in the level
    head : Order
        Points to the first order in queue
    tail : Order
        Points to the last order in queue
    right : Level
        Points to a right-son level in the BST (BookSide)
    left : Level
        Points to a left-son level in the BST (BookSide)
    parent : Level
        Points to its parent level in the BST (BookSide)

    Methods
    -------
    enqueue_order(limit_order: Order) -> None:
        adds a new limit order in the end of the queue

    dequeue_order() -> Order:
        removes and returns the limit order in the front of the queue

    insert_order(limit_order: Order) -> None:
        inserts a limit order considering its timestamp
        relative to the ones already in queue

    remove_order(limit_order: Order) -> None:
        removes a specific limit order inside the queue
        identifying it by its timestamp
    """
    def __init__(self, limit_order: Order) -> None:
        """Constructs a new price level based on a limit order

        Args:
            limit_order (Order)
        """
        # Level data #
        self.price: float = limit_order.price
        self.is_bid: bool = limit_order.is_buy
        self.total_qty: int = limit_order.qty
        # References to the first and last nodes in the Queue #
        self.head: Order = limit_order
        self.tail: Order = limit_order
        # Binary Search Tree node fields #
        self.right: Level = None
        self.left: Level = None
        self.parent: Level = None

    def enqueue_order(self, limit_order: Order) -> None:
        """Adds a new limit order in the end of the queue

        Args:
            limit_order (Order): limit order to be added
        """
        self.total_qty += limit_order.qty
        if self.head is None:
            self.head = limit_order
        else:
            self.tail.next = limit_order
        limit_order.prev = self.tail
        self.tail = limit_order

    def dequeue_order(self) -> Order:
        """Removes the limit order in the front of the queue

        Returns:
            Order: the first limit order in queue
        """
        order = self.head
        if order is not None:
            self.head = order.next
            if self.head is not None:
                self.head.prev = None
        self.total_qty -= order.qty
        if order == self.tail:
            self.tail = None
        return order

    def insert_order(self, limit_order: Order) -> None:
        """Inserts a limit order considering its timestamp
        relative to the ones already in queue

        Args:
            limit_order (Order): limit order to be added
        """
        if limit_order.timestamp >= self.tail.timestamp:
            self.enqueue_order(limit_order)
            return
        self.total_qty += limit_order.qty
        pointer: Order = self.head
        aux: Order = None
        while (pointer.timestamp >= limit_order.timestamp):
            aux = pointer
            pointer = pointer.next
        aux.next = limit_order
        pointer.prev = limit_order
        limit_order.next = pointer
        limit_order.prev = aux

    def remove_order(self, limit_order: Order) -> None:
        """Removes a specific limit order inside the queue
        identifying it by its timestamp

        Args:
            limit_order (Order): limit order to be removed
        """
        if limit_order == self.head:
            self.dequeue_order()
            return
        self.total_qty -= limit_order.qty
        pointer: Order = self.head
        aux: Order = None
        while (pointer != limit_order):
            aux = pointer
            pointer = pointer.next
        aux.next = limit_order.next
        if limit_order.next is not None:
            limit_order.next.prev = aux
