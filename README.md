# btcmarkets-python
This library is an unofficial python wrapper for BTC Markets API V3.

The official BTC Markets resources are below: \
https://api.btcmarkets.net/doc/v3 \
https://github.com/BTCMarkets/API 

### Example
```python

import btcmarkets

# Example

api_key = "<add-your-own>"
api_secret = "<add-your-own>"

client = btcmarkets.Client(api_key, api_secret)

print(client.list_orders(status="open"))
order = client.place_new_order("BTC-AUD", "100.12", "0.0024", "Limit", "Bid")
print(order)
print(client.cancel_an_order(order["orderId"]))
print(client.list_orders(status="open"))
```
