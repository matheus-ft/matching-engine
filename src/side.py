from quote import Order
from level import Level


class BookSide:  # bst
    """Class to represent one side of an Order Book

    Attributes
    ----------
    root : Level
        Points to the first level stored in the binary search tree
    is_bid : bool
        Indicates if the side contains bid (`True`) or ask (`False`) prices
    total_qty : int
        Total amount of shares to be traded in this side of the book

    Methods
    -------
    register_order(limit_order: Order, timestamp: bool = False) -> None:
        Properly registers a limit order in the order book.

    min_level(start: Level = None) -> Level:
        Finds the level with the lowest price.

    max_level(start: Level = None) -> Level:
        Finds the level with the highest price.

    next_level(level: Level) -> Level:
        Finds the successor of a given price level.

    replace_level(old: Level, new: Level) -> None:
        Replaces a given level by another one inside the BST.

    remove_level(level: Level) -> None:
        Removes a given level of the BookSide
        by replacing it with its successor
    """
    def __init__(self, is_bid: bool) -> None:
        """Constructs a side of an order book

        Args:
            is_bid (bool)
        """
        self.root: Level = None
        self.is_bid: bool = is_bid
        self.total_qty: int = 0

    def register_order(self, limit_order: Order, timestamp: bool = False):
        """Properly registers a limit order in the order book.
        If there's no existing Level for the order, one is created.
        If `timestamp` is not given, the order is enqueued in its Level,
        otherwise, the order will be inserted respecting its timestamp.

        Args:
            limit_order (Order): limit order to be registered
            timestamp (bool, optional): indicates whether the order should be
            added at the end or in the middle of a queue. Defaults to False.
        """
        self.total_qty += limit_order.qty
        if self.root is None:
            self.root = Level(limit_order)
            return
        pointer: Level = self.root
        aux: Level = None
        while pointer is not None:
            aux = pointer
            if (pointer.price > limit_order.price):
                pointer = pointer.left
            elif (pointer.price < limit_order.price):
                pointer = pointer.right
            else:
                break
        if aux.price == limit_order.price:
            if timestamp:
                aux.insert_order(limit_order)
            else:
                aux.enqueue_order(limit_order)
            return
        elif aux.price > limit_order.price:
            aux.left = Level(limit_order)
            level = aux.left
        else:
            aux.right = Level(limit_order)
            level = aux.right
        level.parent = aux

    def min_level(self, start: Level = None) -> Level:
        """Finds the level with the lowest price.

        Args:
            start (Level, optional): specifies the starting level
            of the search. Defaults to None.

        Returns:
            Level: the price level wanted
        """
        level = start if (start is not None) else self.root
        if level is None:
            return None
        while (level.left is not None):
            level = level.left
        return level

    def max_level(self, start: Level = None) -> Level:
        """Finds the level with the highest price.

        Args:
            start (Level, optional): specifies the starting level
            of the search. Defaults to None.

        Returns:
            Level: the price level wanted
        """
        level = start if (start is not None) else self.root
        if level is None:
            return None
        while (level.right is not None):
            level = level.right
        return level

    def next_level(self, level: Level) -> Level:
        """Finds the successor of a given price level.

        "Successor" being the price level with the lowest price
        thats is greater than `level.price`

        Args:
            level (Level): price level whose successor is wanted

        Returns:
            Level: the successor
        """
        if level is None:
            return None
        if level.right is not None:
            return self.min_level(level.right)
        next = level.parent
        aux = level
        while (next is not None) and (aux == next.right):
            aux = next
            next = next.parent
        return next

    def replace_level(self, old: Level, new: Level) -> None:
        """Replaces a given level by another one inside the BST

        Args:
            old (Level): price level to be replaced
            new (Level): replacing level
        """
        if old is not None:
            if (old.parent is None):
                self.root = new
            elif (old == old.parent.left):
                old.parent.left = new
            else:
                old.parent.right = new

            if new is not None:
                new.parent = old.parent

    def remove_level(self, level: Level) -> None:
        """Removes a given level of the BookSide
        by replacing it with its successor

        Args:
            level (Level): price level to be removed
        """
        if (level.left is None):
            self.replace_level(level, level.right)
        elif (level.right is None):
            self.replace_level(level, level.left)
        else:
            next_level = self.next_level(level)
            if next_level.parent != level:
                self.replace_level(next_level, next_level.right)
                next_level.right = level.right
                next_level.right.parent = next_level
            self.replace_level(level, next_level)
            next_level.left = level.left
            next_level.left.parent = next_level
