# Matching Engine

This project is an exercise to build a simple matching engine that deals one security and receives order by user input at the terminal.

---

## Sendind Orders and Seeing Trades

The engine expects inputs in the following format:

```
limit <side> <price> <qty>
```

or

```
market <side> <qty>
```

(Market orders don't have a specified price, so they trade at the best offer available)

And, for simplicity, it is considered that the input is always in the correct format. As if the engine received the order from a button pressed and not an actual string typed by a person who could make a mistake. Yes, this is a point where the project could improve.

The outputs, however, are only two:

```
Trade, price: <price>, qty: <qty>
```

if a match was found, and

```
Booking failed: no orders to match
```

if a market order could not trade (limit orders that don't trade will always be stored in the order book).

---

## The matching algorithm

### Data structures

The `OrderBook` is a structure that points to two binary search trees, each representing one side of the book (`BookSide`). The nodes of the binary search trees are called Price `Level`s, which are, in fact, queues implemented using a doubly linked list.

---

### Performance

The binary search tree data structure was chosen so that the average time complexity for the search of *any* price level would be _O(n)_, in particular, findind the best bid (the highest buy price) and the best ask (the lowest sell price) for any market order will also be, on average, _O(n)_.
The queue, however, was chosen to garantuee that the orders would be matched following a FIFO policy and, also, that insertion and remotion would be _O(1)_.

---

### Exception to the FIFO policy

The algorithm will only match limit orders that represent "good offers" to each other. That is, if a limit order to buy _n_ shares at price _x_ arrives, "good offer" is an order to sell _m_ shares at price _y_ with _x >= y_. The opposite is also true: arriving a sell _n_ shares at price _x_, then a good offer is a buy _m_ shares at price _y_ with _x <= y_ (the conditions over _m_ and _n_ will appear).

It should be noted, however, that the cases in which _x == y_, the order can be matched in place, which means that their prices will stay the same, only the quantities will change.

If that is not the case, however, the amount of shares and the total volume (quantity times price) of the offers can make the trade impossible. In fact, it is only possible to trade if both of them are different (_m != n_ and _ym != xn_), so that the one with less volume can be updated to a better price and lower quantity (with both equal, there's no room for change).

To make this simulated market more liquid, the algorithm will not stop at the head of the queue if the volume and quantity conditions are not met. This is not an actual exception to the FIFO policy *per se*, it is more of a secondary step to match orders, in which total volume has the advantage.

Important considerations:

* The order to be changed (the one with higher volume) can be the already booked one. In this case, since its price will change, this order must be reallocated to a proper level. To respect the FIFO in the new price level, the order is inserted considering its timestamp relative to the other ones already in queue. Unfortunately, this insertion is _O(n)_ (with _n_ being the numbers of orders in queue).

* The condition over the prices for an offer to be good is so that the order changed (wether it is a buy or sell) will always be closer to the best offer, which will increase the chance of a match.
  * if the order changed is a buy, its price will increase, making it closer to being the best bid
  * if the order changes is a sell, its price will decrease, making it closer to being the best ask

---

## Why Python?

Since this exercise was done in about a week, I prioritized development speed over execution speed. As I am more familiar with Python than Java and C++, I was able to code faster. But it should not be difficult to translate the program to another language, specially considering that no outside package was used.
